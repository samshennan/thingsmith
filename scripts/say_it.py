#!/usr/bin/env python3
"""Pronunciation screen for the thingsmith skill: readings + an automated radio test.

Two tests, both machine stand-ins for human tests in references/06-screening.md.
Neither replaces three native speakers resident in-country. Both are cheap
enough to run on every survivor of the form screen.

1. READINGS (the four-language test, automated)
   eSpeak NG applies each language's spelling-to-sound rules to the bare
   name, the way a native reader meets it cold on a sign. Each reading is
   printed as IPA, and the readings are compared. If two markets read the
   spelling very differently, the name is two brands wearing one spelling:
   DIVERGENT. That is a kill in the skill, not a deduction.

2. RADIO (say it once, can the listener spell it?)
   The name is spoken inside a carrier sentence ("The company is called X.")
   by a text-to-speech voice for each language, then transcribed by Whisper
   with NO hint of the spelling. If the transcript spells the name back, PASS.
   If it hears a different word, FAIL, and the heard spelling is printed,
   because that is the spelling customers will type into a search box.
   Synthetic voices are cleaner than a phone call and Whisper is better than a
   distracted listener, so a FAIL here is strong evidence and a PASS is weak.

Anything that could not run (no voice for a language, no eSpeak, no Whisper)
is UNSUPPORTED, printed as itself, and the process exits non-zero, so a partial
screen cannot be handed over as a complete one.

Backends, best first:
  TTS:  Windows SAPI voice for the language  ->  eSpeak NG voice  ->  UNSUPPORTED
  IPA:  eSpeak NG (`espeak-ng --ipa`)                              ->  UNSUPPORTED
  ASR:  faster-whisper (`pip install faster-whisper`; model downloads once)

Usage:
    python say_it.py --names karbia zyla --langs en pl de
    python say_it.py --names karbia --readings-only
    python say_it.py --names karbia --langs en pl --model small --json say.json
"""

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

CARRIERS = {
    "en": "The company is called {}.",
    "pl": "Firma nazywa się {}.",
    "de": "Die Firma heißt {}.",
    "fr": "L'entreprise s'appelle {}.",
    "es": "La empresa se llama {}.",
    "it": "L'azienda si chiama {}.",
    "nl": "Het bedrijf heet {}.",
    "pt": "A empresa chama-se {}.",
}
SAPI_CULTURE = {"en": "en-", "pl": "pl-PL", "de": "de-DE", "fr": "fr-FR",
                "es": "es-ES", "it": "it-IT", "nl": "nl-NL", "pt": "pt-"}
DIVERGENT_BELOW = 0.60   # pairwise IPA similarity; below this two markets say different words
ESPEAK_PATHS = [r"C:\Program Files\eSpeak NG\espeak-ng.exe",
                r"C:\Program Files (x86)\eSpeak NG\espeak-ng.exe"]


def find_espeak():
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if exe:
        return exe
    return next((p for p in ESPEAK_PATHS if os.path.exists(p)), None)


def fold(s):
    """Lowercase, strip diacritics and anything that is not a letter or digit."""
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if c.isalnum() and not unicodedata.combining(c))


# --- readings ---------------------------------------------------------------

def ipa(espeak, name, lang):
    r = subprocess.run([espeak, "-q", "--ipa", "-v", lang, name],
                       capture_output=True, text=True, encoding="utf-8", timeout=30)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


# Each language's eSpeak voice writes the same sound with its own allophones
# (English /əʊ/, Polish /ɔ/, German /oː/ are all "o" to a listener). Compare
# broad sound classes, not narrow IPA, or every pair of languages diverges.
# Diphthongs become single symbols first so "kai-" never matches "ki-".
DIPHTHONGS = [("aɪ", "Y"), ("aj", "Y"), ("eɪ", "E"), ("ej", "E"), ("əʊ", "o"),
              ("oʊ", "o"), ("aʊ", "W"), ("ɔɪ", "O"), ("ɔj", "O"), ("oj", "O")]
BROAD = str.maketrans({"ɐ": "a", "ɑ": "a", "æ": "a", "ʌ": "a", "ə": "a", "ɜ": "e",
                       "ɛ": "e", "ɪ": "i", "ɨ": "i", "ɔ": "o", "ɒ": "o", "ʊ": "u",
                       "ɹ": "r", "ɾ": "r", "ʁ": "r", "β": "v", "ɡ": "g", "ʃ": "S",
                       "ʂ": "S", "ɕ": "S", "ʒ": "Z", "ʐ": "Z", "ʑ": "Z", "ŋ": "n",
                       "ɲ": "n", "ɫ": "l", "θ": "t", "ð": "d", "ʲ": None, "ʰ": None})
VOWELS = set("aeiouyYEWO")


def ipa_core(s):
    # Stress, length and syllable marks change emphasis, not identity.
    s = "".join(c for c in s if c not in "ˈˌːˑ.‿ -_()" and not c.isspace())
    for a, b in DIPHTHONGS:
        s = s.replace(a, b)
    s = s.translate(BROAD)
    return re.sub(r"(.)\1+", r"\1", s)  # doubled letters are one sound


def first_vowel(core):
    return next((c for c in core if c in VOWELS), "")


def readings(espeak, name, langs):
    rows = {l: ipa(espeak, name, l) for l in langs}
    cores = {l: ipa_core(v) for l, v in rows.items() if v}
    worst = (1.0, None, None)
    ls = list(cores)
    for i, a in enumerate(ls):
        for b in ls[i + 1:]:
            r = difflib.SequenceMatcher(None, cores[a], cores[b]).ratio()
            # The first vowel carries the name's identity: "KAI-peto" and
            # "ki-PE-to" are different words whatever the rest scores.
            if first_vowel(cores[a]) != first_vowel(cores[b]):
                r = min(r, DIVERGENT_BELOW - 0.01)
            if r < worst[0]:
                worst = (r, a, b)
    return rows, worst


# --- text to speech ---------------------------------------------------------

def sapi_voice(lang):
    if os.name != "nt":
        return None
    ps = ("Add-Type -AssemblyName System.Speech;"
          "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
          "$s.GetInstalledVoices()|%{$_.VoiceInfo.Name+'|'+$_.VoiceInfo.Culture}")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return None
    for line in out.splitlines():
        if "|" in line:
            vname, culture = line.rsplit("|", 1)
            if culture.strip().startswith(SAPI_CULTURE.get(lang, lang + "-")):
                return vname.strip()
    return None


def speak_sapi(voice, text, wav):
    text = text.replace("'", "''")
    ps = ("Add-Type -AssemblyName System.Speech;"
          "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
          f"$s.SelectVoice('{voice}');$s.Rate=-1;"
          f"$s.SetOutputToWaveFile('{wav}');$s.Speak('{text}');$s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, timeout=60, check=True)


def speak_espeak(espeak, lang, text, wav):
    subprocess.run([espeak, "-v", lang, "-s", "150", "-w", wav, text],
                   capture_output=True, timeout=60, check=True)


# --- speech to text ---------------------------------------------------------

_MODEL = None


def transcribe(wav, lang, model_size):
    global _MODEL
    from faster_whisper import WhisperModel
    if _MODEL is None:
        _MODEL = WhisperModel(model_size, device="cpu", compute_type="int8")
    # No initial_prompt: giving Whisper the spelling would turn the test into
    # a dictation exercise.
    segs, _ = _MODEL.transcribe(wav, language=lang, beam_size=5, temperature=0.0,
                                vad_filter=False)
    return " ".join(s.text for s in segs).strip()


def heard_name(transcript, carrier):
    """The words after the carrier phrase, joined, as a customer would type them."""
    prefix_len = len(carrier.format("").split())
    words = transcript.replace(",", " ").split()
    tail = words[prefix_len:] if len(words) > prefix_len else words[-1:]
    return "".join(w.strip(".!?\"'«»„”") for w in tail)


def radio(name, lang, voices, espeak, model_size, tmp):
    carrier = CARRIERS[lang]
    wav = os.path.join(tmp, f"{fold(name)}-{lang}.wav")
    if voices.get(lang):
        backend = f"sapi:{voices[lang]}"
        speak_sapi(voices[lang], carrier.format(name), wav)
    elif espeak:
        backend = "espeak-ng"
        speak_espeak(espeak, lang, carrier.format(name), wav)
    else:
        return {"status": "UNSUPPORTED", "note": f"no TTS voice for {lang}"}
    text = transcribe(wav, lang, model_size)
    heard = heard_name(text, carrier)
    ok = fold(heard) == fold(name)
    return {"status": "PASS" if ok else "FAIL", "heard": heard,
            "transcript": text, "tts": backend}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--names", nargs="+", required=True)
    ap.add_argument("--langs", nargs="+", default=["en", "pl", "de", "fr", "es", "it"],
                    choices=sorted(CARRIERS))
    ap.add_argument("--model", default="small", help="faster-whisper model size")
    ap.add_argument("--readings-only", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()

    espeak = find_espeak()
    unresolved = 0
    out = {}

    voices = {}
    asr_ok = False
    if not a.readings_only:
        voices = {l: sapi_voice(l) for l in a.langs}
        try:
            import faster_whisper  # noqa: F401
            asr_ok = True
        except ImportError:
            pass

    with tempfile.TemporaryDirectory() as tmp:
        for name in a.names:
            res = {"readings": {}, "radio": {}}
            print(f"\n{name}")

            if espeak:
                rows, (score, la, lb) = readings(espeak, name, a.langs)
                for l in a.langs:
                    v = rows[l]
                    res["readings"][l] = v
                    if v is None:
                        unresolved += 1
                    print(f"  read  {l}  /{v}/" if v else f"  read  {l}  UNSUPPORTED")
                verdict = ("DIVERGENT" if la and score < DIVERGENT_BELOW else "converges")
                res["convergence"] = {"verdict": verdict, "worst_pair": [la, lb],
                                      "similarity": round(score, 2)}
                pair = f" (worst: {la} vs {lb}, {score:.2f})" if la else ""
                print(f"  readings {verdict}{pair}")
            else:
                unresolved += 1
                res["convergence"] = {"verdict": "UNSUPPORTED", "note": "eSpeak NG not installed"}
                print("  readings UNSUPPORTED  (install eSpeak NG)")

            if not a.readings_only:
                for l in a.langs:
                    if not asr_ok:
                        r = {"status": "UNSUPPORTED", "note": "pip install faster-whisper"}
                    else:
                        try:
                            r = radio(name, l, voices, espeak, a.model, tmp)
                        except Exception as e:
                            r = {"status": "UNSUPPORTED", "note": f"{type(e).__name__}: {e}"}
                    res["radio"][l] = r
                    if r["status"] == "UNSUPPORTED":
                        unresolved += 1
                        print(f"  radio {l}  UNSUPPORTED  ({r['note']})")
                    else:
                        print(f"  radio {l}  {r['status']:<4}  heard '{r['heard']}'  [{r['tts']}]")
            out[name] = res

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

    print("\nMachine screen only. Native-speaker check (3 per language, resident in-country)"
          "\nis still required before money is spent. See assets/native-speaker-check.md.")
    if unresolved:
        print(f"{unresolved} check(s) UNSUPPORTED -- this screen is not complete.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
