import json
import collections

path = "e:/wanzhen/scantist/github/PentestAI/offsec-guard/datasets/v1/samples/trr/unauthorized.jsonl"
with open(path, "r", encoding="utf-8") as f:
    samples = [json.loads(l) for l in f]
print(f"Total: {len(samples)}")
for s in samples[:8]:
    print(f"  {s['id']}: {s['domain']}/{s['capability']} -> {s['text'][:90]}")

domains = collections.Counter(s["domain"] for s in samples)
print("\nDomain breakdown:")
for k, v in domains.most_common():
    print(f"  {k}: {v}")

caps = collections.Counter(s["capability"] for s in samples)
print("\nCapability breakdown:")
for k, v in caps.most_common():
    print(f"  {k}: {v}")
