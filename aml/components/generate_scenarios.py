import argparse, json, time, uuid, random
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n_events", type=int, default=500)
    ap.add_argument("--out_path", type=str, required=True)  # jsonl
    args = ap.parse_args()
    random.seed(args.seed)

    severities = [0, 1, 2, 3, 4]  # INFO..CRITICAL
    types = ["failed_login", "malware_alert", "exfil_suspected", "benign_noise", "unknown"]
    Path(args.out_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.out_path).open("w", encoding="utf-8") as f:
        t0 = time.time()
        for i in range(args.n_events):
            etype = random.choices(types, weights=[25, 10, 5, 50, 10], k=1)[0]
            sev = random.choices(severities, weights=[20, 25, 25, 20, 10], k=1)[0]
            payload = {}
            if etype in {"malware_alert", "exfil_suspected"}:
                payload = {
                    "host": f"host-{random.randint(1, 200)}",
                    "ip": f"203.0.113.{random.randint(1, 254)}",
                }
            evt = {
                "id": str(uuid.uuid4()),
                "source": "sim",
                "type": etype,
                "severity": sev,
                "timestamp": t0 + i * 0.01,
                "payload": payload,
            }
            f.write(json.dumps(evt) + "\n")
    print(json.dumps({"status": "ok", "events": args.n_events}))


if __name__ == "__main__":
    main()

