from flask import Flask, request, jsonify, send_file
from .Utils.db_shortest_path_maker import validate_and_process_start_end as get_start_end
from .Utils.svg_manipulator import main as make_svg, output as output_svg_location
import os
from flask_cors import CORS
from .Utils.loader import env_variables
from .Utils.db_access import get_teacher_data, add_teacher_to_db
from .Utils.db_maker import (
    create_user_db,
    add_user,
    add_login_timestamp,
    get_all_users,
    get_login_timestamps,
    delete_user,
)

app = Flask(__name__)
CORS(app)


@app.route("/load_svg", methods=["GET"])
def load_svg():
    """
    Load an SVG from the Floor Maps directory.
    Query parameter: `floor=<int>`
    """
    floor = request.args.get("floor")
    if not floor:
        return jsonify({"error": "Floor parameter is required"}), 400

    svg_path = os.path.join(
        env_variables["floor_map"], f"Floor {floor} copy path.svg")
    if not os.path.exists(svg_path):
        return jsonify({"error": f"SVG file for floor {floor} not found"}), 404

    return send_file(svg_path, mimetype="image/svg+xml")


@app.route("/load_shortest_path_svg", methods=["GET"])
def load_shortest_path_svg():
    """
    Load a modified SVG file for the shortest path visualization.
    Query parameters: `floor=<int>`
    """
    floor = request.args.get("floor")
    if not floor:
        return jsonify({"error": "Floor parameter is required"}), 400

    # Construct the path to the output SVG file
    svg_path = output_svg_location(floor)
    if not os.path.exists(svg_path):
        return jsonify({"error": f"SVG file for floor {floor} not found"}), 404

    # Serve the SVG file
    return send_file(svg_path, mimetype="image/svg+xml")


@app.route("/process_path", methods=["POST"])
def process_path():
    """
    API Endpoint to process and visualize the shortest path on floor maps.

    This route accepts JSON input containing the start and end points of a path.
    It validates the input, determines the floor maps involved, and generates the 
    shortest path visualization on the corresponding SVG files. 

    If the path is within the same floor, it returns the modified SVG for that floor. 
    For paths spanning multiple floors, it returns URLs for the SVG files of the 
    respective floors.

    ---
    Input:
    - JSON payload: {"start": "start_description", "end": "end_description"}

    Output:
    - Single floor:
        - SVG file for the floor with the visualized path (mimetype: image/svg+xml)
    - Multiple floors:
        - JSON response with URLs for the SVG files for the start and end floors.

    Responses:
    - 200 OK: Successful response with SVG file or JSON containing URLs.
    - 400 Bad Request: Missing or invalid start/end points.
    - 404 Not Found: One or both floor map SVG files are unavailable.

    Example:
    Input:
    {
        "start": "Room A",
        "end": "Room B"
    }
    Output (Single Floor):
    SVG file visualizing the path between "Room A" and "Room B".

    Output (Multiple Floors):
    {
        "files": {
            "start_floor": "/load_shortest_path_svg?floor=1",
            "end_floor": "/load_shortest_path_svg?floor=2"
        }
    }
    """
    # Parse JSON input
    data = request.json
    start = data.get("start")
    end = data.get("end")

    # Log input data and request headers for debugging
    print("Received JSON:", request.json)
    print("Request Headers:", request.headers)

    # Validate input data
    if not start or not end:
        return jsonify({"error": "Start and end points are required"}), 400

    try:
        # Determine the floor numbers for start and end points
        start_floor_no, end_floor_no = get_start_end(start, end)

        # Construct file paths for the floor SVGs
        input_svg_start = os.path.join(
            env_variables["floor_map"], f"floor {start_floor_no} copy path.svg"
        )
        input_svg_end = os.path.join(
            env_variables["floor_map"], f"floor {end_floor_no} copy path.svg"
        )
        print(
            f"Input SVG Paths: Start: {input_svg_start}, End: {input_svg_end}")

        # Check if the SVG files exist
        if not os.path.exists(input_svg_start):
            return jsonify({"error": f"SVG file for floor {start_floor_no} not found"}), 404
        if not os.path.exists(input_svg_end):
            return jsonify({"error": f"SVG file for floor {end_floor_no} not found"}), 404

        # Modify the SVG to visualize the shortest path
        print("Processing and modifying SVGs for the path visualization")
        make_svg(start, end)

        # If the path is within the same floor, return the modified SVG
        if start_floor_no == end_floor_no:
            print("Path within a single floor, returning SVG for floor",
                  start_floor_no)
            output_svg = output_svg_location(start_floor_no)
            return send_file(output_svg, mimetype="image/svg+xml")

        # If the path spans multiple floors, return URLs for the respective SVGs
        print("Path spans multiple floors, returning URLs for start and end floor SVGs")
        return jsonify({
            "files": {
                "start_floor": f"/load_shortest_path_svg?floor={start_floor_no}",
                "end_floor": f"/load_shortest_path_svg?floor={end_floor_no}"
            }
        })
    except Exception as e:
        # Catch unexpected errors and log for debugging
        print("Error occurred:", e)
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/teachers", methods=["GET", "POST"])
def manage_teachers():
    """
    Handle POST and GET requests for teacher data.

    POST:
        - Adds a new teacher to the database.
        - Expects a JSON payload with:
          { "name": str, "cabin_no": str, "room_no": str, "phone_number": str, "email": str }

    GET:
        - Retrieves teacher data with optional filters:
          Query Parameters:
            - name: Filter by teacher name (supports partial matches with SQL LIKE).
            - cabin_no: Filter by cabin number.
            - room_no: Filter by room number.

    Returns:
        JSON response containing the operation result or teacher data.
    """
    if request.method == "POST":
        # Handle POST: Add a new teacher
        data = request.get_json()
        required_fields = ["name", "cabin_no",
                           "room_no", "phone_number", "email"]

        # Validate input
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            # Call database function to add teacher
            db_path = env_variables["db_path"]
            add_teacher_to_db(db_path, data)
            return jsonify({"message": "Teacher added successfully"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "GET":
        # Handle GET: Retrieve teacher data
        name = request.args.get("name")
        cabin_no = request.args.get("cabin_no")
        room_no = request.args.get("room_no")

        try:
            # Call database function to retrieve teachers
            db_path = env_variables["db_path"]
            teachers = get_teacher_data(db_path, name, cabin_no, room_no)
            return jsonify(teachers), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Register a new user


@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    result = add_user(username, password, env_variables["user_db_path"])
    return jsonify(result), 201 if "message" in result else 400

# Log in a user and add a timestamp


@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400

    result = add_login_timestamp(username, env_variables["user_db_path"])
    return jsonify(result), 200 if "message" in result else 404

# Get all users


@app.route('/users', methods=['GET'])
def get_users():
    users = get_all_users(env_variables["user_db_path"])
    return jsonify({"users": [{"id": user[0], "username": user[1]} for user in users]}), 200

# Get login timestamps for a specific user


@app.route('/users/<username>/timestamps', methods=['GET'])
def get_timestamps(username):
    result = get_login_timestamps(username, env_variables["user_db_path"])
    if isinstance(result, dict):  # If an error occurred
        return jsonify(result), 404
    return jsonify({"timestamps": [{"id": ts[0], "login_time": ts[2]} for ts in result]}), 200

# Delete a user (cascades to delete their timestamps)


@app.route('/users/<username>', methods=['DELETE'])
def delete_user_route(username):
    result = delete_user(username, env_variables["user_db_path"])
    return jsonify(result), 200 if "message" in result else 404


if __name__ == "__main__":
    app.run(debug=True)
