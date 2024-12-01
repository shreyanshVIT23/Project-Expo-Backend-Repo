import subprocess
import sys
import os
import webbrowser
from pathlib import Path
def run_svg_manipulator(param1, param2, param3, open_in_browser=False):
    try:
        os.chdir("server")
        print("Changed directory to 'server'.")
        process = subprocess.run(
            ["python", "-m", "Utils.svg_manipultor", param1, param2, "--preference", param3],
            capture_output=True,
            text=True,
            check=True
        )
        output = process.stdout.strip().splitlines()[-1]
        print("Output from svg_manipulator:")
        print(process.stdout)
        if open_in_browser:
            output_path = Path(output)  
            if output_path.exists():
                print(f"Opening {output_path} in the default web browser...")
                webbrowser.open(output_path.resolve().as_uri())
            else:
                print(f"Error: Output file {output_path} does not exist.")
    except FileNotFoundError:
        print("Error: 'server' directory not found. Please ensure the directory exists.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the command:")
        print(e.stderr if e.stderr else e)
        sys.exit(1)
if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python run_svg_manipulator.py <param1> <param2> <param3> [--open]")
        sys.exit(1)
    param1 = sys.argv[1]
    param2 = sys.argv[2]
    param3 = sys.argv[3]
    open_in_browser = "--open" in sys.argv
    run_svg_manipulator(param1, param2, param3, open_in_browser)