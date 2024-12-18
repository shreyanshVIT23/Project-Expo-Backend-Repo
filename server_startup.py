import subprocess
import sys
import os


def setup_project():
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("Requirements installed successfully.")
        setup_env_file()
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")
        sys.exit(1)


def setup_env_file():
    server_dir = os.path.join(os.getcwd(), "server")
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
    env_file_path = os.path.join(server_dir, ".env")
    pythonpath = os.path.join(os.getcwd(), "server")
    env_content = (
        f"DB_MAP_PATH=DB\\Test_Use_3.db\n"
        f"DB_AUTH_PATH=DB\\user_auth.db\n"
        f"EXCEL_TEACHER_PATH=Teacher_Data\\faculty.xlsx\n"
        f"FLASK_APP=app.py\n"
        f"FLOOR_MAPS_DIR=Floor Maps\n"
        f"OUTPUT_MAPS_DIR=Output Maps\n"
        f"ASSETS_DIR=..\\Assets\\location_symbol-removebg.png\n"
        f"AUDIO_DIR=Chatbot\\temp_audio\n"
        f"PYTHONPATH={pythonpath}\n"
    )
    try:
        if not os.path.exists(env_file_path):
            print("Creating .env file in the 'server' directory...")
            with open(env_file_path, "w") as env_file:
                env_file.write(env_content)
            print(".env file created with dynamic PYTHONPATH and default values.")
        else:
            print(
                ".env file already exists in the 'server' directory. Skipping creation."
            )
    except IOError as e:
        print(f"Error creating .env file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_project()
