import subprocess
import sys
import os
def run_svg_manipulator(param1, param2, param3):
    try:
        os.chdir("server")
        print("Changed directory to 'server'.")
        subprocess.run(
            ["python", "-m", "Utils.svg_manipultor", param1, param2, param3],
            check=True
        )
        print("Command executed successfully.")
    except FileNotFoundError:
        print("Error: 'server' directory not found. Please ensure the directory exists.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        sys.exit(1)
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python run_svg_manipulator.py <param1> <param2> <param3>")
        sys.exit(1)
    param1 = sys.argv[1]
    param2 = sys.argv[2]
    param3 = sys.argv[3]
    run_svg_manipulator(param1, param2, param3)