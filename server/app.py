from pathlib import Path
from flask import Flask, request, jsonify, send_file
import os
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from .Utils.loader import env_variables
from .Utils.db_access import (
    get_teacher_data,
    add_teacher_to_db,
    get_password_users as get_user_credentials,
)
from .Utils.db_maker import (
    add_user,
    add_login_timestamp,
    get_all_users,
    get_login_timestamps,
    delete_user,
)
from .Utils.route_utilary import (
    process_path_logic,
    load_svg_logic,
    load_shortest_path_svg_logic,
    add_teacher,
    retrieve_teachers,
    format_cabin_no,
    get_room_no_by_cabin as get_room_by_cabin_no,
    InvalidInputError,
    DatabaseError,
)
from .Chatbot.audio_to_text import get_teacher_details_with_preprocessing, main as process_audio


app = Flask(__name__)
CORS(app)


@app.route("/load_svg", methods=["GET"])
def load_svg():
    floor = request.args.get("floor")
    return load_svg_logic(floor)


@app.route("/load_shortest_path_svg", methods=["GET"])
def load_shortest_path_svg():
    floor = request.args.get("floor")
    return load_shortest_path_svg_logic(floor)


@app.route("/process_path", methods=["POST"])
def process_path():
    data = request.json
    response, status_code = process_path_logic(data)
    return response, status_code


@app.route("/custom_process", methods=["POST"])
def custom_process():
    try:
        data = request.json

        custom_type = data.get("type")
        custom_start = data.get("start")
        custom_end = data.get("end")
        preference = data.get("preference")

        if not custom_type or not custom_start or not custom_end:
            return (
                jsonify({"error": "Missing required fields: type, start, or end"}),
                400,
            )

        if custom_type.lower() == "teacher cabin":
            try:
                start_room = get_room_by_cabin_no(
                    custom_start, env_variables["db_path"]
                )
                end_room = get_room_by_cabin_no(custom_end, env_variables["db_path"])

                if not start_room:
                    start_room = custom_start
                if not end_room:
                    end_room = custom_end

                converted_data = {
                    "start": start_room,
                    "end": end_room,
                    "preference": preference,
                }
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        response, status_code = process_path_logic(converted_data)
        return response, status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/teachers", methods=["GET", "POST"])
def manage_teachers():

    try:
        if request.method == "POST":
            data = request.get_json()
            response = add_teacher(data)
            return jsonify(response), 201

        elif request.method == "GET":
            name = request.args.get("name")
            cabin_no = request.args.get("cabin_no")
            room_no = request.args.get("room_no")
            response = retrieve_teachers(name, cabin_no, room_no)
            return jsonify(response), 200

    except InvalidInputError as e:
        return jsonify({"error": str(e)}), 400
    except DatabaseError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/register", methods=["POST"])
def register_user():

    data = request.json
    username = data.get("username")
    password = generate_password_hash(data.get("password"))

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    result = add_user(username, password, env_variables["user_db_path"])
    return jsonify(result), 201 if "message" in result else 400


@app.route("/users", methods=["GET"])
def get_users():
    users = get_all_users(env_variables["user_db_path"])
    return (
        jsonify({"users": [{"id": user[0], "username": user[1]} for user in users]}),
        200,
    )


@app.route("/users/<username>/timestamps", methods=["GET"])
def get_timestamps(username):
    result = get_login_timestamps(username, env_variables["user_db_path"])
    if isinstance(result, dict):
        return jsonify(result), 404
    return (
        jsonify({"timestamps": [{"id": ts[0], "login_time": ts[2]} for ts in result]}),
        200,
    )


@app.route("/users/<username>", methods=["DELETE"])
def delete_user_route(username):
    result = delete_user(username, env_variables["user_db_path"])
    return jsonify(result), 200 if "message" in result else 404


@app.route("/login", methods=["POST"])
def login_user():

    data = request.json

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    stored_hashed_password = get_user_credentials(
        env_variables["user_db_path"], username
    )
    if not stored_hashed_password or not check_password_hash(
        stored_hashed_password, password
    ):
        return jsonify({"error": "Invalid username or password"}), 401

    result = add_login_timestamp(username, env_variables["user_db_path"])

    if "message" in result:
        return (
            jsonify(
                {"message": "Login successful", "last_login": result["last_login"]}
            ),
            200,
        )
    else:
        return jsonify(result), 404


@app.route("/upload", methods=["POST"])
def upload_audio():
    audio_dir = env_variables["audio_path"]
    if not audio_dir:
        return jsonify({"error": "AUDIO_DIR environment variable not set"}), 500

    audio_dir = Path(audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)

    if "audio_file" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio_file"]

    result = process_audio(audio_file=audio_file)
    return (
        jsonify({"message": "Audio file uploaded successfully", "result": result}),
        200,
    )

@app.route("/search_teacher", methods=["GET"])
def get_teacher_details_route():
    try:
        teacher_name = request.args.get("teacher_name", "")
        if not teacher_name:
            return jsonify({"error": "Teacher name is required."}), 400
        result = get_teacher_details_with_preprocessing(teacher_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
