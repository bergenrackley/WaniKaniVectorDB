import subprocess
import sys
import os
from pathlib import Path

def main():
    uvicorn = Path("venv") / "Scripts" / "uvicorn.exe" if os.name == "nt" else Path("venv") / "bin" / "uvicorn"

    if not uvicorn.exists():
        print("❌ Could not find uvicorn in venv. Run 'python setup.py' first.")
        return

    print("🚀 Starting FastAPI server at http://localhost:8000 ...")
    subprocess.run([str(uvicorn), "main:app", "--reload"])

if __name__ == "__main__":
    main()
