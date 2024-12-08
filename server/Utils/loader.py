from dotenv import load_dotenv
import os

load_dotenv()

env_variables = {
    "db_path": os.getenv("DB_MAP_PATH"),
    "floor_map": os.getenv("FLOOR_MAPS_DIR"),
    "output_map": os.getenv("OUTPUT_MAPS_DIR"),
    "python_path": os.getenv("PYTHONPATH"),
    "user_db_path": os.getenv("DB_AUTH_PATH"),
    "teacher_data": os.getenv("EXCEL_TEACHER_PATH"),
    "image_assets": os.getenv("ASSETS_DIR"),
    "audio_path": os.getenv("AUDIO_DIR"),
}

print(env_variables["python_path"])
