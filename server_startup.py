import subprocess
import sys
import os
import platform


def setup_project():
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("Requirements installed successfully.")
        setup_env_file()
        ensure_db_files_exist()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")
        sys.exit(1)


def setup_env_file():
    if os.getenv("RAILWAY_ENVIRONMENT"):  # Running on Railway
        print("Running on Railway. Skipping .env file creation.")
        return

    server_dir = os.path.join(os.getcwd(), "server")
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)

    env_file_path = os.path.join(server_dir, ".env")
    pythonpath = os.path.join(os.getcwd(), "server")

    db_map_path = os.path.join("DB", "Test_Use_3.db")
    db_auth_path = os.path.join("DB", "user_auth.db")
    excel_teacher_path = os.path.join("Teacher_Data", "faculty.xlsx")
    assets_dir = os.path.join("..", "Assets", "location_symbol-removebg.png")
    audio_dir = os.path.join("Chatbot", "temp_audio")
    floor_maps_dir = "Floor_Maps"
    output_maps_dir = "Output_Maps"

    env_content = f"""DB_MAP_PATH={db_map_path}
DB_AUTH_PATH={db_auth_path}
EXCEL_TEACHER_PATH={excel_teacher_path}
FLASK_APP=app.py
FLOOR_MAPS_DIR={floor_maps_dir}
OUTPUT_MAPS_DIR={output_maps_dir}
ASSETS_DIR={assets_dir}
AUDIO_DIR={audio_dir}
PYTHONPATH={pythonpath}
"""

    try:
        if not os.path.exists(env_file_path):
            print("Creating .env file in the 'server' directory...")
            with open(env_file_path, "w") as env_file:
                env_file.write(env_content)
            print(".env file created with dynamic PYTHONPATH and default values.")
        else:
            print(".env file already exists. Skipping creation.")
    except IOError as e:
        print(f"Error creating .env file: {e}")
        sys.exit(1)


def ensure_db_files_exist():
    db_files = ["server/DB/Test_Use_3.db", "server/DB/user_auth.db"]
    for db_file in db_files:
        if not os.path.exists(db_file):
            print(f"Creating empty database file: {db_file}")
            open(db_file, "w").close()


if __name__ == "__main__":
    setup_project()
