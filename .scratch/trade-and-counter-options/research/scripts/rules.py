import re, sys, glob, os
for f in sorted(glob.glob("per/*.per")):
    if f.endswith("_P1.per"): continue
    t = open(f, encoding="utf-8", errors="replace").read()
    t = re.sub(r";[^\n]*", "", t)
    out = []
    # conditional blocks
    conds = re.findall(r"#(?:load-if-defined|load-if-not-defined)\s+[\w-]+", t)
    for m in re.finditer(r"\(defrule(.*?)=>(.*?)\n\)", t, re.S):
        lhs, rhs = m.group(1), m.group(2)
        if re.search(r"\((build|build-forward) (market|dock)\)|\(train trade-(cart|cog)\)|(buy|sell)-commodity", rhs):
            acts = re.findall(r"\((?:build|build-forward) (?:market|dock)\)|\(train trade-\w+\)|\((?:buy|sell)-commodity \w+\)", rhs)
            lc = " ".join(lhs.split())
            # nearest preceding #load-if
            pre = t[:m.start()]
            blk = re.findall(r"#(load-if-defined|load-if-not-defined|else|end-if)\s*([\w-]*)", pre)
            depth = []
            for k, v in blk:
                if k.startswith("load"): depth.append(f"{k} {v}")
                elif k == "else" and depth: depth[-1] += " [else]"
                elif k == "end-if" and depth: depth.pop()
            out.append(f"   {sorted(set(acts))} IF {lc[:170]} {('IN '+str(depth)) if depth else ''}")
    loads = re.findall(r'\(load "([^"]+)"\)', t)
    print(os.path.basename(f)[:-4], "loads=", loads)
    for o in out: print(o)
