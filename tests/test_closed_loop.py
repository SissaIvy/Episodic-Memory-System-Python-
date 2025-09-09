import time
import uuid
import unittest

from closed_loop_security import build_system, Severity


def make_event(host: str = "host-1", ip=None, etype: str = "malware_alert", sev: Severity = Severity.HIGH):
    payload = {"host": host}
    if ip:
        payload["ip"] = ip
    return {
        "id": str(uuid.uuid4()),
        "source": "edr",
        "type": etype,
        "severity": int(sev),
        "timestamp": time.time(),
        "payload": payload,
    }


class TestClosedLoop(unittest.TestCase):
    def test_strict_happy_path(self):
        sysm = build_system(profile_name="strict")
        sysm.ingest_event(make_event(ip="203.0.113.5"))
        out = sysm.process_events()
        self.assertEqual(out["meta"]["profile"], "strict")
        self.assertGreaterEqual(out["insights"][0]["action_count"], 1)
        self.assertIn("trace", out["insights"][0])

    def test_strict_missing_fields_rejected(self):
        sysm = build_system(profile_name="strict")
        sysm.ingest_event({"type": "malware_alert"})  # missing required fields
        out = sysm.process_events()
        self.assertEqual(out["meta"]["counts"]["events"], 0)
        self.assertTrue(any("Missing required" in s for s in out["meta"]["issues"]))

    def test_explore_coerces(self):
        sysm = build_system(profile_name="explore")
        sysm.ingest_event({"type": "unknown"})  # coerced
        out = sysm.process_events()
        self.assertEqual(out["meta"]["counts"]["events"], 1)
        self.assertLessEqual(out["insights"][0]["confidence"], 0.8)  # lowered due to unknown


if __name__ == "__main__":
    unittest.main()
