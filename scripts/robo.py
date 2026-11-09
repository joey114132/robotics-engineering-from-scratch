#!/usr/bin/env python3
# robo 실행기: scripts/robo/ 패키지를 불러 CLI 를 돌린다 (python3 scripts/robo.py --help)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from robo.cli import main
except ImportError as e:
    if "rich" in str(e):
        sys.exit("robo needs the 'rich' package: pip install rich")
    raise

if __name__ == "__main__":
    sys.exit(main())
