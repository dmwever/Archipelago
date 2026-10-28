import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORDS = 2400
FIELDS = 8

payload = ["string AP46", "int 1", "int %d" % RECORDS]
payload += ["int *"] * (RECORDS * FIELDS)
payload += ["string END", "int *", "int 424242"]

out = HERE / "run1-ledger.json"
out.write_text(json.dumps({"payload": payload}))
print("wrote %s with %d entries" % (out.name, len(payload)))
