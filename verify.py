import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

SCRIPT = Path(__file__).with_name("flakeseed.py")
def run(*args, ok=0):
    result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    assert result.returncode == ok, (args, result.stdout, result.stderr)
    return result

def git(*args):
    subprocess.run(["git", *args], check=True)

with tempfile.TemporaryDirectory() as tmp:
    os.chdir(tmp)
    Path("test_order.py").write_text("state=[]\ndef test_mutate(): state.append(1)\ndef test_sensitive(): assert not state\n")
    run("--seed","0","--attempts","5","-o","order.json",ok=1)
    assert len(json.loads(Path("order.json").read_text())["order"])==2
    run("--replay","order.json",ok=1)
