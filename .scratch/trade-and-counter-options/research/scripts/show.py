import json,sys
r=json.load(open("out.json"))
def key(x): 
    return json.dumps([x["players"],x["gaia"],x["dip_triggers"]])
by={}
for x in r:
    k,n=x["label"].split(":",1); by.setdefault(n,{})[k]=x
for n in sorted(by):
    v=by[n]; ks=list(v)
    same={a:key(v[a])==key(v[ks[0]]) for a in ks}
    print("==",n,{a:("same" if s else "DIFF") for a,s in same.items()}, "first=",ks[0])
    for k in ks:
        if k!=ks[0] and same[k]: continue
        x=v[k]; print(" [%s]"%k)
        for p in x["players"]:
            print("   P%d %-22s %-7s p1->%s ->p1:%s M%s D%s"%(p["pid"],p["name"][:22],p["color"],p["p1_to"],p["to_p1"],p["market"] or "",p["dock"] or ""))
        if any(x["gaia"].values()): print("   GAIA",x["gaia"])
        for d in x["dip_triggers"]: print("   DIP",d)
