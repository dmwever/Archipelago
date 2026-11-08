import json
import pathlib

RECORDS = 256
FIELDS = 8

payload = ["string AP78", "int 1", "int %d" % RECORDS]
payload += ["int *"] * (RECORDS * FIELDS)
payload += ["string *", "string *", "string END", "int *", "int 424242"]

out = pathlib.Path(__file__).resolve().parent / "ledger.json"
out.write_text(json.dumps({"payload": payload}), encoding="utf-8")
print("wrote %s with %d entries" % (out.name, len(payload)))
