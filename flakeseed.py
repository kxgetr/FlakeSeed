"""Find and reduce a pytest ordering failure. Run from the project under test."""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("paths",nargs="*")
p.add_argument("--seed",type=int,default=1)
p.add_argument("--attempts",type=int,default=10)
p.add_argument("--budget",type=int,default=40)
p.add_argument("-o",type=Path,default=Path("flake-order.json"))
p.add_argument("--replay",type=Path)
a=p.parse_args()
if min(a.attempts,a.budget)<1: p.error("positive attempt and reduction limits required")
try: import pytest
except ImportError: p.exit(2,"Install pytest into this Python environment.\n")
base=[sys.executable,"-m","pytest","-p","flakeseed_plugin","-xq"]
env=os.environ.copy()
env["PYTHONPATH"]=str(Path(__file__).resolve().parent)+os.pathsep+env.get("PYTHONPATH","")
def run(args):
    result=subprocess.run(base+args,env=env)
    if result.returncode not in (0,1): p.exit(result.returncode,"pytest did not finish a valid test run\n")
    return result.returncode
if a.replay: raise SystemExit(run(json.loads(a.replay.read_bytes())["order"]))
with tempfile.TemporaryDirectory() as d:
    orderfile,failfile=Path(d,"order"),Path(d,"failure")
    env.update(FLAKESEED_RECORD=str(orderfile),FLAKESEED_FAILURE=str(failfile))
    def failure(args):
        failfile.unlink(missing_ok=True)
        return json.loads(failfile.read_bytes()) if run(args) and failfile.exists() else None
    for seed in range(a.seed,a.seed+a.attempts):
        sig=failure(["--flake-seed",str(seed),*a.paths])
        if not sig: continue
        order=json.loads(orderfile.read_bytes())
        order=order[:order.index(sig[0])+1]
        if failure(order)!=sig: continue
        width=len(order)-1
        budget=a.budget
        while width and budget:
            for i in range(0,len(order)-1,width):
                stop=min(i+width,len(order)-1)
                trial=order[:i]+order[stop:]
                budget-=1
                if failure(trial)==sig:
                    order=trial
                    break
                if not budget: break
            else:
                width=(width+1)//2 if width>1 else 0
            width=min(width,len(order)-1)
        a.o.write_text(json.dumps({"seed":seed,"signature":sig,"order":order},indent=2),encoding="utf8")
        print("Reproducible order saved:",a.o)
        raise SystemExit(1)
print("No reproducible failure found in the requested seeds.")
