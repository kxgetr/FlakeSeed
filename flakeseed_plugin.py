"""Pytest plugin used by the flakeseed command."""
import json,os,random
from pathlib import Path
import pytest
def pytest_addoption(parser):
    parser.addoption("--flake-seed",type=int,default=None,help="shuffle collected items with this seed")
@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config,items):
    seed=config.getoption("--flake-seed")
    if seed is not None: random.Random(seed).shuffle(items)
    target=os.getenv("FLAKESEED_RECORD")
    if target: Path(target).write_text(json.dumps([i.nodeid for i in items]),encoding="utf8")
def pytest_runtest_logreport(report):
    target=os.getenv("FLAKESEED_FAILURE")
    if target and report.failed:
        crash=getattr(report.longrepr,"reprcrash",None)
        Path(target).write_text(json.dumps([report.nodeid,report.when,getattr(crash,"message",str(report.longrepr))]),encoding="utf8")
