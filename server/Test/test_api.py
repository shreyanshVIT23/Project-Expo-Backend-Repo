import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"


def log_response(output):
    with open("api_test_log.txt", "a") as log_file:
        log_file.write(output + "\n")


def test_load_svg(floor):
    response = requests.get(f"{BASE_URL}/load_svg", params={"floor": floor})
    log_response(f"\nTesting /load_svg for floor {floor}\n{format_response(response)}")


def test_load_shortest_path_svg(floor):
    response = requests.get(
        f"{BASE_URL}/load_shortest_path_svg", params={"floor": floor}
    )
    log_response(
        f"\nTesting /load_shortest_path_svg for floor {floor}\n{format_response(response)}"
    )


def test_process_path(start, end, preference):
    data = {"start": start, "end": end, "preference": preference}
    response = requests.post(f"{BASE_URL}/process_path", json=data)
    log_response(
        f"\nTesting /process_path from {start} to {end}\n{format_response(response)}"
    )


def test_process_path_custom(type, start, end, preference):

    data = {"type": type, "start": start, "end": end, "preference": preference}
    response = requests.post(f"{BASE_URL}/custom_process", json=data)
    log_response(
        f"\nTesting /custom_process from {start} to {end}\n{format_response(response)}"
    )


def test_register_user(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=data)
    log_response(
        f"\nTesting /register for user {username}\n{format_response(response)}"
    )


def test_login_user(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=data)
    log_response(f"\nTesting /login for user {username}\n{format_response(response)}")


def test_get_users():
    response = requests.get(f"{BASE_URL}/users")
    log_response(f"\nTesting /users to fetch all users\n{format_response(response)}")


def test_get_user_timestamps(username):
    response = requests.get(f"{BASE_URL}/users/{username}/timestamps")
    log_response(f"\nTesting /users/{username}/timestamps\n{format_response(response)}")


def test_delete_user(username):
    response = requests.delete(f"{BASE_URL}/users/{username}")
    log_response(f"\nTesting DELETE /users/{username}\n{format_response(response)}")


def test_manage_teachers_post(data):
    response = requests.post(f"{BASE_URL}/teachers", json=data)
    log_response(
        f"\nTesting POST /teachers to add a teacher\n{format_response(response)}"
    )


def test_manage_teachers_get(name=None, cabin_no=None, room_no=None):
    params = {
        key: value
        for key, value in [("name", name), ("cabin_no", cabin_no), ("room_no", room_no)]
        if value
    }
    response = requests.get(f"{BASE_URL}/teachers", params=params)
    log_response(f"\nTesting GET /teachers with filters\n{format_response(response)}")


def test_search_teacher(teacher_name):
    response = requests.get(
        f"{BASE_URL}/search_teacher", params={"teacher_name": teacher_name}
    )
    log_response(
        f"\nTesting /search_teacher for teacher name {teacher_name}\n{format_response(response)}"
    )


def format_response(response):
    output = f"Status Code: {response.status_code}\n"
    try:
        output += "Response JSON:\n" + json.dumps(response.json(), indent=4)
    except ValueError:
        output += "Response Text:\n" + response.text
    return output


if __name__ == "__main__":
    try:
        os.remove("api_test_log.txt")
    except FileNotFoundError:
        print("File api_test_log.txt doesn't exist yet.")

    test_process_path(start="322", end="504", preference="Lift")
    test_load_svg(floor=1)
    test_load_shortest_path_svg(floor=2)
    test_process_path_custom(
        type="teacher cabin", start="g02", end="T004", preference="Lift"
    )
    test_register_user(username="test_user", password="test_password")
    test_login_user(username="test_user", password="test_password")
    test_get_users()
    test_get_user_timestamps(username="test_user")
    test_delete_user(username="test_user")
    # test_manage_teachers_post(
    #     data={"name": "John Doe", "cabin_no": "101", "room_no": "202"}
    # )
    test_manage_teachers_get(cabin_no="G-02")
    test_search_teacher(teacher_name="Dr. Vishal Singh")
