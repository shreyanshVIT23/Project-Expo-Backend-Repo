import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"
# BASE_URL = "https://project-expo-backend-server-production.up.railway.app/"


def log_response(method, endpoint, params=None, json_data=None, output=""):
    with open("api_test_log.txt", "a") as log_file:
        log_file.write(f"\nTesting {method} {endpoint}")
        if params:
            log_file.write(f"\nParameters: {json.dumps(params, indent=4)}")
        if json_data:
            log_file.write(f"\nRequest Body: {json.dumps(json_data, indent=4)}")
        log_file.write(f"\n{output}\n")


def test_load_svg(floor):
    response = requests.get(f"{BASE_URL}/load_svg", params={"floor": floor})
    log_response(
        "GET", "/load_svg", params={"floor": floor}, output=format_response(response)
    )


def test_load_shortest_path_svg(floor):
    response = requests.get(
        f"{BASE_URL}/load_shortest_path_svg", params={"floor": floor}
    )
    log_response(
        "GET",
        "/load_shortest_path_svg",
        params={"floor": floor},
        output=format_response(response),
    )


def test_process_path(start, end, preference):
    data = {"start": start, "end": end, "preference": preference}
    response = requests.post(f"{BASE_URL}/process_path", json=data)
    log_response(
        "POST", "/process_path", json_data=data, output=format_response(response)
    )


def test_process_path_custom(type, start, end, preference):
    data = {"type": type, "start": start, "end": end, "preference": preference}
    response = requests.post(f"{BASE_URL}/custom_process", json=data)
    log_response(
        "POST", "/custom_process", json_data=data, output=format_response(response)
    )


def test_register_user(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=data)
    log_response("POST", "/register", json_data=data, output=format_response(response))


def test_login_user(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=data)
    log_response("POST", "/login", json_data=data, output=format_response(response))


def test_get_users():
    response = requests.get(f"{BASE_URL}/users")
    log_response("GET", "/users", output=format_response(response))


def test_get_user_timestamps(username):
    response = requests.get(f"{BASE_URL}/users/{username}/timestamps")
    log_response(
        "GET", f"/users/{username}/timestamps", output=format_response(response)
    )


def test_delete_user(username):
    response = requests.delete(f"{BASE_URL}/users/{username}")
    log_response("DELETE", f"/users/{username}", output=format_response(response))


def test_manage_teachers_post(data):
    response = requests.post(f"{BASE_URL}/teachers", json=data)
    log_response("POST", "/teachers", json_data=data, output=format_response(response))


def test_manage_teachers_get(name=None, cabin_no=None, room_no=None):
    params = {
        key: value
        for key, value in [("name", name), ("cabin_no", cabin_no), ("room_no", room_no)]
        if value
    }
    response = requests.get(f"{BASE_URL}/teachers", params=params)
    log_response("GET", "/teachers", params=params, output=format_response(response))


def test_search_teacher(teacher_name):
    response = requests.get(
        f"{BASE_URL}/search_teacher", params={"teacher_name": teacher_name}
    )
    log_response(
        "GET",
        "/search_teacher",
        params={"teacher_name": teacher_name},
        output=format_response(response),
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
        os.open("api_test_log.txt", os.O_CREAT)

    test_process_path(start="402", end="504", preference="Lift")
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
