import json, re, hashlib, pathlib, collections, sys
d = pathlib.Path(r"C:\Users\DavidWever\Documents\GitHub\Archipelago\.scratch\scenario-difficulty\assets\ai-scripts")
if not (d / "index.json").exists():
    sys.exit(f"{d} not found: it is gitignored. Extract the AI scripts first with tools/dump_ai.py.")
idx = json.load(open(d / "index.json"))
DIFF = re.compile(r"\(\s*difficulty\s+(\S+)\s+(\w+)\s*\)", re.I)
LOADIF = re.compile(r"#load-if-(not-)?defined\s+(DIFFICULTY-[A-Z]+)")

def strip_comments(t):
    return "\n".join(l.split(";", 1)[0] for l in t.splitlines())

def forms(text):
    """Return top-level parenthesised forms with start offsets."""
    out, depth, start = [], 0, None
    for i, c in enumerate(text):
        if c == "(":
            if depth == 0: start = i
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0: out.append((start, text[start:i+1]))
    return out

def subforms(s):
    return [f for _, f in forms(s)]

def summarize_action(a):
    toks = a.strip("()").split()
    if not toks: return a
    h = toks[0]
    if h in ("chat-local-to-self", "chat-to-all", "chat-to-player", "chat-local", "disable-self", "chat-to-allies"): return None
    return " ".join(toks[:3])

rows, per_script = [], []
hashes = collections.defaultdict(list)
for e in idx:
    raw = (d / e["file"]).read_text(encoding="utf-8")
    t = strip_comments(raw)
    hashes[hashlib.sha1(raw.encode()).hexdigest()[:8]].append(e["file"])
    cmps = collections.Counter()
    rules = []
    for pos, f in forms(t):
        if not f.startswith("(defrule"): continue
        body = f[len("(defrule"):-1]
        if "=>" not in body: continue
        cond, act = body.split("=>", 1)
        dm = DIFF.findall(cond)
        if not dm: continue
        for op, lvl in dm: cmps[f"{op} {lvl}"] += 1
        conds = [c for c in subforms(cond) if not DIFF.fullmatch(c)]
        acts = [s for s in (summarize_action(a) for a in subforms(act)) if s]
        line = t[:pos].count("\n") + 1
        rules.append({"line": line, "difficulty": [f"{o} {l}" for o, l in dm], "conds": [" ".join(c.split()) for c in conds], "acts": acts})
    loadifs = collections.Counter(("!" if n else "") + s for n, s in LOADIF.findall(t))
    other = []
    for kw in ("difficulty-level", "set-difficulty-parameter"):
        for m in re.finditer(r"\(" + kw + r"[^)]*\)", t): other.append(" ".join(m.group(0).split()))
    loads = re.findall(r'\(load\s+"([^"]+)"\)', t)
    per_script.append({**e, "rules": rules, "cmps": dict(cmps), "loadifs": dict(loadifs), "other": other, "loads": loads})

json.dump(per_script, open(d.parent / "difficulty-inventory.json", "w"), indent=1)

ODD = {"== normal", "== standard", "< easy", "equal hard", ">= moderate", "< moderate", "<= hard"}
md = ["# Difficulty inventory of embedded AI scripts", "",
      "Generated from the 18 `AP_*.aoe2scenario` files (Ageipelago `scenario-difficulty` branch, 2026-11-11).",
      "Raw scripts: `ai-scripts/<scenario>_p<N>.per`; machine-readable: `difficulty-inventory.json`.",
      "`ai-scripts/` is gitignored (proprietary game content). If it is missing, extract it first with `python -I tools/dump_ai.py`.", ""]
# Summary table
md += ["## Per-script summary", "", "| Scenario | P | AI name | Live? | Rules w/ difficulty | Comparisons | `#load-if` DIFFICULTY | Loads `scenario difficulty*` | Other |", "|---|---|---|---|---|---|---|---|---|"]
for s in per_script:
    c = ", ".join(f"`{k}`×{v}" + (" ⚠" if k in ODD else "") for k, v in sorted(s["cmps"].items()))
    l = ", ".join(f"`{k}`×{v}" for k, v in sorted(s["loadifs"].items()))
    o = "; ".join(f"`{x}`" for x in s["other"])
    live = "yes" if (s["active"]=="True" and s["player"]>1) else ("P1 (human)" if s["player"]==1 else ("GAIA" if s["player"]==0 else "inactive"))
    sd = ", ".join(x for x in s["loads"] if "scenario difficulty" in x)
    md.append(f"| {s['scenario']} | {s['player']} | {s['personality']} | {live} | {len(s['rules'])} | {c} | {l} | {sd} | {o} |")
md += ["", "## Guarded rules per script", "",
       "Each rule: line, difficulty test(s), remaining conditions → actions (chat/disable-self dropped).", ""]
for s in per_script:
    if not s["rules"]: continue
    md.append(f"### {s['scenario']} p{s['player']} — {s['personality']}")
    md.append("")
    for r in s["rules"]:
        md.append(f"- L{r['line']} `{' & '.join(r['difficulty'])}` | {'; '.join(r['conds'])} → {'; '.join(r['acts'])}")
    md.append("")
md += ["## Identical script bodies", ""]
for h, fs in hashes.items():
    if len(fs) > 1: md.append(f"- `{h}`: {', '.join(fs)}")
(d.parent / "difficulty-inventory.md").write_text("\n".join(md), encoding="utf-8")

# headline stats
tot = collections.Counter(); byname = collections.defaultdict(lambda: [0,0,0])
for s in per_script:
    tot.update(s["cmps"])
    b = byname[s["personality"]]; b[0]+=1; b[1]+= bool(s["rules"]); b[2]+= bool(s["loadifs"])
print("scripts with rule-level difficulty:", sum(bool(s["rules"]) for s in per_script))
print("scripts with #load-if DIFFICULTY:", sum(bool(s["loadifs"]) for s in per_script))
print("neither:", [ (s['file'], s['personality']) for s in per_script if not s["rules"] and not s["loadifs"]])
print(tot.most_common())
for n,b in sorted(byname.items()):
    if b[1] or b[2]: pass
print({n:b for n,b in byname.items() if not n.endswith(" .ai") and ("player" not in n)})
print("dup groups", sum(len(v)>1 for v in hashes.values()))
