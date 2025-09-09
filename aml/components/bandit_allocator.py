import argparse, json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior_alpha", type=float, default=1.0)
    ap.add_argument("--prior_beta", type=float, default=1.0)
    ap.add_argument("--strict_metric", type=str, required=False)
    ap.add_argument("--explore_metric", type=str, required=False)
    ap.add_argument("--allocation_json", type=str, required=True)
    args = ap.parse_args()

    s = json.loads(Path(args.strict_metric).read_text()) if args.strict_metric and Path(args.strict_metric).exists() else {}
    e = json.loads(Path(args.explore_metric).read_text()) if args.explore_metric and Path(args.explore_metric).exists() else {}

    # Thompson sampling on success proxy = (1 - failure_rate)
    def draw_success(m):
        succ = max(0.0, 1.0 - m.get("failure_rate", 0.2))
        alpha = args.prior_alpha + succ * 100
        beta = args.prior_beta + (1 - succ) * 100
        # beta sample via gamma
        import random

        a = random.gammavariate(alpha, 1.0)
        b = random.gammavariate(beta, 1.0)
        return a / (a + b)

    ps = draw_success(s) if s else 0.5
    pe = draw_success(e) if e else 0.5
    total = ps + pe if ps + pe > 0 else 1.0
    allocation = {"strict": ps / total, "explore": pe / total}
    Path(args.allocation_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.allocation_json).write_text(json.dumps(allocation, indent=2), encoding="utf-8")
    print(json.dumps(allocation))


if __name__ == "__main__":
    main()

