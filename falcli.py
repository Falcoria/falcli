#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))


from app.client import app


if __name__ == "__main__":
    app()
