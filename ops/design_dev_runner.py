#!/usr/bin/env python3
"""
Orchestrate design checks + site build + git deploy for website development loop.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMDS = [
    ['python3', str(ROOT / 'ops' / 'design_compare.py')],
    ['python3', str(ROOT / 'scripts' / 'build_site.py')],
]

for cmd in CMDS:
    print(f'\n$ {" ".join(cmd)}')
    subprocess.run(cmd, check=True, cwd=ROOT)

print('\nDesign dev runner completed. Next: commit/push if output is acceptable.')
