from sqlite3 import DatabaseError
from flask import Flask, jsonify, request, send_file
from .db_access import add_teacher_to_db, get_teacher_data, sqlite3
from .svg_manipulator import main as make_svg, output as output_svg_location
from .loader import env_variables
import os


class InvalidInputError (Exception):

    pass


def process_path_logic(data):
    start = data .get("start")
    end = data .get("end")
    preference = data .get("preference")

    if not start or not end:
        return {"error": "Start and end points are required"}, 400
    if start == end:
        return {"error": "Start and end points cannot be the same"}, 400

    try:

        result = make_svg(start, end, preference)

        if result["error"]:
            return {"error": result["error"]}, 500

        if result["complexity"] == "simple":
            floor_no = result["path"][0]
            output_svg = output_svg_location(floor_no)
            return send_file(output_svg, mimetype="image/svg+xml"), 200

        elif result["complexity"] == "complex":
            start_floor = result["path"][0][0]
            end_floor = result["path"][1][0]
            return jsonify({
                "files": {
                    "start_floor": f"/load_shortest_path_svg?floor={start_floor}",
                    "end_floor": f"/load_shortest_path_svg?floor={end_floor}"
                }
            }), 200
        return {"error": "Unexpected path complexity"}, 500

    except Exception as e:
        return {"error": str(e)}, 500


def load_svg_logic(floor):
    if not floor:
        return {"error": "Floor parameter is required"}, 400

    svg_path = os .path .join(
        env_variables["floor_map"], f"Floor {floor} copy path.svg")
    if not os .path .exists(svg_path):
        return {"error": f"SVG file for floor {floor} not found"}, 404

    return send_file(svg_path, mimetype="image/svg+xml"), 200


def load_shortest_path_svg_logic(floor):
    if not floor:
        return {"error": "Floor parameter is required"}, 400

    svg_path = output_svg_location(floor)
    if not os .path .exists(svg_path):
        return {"error": f"SVG file for floor {floor} not found"}, 404

    return send_file(svg_path, mimetype="image/svg+xml"), 200


def add_teacher(data):

    required_fields = ["name", "cabin_no", "room_no", "phone_number"]

    if not data or not all(field in data for field in required_fields):
        raise InvalidInputError("Missing required fields")

    try:
        db_path = env_variables["db_path"]
        add_teacher_to_db(db_path, data)
        return {"message": "Teacher added successfully"}
    except Exception as e:
        raise DatabaseError(f"Failed to add teacher: {str(e)}")


def retrieve_teachers(name, cabin_no, room_no):

    try:
        db_path = env_variables["db_path"]
        teachers = get_teacher_data(db_path, name, cabin_no, room_no)
        if not teachers:
            raise InvalidInputError("No teacher present")
        return teachers
    except Exception as e:
        raise DatabaseError(f"Failed to retrieve teachers: {str(e)}")


def format_cabin_no(cabin_no):

    if not cabin_no or len(cabin_no) < 2:
        raise ValueError("Invalid cabin number format")
    building_side = cabin_no[0].upper()
    cabin_number = cabin_no[1:]
    if not cabin_number .isdigit():
        raise ValueError("Invalid cabin number format")
    return f"{building_side}-{cabin_number}"


def get_room_no_by_cabin(cabin_no, db_path):

    formatted_cabin_no = format_cabin_no(cabin_no)

    try:

        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()

            query = """
            SELECT room_no
            FROM teachers
            WHERE TRIM(cabin_no) = ?;
            """
            cursor .execute(query, (formatted_cabin_no,))
            result = cursor .fetchone()

            return result[0]if result else None
    except sqlite3 .Error as e:
        print(f"An error occurred while accessing the database: {e}")
        return None


if __name__ == "__main__":

    try:
        print(get_room_no_by_cabin("a222", env_variables["db_path"]))
        print(get_room_no_by_cabin("203", env_variables["db_path"]))
        print(format_cabin_no("B202"))
        print(format_cabin_no("c303"))
        print(process_path_logic({
        'start': '218',
        'end': '204',
        'preference': 'shortest'
    }))
    except ValueError as e:
        print(f"Error in format_cabin_no: {e}")

    try:
        print(format_cabin_no(""))
    except ValueError as e:
        print(f"Error: {e}")

    try:
        print(format_cabin_no("123"))
    except ValueError as e:
        print(f"Error: {e}")
