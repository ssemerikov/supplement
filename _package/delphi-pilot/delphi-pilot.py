import json, time, re, math, os, concurrent.futures as cf, urllib.request, collections
OLLAMA=os.environ.get("OLLAMA_URL","http://localhost:11434/api/chat")
OMNI=os.environ.get("OMNI_URL","http://localhost:20128/v1/chat/completions")
# Never hardcode the gateway credential: this file ships in the supplement.
# Export OMNI_KEY before running. The pilot's raw responses are already archived in
# docs/design/delphi-pilot_raw.json, and code/02_pilot_icvi_cutpoint.py reproduces every
# published pilot statistic from that file without making any network call.
KEY=os.environ.get("OMNI_KEY","")
ITEMS=[("I01","It is important to him to make his own decisions about his life."),
("I02","It is important to him to help the people around him."),
("I03","Generally speaking, most people can be trusted."),
("I04","It is important to him to be very successful and have others recognise his achievements."),
("I05","The courts in this country treat everyone equally."),
("I06","Children should learn obedience above all else."),
("I07","It is important to him that every person in the world be treated justly."),
("I08","A strong leader can do more good for the country than all the laws and talk."),
("I09","It is important to him to be wealthy and to have expensive things."),
("I10","The government should reduce differences in income levels."),
("I11","People should do what they are told even when they disagree."),
("I12","It is important to him to care for nature and the environment.")]
DEFS="""D1 individualism<->collectivism: is the ultimate bearer of claims and responsibility the individual person or the collective?
D2 altruism<->egoism: is concern directed outward, to others, or inward, to the self?
D3 institutional trust/respect<->anti-institutional personalism: respect for impersonal rules and democratic institutions versus reliance on persons over institutions."""
SYS=("You are {persona}, serving as an independent expert panelist in a construct-validation exercise. "
 "Judge from your professional expertise. Be critical and discriminating. It is expected and valued that you reject items, "
 "give low ratings and disagree; a panel that approves everything is useless. "
 "Reply with exactly one fenced ```json block and nothing else.")
PERS="a survey methodologist specialising in cross-national measurement and item analysis"
ilist="\n".join(f"{i} {t}" for i,t in ITEMS)
T1=f"""TASK A. Assign each item below to EXACTLY ONE of three dimensions, or to REJECT if it does not measure any of them.
{DEFS}
ITEMS:
{ilist}
Return ONLY:
{{"assignments":[{{"id":"I01","dimension":"D1","confidence":0}}]}}
One entry per item. dimension must be one of D1, D2, D3, REJECT. confidence is an integer 0-100."""
T5=f"""TASK B. Rate on a 1-9 scale.
{DEFS}
(a) Rate the FACE VALIDITY of each dimension definition (1 = very poor, 9 = excellent).
(b) Rate the RELEVANCE of each item below to the three-dimension model (1 = not relevant, 9 = highly relevant).
ITEMS:
{ilist}
Return ONLY:
{{"definitions":[{{"id":"D1","face_validity":0}},{{"id":"D2","face_validity":0}},{{"id":"D3","face_validity":0}}],
 "items":[{{"id":"I01","relevance":0}}]}}
Integers 1-9 only. One entry per item."""
def post(u,p,h,t=600):
    r=urllib.request.Request(u,data=json.dumps(p).encode(),headers=h,method="POST")
    with urllib.request.urlopen(r,timeout=t) as x: return x.read().decode()
def sse(raw):
    o=[]
    for L in raw.splitlines():
        L=L.strip()
        if not L.startswith("data:"): continue
        p=L[5:].strip()
        if p=="[DONE]": break
        try: c=json.loads(p)
        except: continue
        for ch in c.get("choices",[]):
            pc=(ch.get("delta") or {}).get("content")
            if pc: o.append(pc)
    return "".join(o)
def xjson(t):
    m=re.search(r"```(?:json)?\s*(\{.*?\})\s*```",t,re.S)
    cands=[m.group(1)] if m else []
    s=t.find("{")
    if s!=-1: cands.append(t[s:t.rfind("}")+1])
    for c in cands:
        try: return json.loads(c)
        except: pass
    return None
def call(ch,m,task,rep):
    msgs=[{"role":"system","content":SYS.format(persona=PERS)},{"role":"user","content":task}]
    try:
        if ch=="ollama":
            b=post(OLLAMA,{"model":m,"messages":msgs,"stream":False,"think":False,"options":{"temperature":0.3,"seed":7+rep,"num_predict":6000}},{"Content-Type":"application/json"})
            return xjson(json.loads(b).get("message",{}).get("content",""))
        return xjson(sse(post(OMNI,{"model":m,"messages":msgs,"temperature":0.3,"max_tokens":6000},{"Content-Type":"application/json","Authorization":f"Bearer {KEY}"})))
    except Exception as e: return {"__err":str(e)[:60]}
EPS=[("ollama","gpt-oss:120b-cloud"),("ollama","gemma4:31b-cloud"),("ollama","nemotron-3-ultra:cloud"),("ollama","minimax-m3:cloud"),
     ("omniroute","kiro/claude-haiku-4.5"),("omniroute","kiro/claude-sonnet-4.5"),("omniroute","kiro/glm-5"),("omniroute","kiro/deepseek-3.2")]
jobs=[(ch,m,"T1",r) for ch,m in EPS for r in (0,1)]+[(ch,m,"T5",r) for ch,m in EPS for r in (0,1)]
def run(j):
    ch,m,t,r=j
    return (ch,m,t,r,call(ch,m,T1 if t=="T1" else T5,r))
with cf.ThreadPoolExecutor(max_workers=16) as ex: res=list(ex.map(run,jobs))
json.dump([[a,b,c,d,e] for a,b,c,d,e in res],open("/tmp/claude-1001/-home-cc-Dropbox-Conference--2026-Springer-journals-paper69/6a6a461b-155c-4a12-9a3e-d5d8ad6ff982/scratchpad/pilot_raw.json","w"),indent=1)
print("=== T1 assignment distribution per item (over endpoint x replicate draws) ===")
assign=collections.defaultdict(list); conf=collections.defaultdict(list); nT1=0
for ch,m,t,r,o in res:
    if t!="T1" or not o or "assignments" not in o: continue
    nT1+=1
    for a in o["assignments"]:
        if a.get("id") and a.get("dimension"): assign[a["id"]].append(a["dimension"]); conf[a["id"]].append(a.get("confidence"))
print(f"valid T1 draws: {nT1}/{len(EPS)*2}")
def H(v):
    c=collections.Counter(v); n=len(v)
    return -sum((k/n)*math.log(k/n,4) for k in c.values()) if n else float("nan")
tot=[]
for i,_ in ITEMS:
    v=assign[i]; c=collections.Counter(v)
    h=H(v); tot.append(h)
    print(f"  {i}  n={len(v):2}  H={h:.3f}  modal={c.most_common(1)[0][0]}({c.most_common(1)[0][1]}/{len(v)})  {dict(c)}")
print(f"  MEAN ENTROPY (T1) = {sum(tot)/len(tot):.3f}   [0=unanimous, 1=uniform over 4 options]")
allc=[x for i,_ in ITEMS for x in conf[i] if isinstance(x,(int,float))]
print(f"  confidence: n={len(allc)} mean={sum(allc)/len(allc):.1f} min={min(allc)} max={max(allc)} at-100={sum(1 for x in allc if x>=100)/len(allc):.2f}")
print("\n=== T5 (absolute 1-9 ratings) ===")
dv=collections.defaultdict(list); iv=collections.defaultdict(list); nT5=0
for ch,m,t,r,o in res:
    if t!="T5" or not o or "items" not in o: continue
    nT5+=1
    for d in o.get("definitions",[]) or []:
        if isinstance(d.get("face_validity"),(int,float)): dv[d["id"]].append(d["face_validity"])
    for it in o.get("items",[]) or []:
        if isinstance(it.get("relevance"),(int,float)): iv[it["id"]].append(it["relevance"])
print(f"valid T5 draws: {nT5}/{len(EPS)*2}")
for d in ("D1","D2","D3"):
    v=dv[d]; print(f"  {d} face_validity n={len(v)} mean={sum(v)/len(v):.2f} min={min(v)} max={max(v)} pct>=8={sum(1 for x in v if x>=8)/len(v):.2f}")
allrel=[]
for i,_ in ITEMS:
    v=iv[i]; allrel+=v
    print(f"  {i} relevance n={len(v)} mean={sum(v)/len(v):.2f} min={min(v)} max={max(v)}")
import statistics as st
print(f"  ALL item relevance: n={len(allrel)} mean={st.mean(allrel):.2f} sd={st.pstdev(allrel):.2f} pct>=7={sum(1 for x in allrel if x>=7)/len(allrel):.3f} pct==9={sum(1 for x in allrel if x==9)/len(allrel):.3f}")
# I-CVI analogue: proportion rating >=7 on 1-9
icvi=[sum(1 for x in iv[i] if x>=7)/len(iv[i]) for i,_ in ITEMS if iv[i]]
print(f"  I-CVI analogue (>=7 of 9): mean={sum(icvi)/len(icvi):.3f}  n_items_at_1.00={sum(1 for x in icvi if x==1.0)}/{len(icvi)}")
# item-discrimination ratio: between-item var / (between-item + within)
gm=st.mean(allrel); im=[st.mean(iv[i]) for i,_ in ITEMS if iv[i]]
sb=st.pvariance(im); sw=st.mean([st.pvariance(iv[i]) for i,_ in ITEMS if len(iv[i])>1])
print(f"  T5 item-discrimination ratio D = {sb/(sb+sw):.3f}   (sigma2_item={sb:.3f}, sigma2_within={sw:.3f})")
