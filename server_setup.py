import subprocess
import sys
def setup_project():
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")
        sys.exit(1)
if __name__ == "__main__":
    setup_project()