from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
RSS_WORKER_ROOT = REPO_ROOT / "rss-worker"

for path in (str(REPO_ROOT), str(RSS_WORKER_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)
