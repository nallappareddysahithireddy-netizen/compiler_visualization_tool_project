"""Basic-block and control-flow graph construction from TAC."""
import re

def build_control_flow(code):
    if not code: return [], {"nodes":[],"edges":[]}
    leaders={0}; labels={}
    for i,line in enumerate(code):
        if line.startswith("label "): labels[line.split()[1]]=i; leaders.add(i)
        if line.startswith("goto ") or line.startswith("ifFalse "):
            if i+1<len(code): leaders.add(i+1)
    for i,line in enumerate(code):
        m=re.search(r"goto\s+(L\d+)",line)
        if m and m.group(1) in labels: leaders.add(labels[m.group(1)])
    starts=sorted(leaders); blocks=[]
    for n,start in enumerate(starts):
        end=starts[n+1] if n+1<len(starts) else len(code)
        blocks.append({"id":f"B{n+1}","start":start,"end":end,"instructions":code[start:end],"successors":[]})
    index_to_block={i:b["id"] for b in blocks for i in range(b["start"],b["end"])}
    label_to_block={}
    for b in blocks:
        for line in b["instructions"]:
            if line.startswith("label "): label_to_block[line.split()[1]]=b["id"]
    for idx,b in enumerate(blocks):
        last=b["instructions"][-1] if b["instructions"] else ""
        target=re.search(r"goto\s+(L\d+)",last)
        if target and target.group(1) in label_to_block: b["successors"].append(label_to_block[target.group(1)])
        if last.startswith("ifFalse") and idx+1<len(blocks): b["successors"].append(blocks[idx+1]["id"])
        elif not last.startswith("goto ") and not last.startswith("ifFalse") and idx+1<len(blocks): b["successors"].append(blocks[idx+1]["id"])
        b["successors"]=list(dict.fromkeys(b["successors"]))
    edges=[{"from":b["id"],"to":dest,"label":"flow"} for b in blocks for dest in b["successors"]]
    return blocks,{"nodes":[{"id":b["id"],"label":b["id"]} for b in blocks],"edges":edges}
