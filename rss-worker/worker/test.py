import sys

from rss_worker.healthcheck import main, test_uvicorn

__all__ = ["main", "test_uvicorn"]


if __name__ == "__main__":
    sys.exit(main())
