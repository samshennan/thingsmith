"""Offline regressions for observations, ambiguity and partial-result reporting."""
import contextlib
import base64
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


domains = load("check_domains")
handles = load("check_handles")
speech = load("say_it")
adapters = load("sync_adapters")
context = load("context_sheet")


class DomainTests(unittest.TestCase):
    def test_structured_negative_is_only_no_record(self):
        self.assertEqual(domains.read_rdap(404, b'{"errorCode":404}', "example.com")[0], domains.NO_RECORD)

    def test_bare_or_html_404_is_unresolved(self):
        for body in (b"", b"<html>not found</html>", b'[]', b'{"errorCode":429}'):
            with self.subTest(body=body):
                self.assertEqual(domains.read_rdap(404, body, "example.com")[0], domains.UNVERIFIED)

    def test_unrelated_404_cannot_clear_registration(self):
        body = b'{"objectClassName":"domain","ldhName":"example.com","errorCode":500,"remarks":["request 404"]}'
        self.assertEqual(domains.read_rdap(200, body, "example.com")[0], domains.UNVERIFIED)

    def test_matching_object_and_wrong_domain(self):
        body = b'{"objectClassName":"domain","ldhName":"EXAMPLE.COM"}'
        self.assertEqual(domains.read_rdap(200, body, "example.com")[0], domains.TAKEN)
        self.assertEqual(domains.read_rdap(200, body, "other.com")[0], domains.UNVERIFIED)

    def test_record_beats_disclaimer(self):
        body = "Domain Name: EXAMPLE.COM\nRegistrar: Example\nHelp: if not found contact support"
        self.assertEqual(domains.read_whois(body, "example.com")[0], domains.TAKEN)

    def test_generic_whois_negative_is_unresolved(self):
        for body in ("not found", "No match for another.com", "No Data Found", None):
            self.assertEqual(domains.read_whois(body, "example.com")[0], domains.UNVERIFIED)

    def test_query_specific_whois_negatives(self):
        for query, body in (("example.com", 'No match for "EXAMPLE.COM".'),
                            ("example.pl", "No information available about domain name example.pl in the Registry NASK database.")):
            self.assertEqual(domains.read_whois(body, query)[0], domains.NO_RECORD)

    def test_throttling_and_contradictory_whois(self):
        self.assertEqual(domains.read_whois('Rate limit exceeded\nNo match for "example.com".', "example.com")[0], domains.UNVERIFIED)
        self.assertEqual(domains.read_whois('Registrar: Example\nNo match for "example.com".', "example.com")[0], domains.UNVERIFIED)

    def test_dns_absence_alone_is_not_no_record(self):
        with patch.object(domains, "dns_has_ns", return_value=False):
            self.assertEqual(domains.check_one("example.com", "com", None, None)[0], domains.UNSUPPORTED)

    def test_probe_error_is_retained_in_partial_results(self):
        job = {"domain": "example.com", "tld": "com", "rdap": None, "whois": None}
        with patch.object(domains, "check_one", side_effect=ValueError("fixture")), contextlib.redirect_stdout(io.StringIO()):
            result = domains.run([job], 0, 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], domains.UNVERIFIED)
        self.assertIn("checked_at", result[0])

    def test_multilabel_suffix_resolves_root_registry(self):
        self.assertEqual(domains.resolve_rdap("com.au", {"au": "https://example.invalid"}), "https://example.invalid")


class HandleTests(unittest.TestCase):
    def test_telegram_hidden_holder_stays_unresolved(self):
        with patch.object(handles, "fetch", return_value=(200, "https://t.me/example", '<div class="tgme_page">Contact</div>')):
            self.assertEqual(handles.p_telegram("example")[0], handles.UNVERIFIED)

    def test_gitlab_hidden_group_stays_unresolved(self):
        with patch.object(handles, "fetch", side_effect=[(200, "users", "[]"), (404, "groups", "{}")]):
            self.assertEqual(handles.p_gitlab("example")[0], handles.UNVERIFIED)

    def test_gitlab_error_object_is_not_a_user(self):
        with patch.object(handles, "fetch", return_value=(200, "users", '{"error":"blocked"}')):
            self.assertEqual(handles.p_gitlab("example")[0], handles.UNVERIFIED)

    def test_youtube_consent_and_unknown_html(self):
        for url, body in (("https://consent.youtube.com", "consent"), ("https://youtube.com/@example", "<html>try again</html>")):
            with patch.object(handles, "fetch", return_value=(200, url, body)):
                self.assertEqual(handles.p_youtube("example")[0], handles.UNVERIFIED)

    def test_http_negative_is_not_claimability(self):
        self.assertEqual(handles.by_status(404)[0], handles.NO_RECORD)
        self.assertEqual(handles.by_status(429)[0], handles.UNVERIFIED)

    def test_pypi_normalises_query(self):
        with patch.object(handles, "fetch", return_value=(404, "query", "{}")) as fetch:
            self.assertEqual(handles.p_pypi("my_name.test")[0], handles.NO_RECORD)
            self.assertIn("my-name-test", fetch.call_args.args[0])

    def test_trace_records_both_source_and_final_url(self):
        handles.TRACE.requests = []
        handles.record_response(404, "source", "final", "{}")
        evidence = handles.TRACE.requests[0]
        self.assertEqual(evidence["url"], "source")
        self.assertEqual(evidence["final_url"], "final")
        self.assertEqual(len(evidence["body_sha256"]), 64)

    def test_cli_preserves_manual_work_and_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "handles.json"
            with patch.object(sys, "argv", ["check", "--names", "example", "--only", "github", "--json", str(output)]), \
                    patch.object(handles, "fetch", return_value=(404, "fixture", "{}")), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(handles.main(), 0)
            result = json.loads(output.read_text())["example"]
        self.assertFalse(result["_summary"]["manual_complete"])
        self.assertEqual(result["github"]["claimability"], "UNCONFIRMED")
        self.assertIn("checked_at", result["github"])

    def test_invalid_requested_platform_check_exits_nonzero(self):
        with patch.object(sys, "argv", ["check", "--names", "a", "--only", "telegram"]), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(handles.main(), 1)


class CommandTests(unittest.TestCase):
    def test_sapi_values_are_data_not_powershell_code(self):
        values = {"voice": "Voice'); Write-Output injected; #", "text": "A name with ’ and ' quotes", "wav": "C:/O'Brien/audio.wav"}
        with patch.object(speech.subprocess, "run") as run:
            speech.speak_sapi(values["voice"], values["text"], values["wav"])
        script = run.call_args.args[0][-1]
        self.assertNotIn("Write-Output injected", script)
        self.assertNotIn("O'Brien", script)
        payload = script.split("FromBase64String('", 1)[1].split("')", 1)[0]
        self.assertEqual(json.loads(base64.b64decode(payload)), values)

    def test_cli_rejects_bad_input_before_network(self):
        for module, args in ((domains, ["--names", "bad/name"]),
                             (domains, ["--names", "example", "--attempts", "0"]),
                             (domains, []), (handles, ["--names", "bad?name"])):
            with self.subTest(module=module.__name__, args=args), patch.object(sys, "argv", ["check"] + args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 2)

    def test_missing_reading_cannot_report_convergence(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "speech.json"
            args = ["say", "--names", "example", "--langs", "en", "pl", "--readings-only", "--json", str(output)]
            with patch.object(sys, "argv", args), patch.object(speech, "find_espeak", return_value="fixture"), \
                    patch.object(speech, "readings", return_value=({"en": "test", "pl": None}, (1.0, None, None))), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(speech.main(), 1)
            self.assertEqual(json.loads(output.read_text())["example"]["convergence"]["verdict"], "UNSUPPORTED")

    def test_context_escapes_candidate_html(self):
        result = context.scenes('<script>alert(1)</script>', "description", [], "Sam")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)

    def test_generated_adapters_match_canonical_skill(self):
        for name, expected in adapters.render((ROOT / "SKILL.md").read_text(encoding="utf-8")).items():
            self.assertEqual((ROOT / name).read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
