import webbrowser
import subprocess
import sys
import json
from pathlib import Path


def sanitize_output(output):
    """Extract the JSON-like portion from the output."""
    for line in output.splitlines():
        if line.startswith("{") and line.endswith("}"):
            return line  # Return the JSON-like content
    return None


def run_svg_manipulator(param1, param2, param3, open_in_browser=False):
    try:
        # Use the current Python executable from the active environment
        python_executable = sys.executable

        process = subprocess.run(
            [
                python_executable, "-m", "Utils.svg_manipulator", param1, param2, "--preference", param3
            ],
            capture_output=True,
            text=True,
            check=True
        )

        raw_output = process.stdout.strip()
        print("Raw output:")
        print(raw_output)

        # Sanitize and parse output
        json_part = sanitize_output(raw_output)
        if not json_part:
            raise ValueError("No JSON-like content found in the output.")

        result = json.loads(json_part.replace("'", '"'))  # Replace single quotes if necessary
        print("Output from svg_manipulator (as dictionary):", result)

        # Further handling (e.g., open SVGs)
        if "svg_updates" in list(result.keys()) and open_in_browser:
            for svg_file in result["svg_updates"]:
                svg_path = Path(svg_file)
                if svg_path.exists():
                    print(f"Opening {svg_path} in the default web browser...")
                    webbrowser.open(svg_path.resolve().as_uri())
                else:
                    print(f"Error: Output file {svg_path} does not exist.")
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Error: {e}")
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
