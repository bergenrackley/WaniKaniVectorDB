import subprocess
import sys
import os
from shutil import copyfile
from pathlib import Path

def run(cmd, **kwargs):
    print(f"🔧 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, **kwargs)

def main():
    # Step 1: Create virtual environment if it doesn't exist
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        run([sys.executable, "-m", "venv", "venv"])

    # Step 2: Determine pip path
    pip = venv_dir / "Scripts" / "pip.exe" if os.name == "nt" else venv_dir / "bin" / "pip"

    # Step 3: Upgrade pip and install dependencies
    print("⬆️ Upgrading pip...")
    run([str(pip), "install", "--upgrade", "pip"])

    print("📚 Installing requirements...")
    run([str(pip), "install", "-r", "requirements.txt"])

    template = Path("config_template.json")
    config = Path("config.json")
    if template.exists() and not config.exists():
        print("🛡️  Creating config.json from template...")
        copyfile(template, config)
        print("🔑  Please add your WaniKani API key to config.json")
    
    print("✅ Setup complete! You can now run the app using: python run.py")

if __name__ == "__main__":
    main()
