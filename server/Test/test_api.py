import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def test_load_svg(floor):

    print(f"\nTesting /load_svg for floor {floor}")
    response = requests.get(f"{BASE_URL}/load_svg", params={"floor": floor})
    print_response(response)


def test_load_shortest_path_svg(floor):

    print(f"\nTesting /load_shortest_path_svg for floor {floor}")
    response = requests.get(
        f"{BASE_URL}/load_shortest_path_svg", params={"floor": floor}
    )
    print_response(response)


def test_process_path(start, end, preference):

    print(f"\nTesting /process_path from {start} to {end}")
    data = {"start": start, "end": end, "preference": preference}
    response = requests.post(f"{BASE_URL}/process_path", json=data)
    print_response(response)


def test_process_path_custom(type, start, end, preference):

    print(f"\nTesting /process_path from {start} to {end}")
    data = {"type": type, "start": start, "end": end, "preference": preference}
    response = requests.post(f"{BASE_URL}/cusom_process", json=data)
    print_response(response)


def test_register_user(username, password):

    print(f"\nTesting /register for user {username}")
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/register", json=data)
    print_response(response)


def test_login_user(username, password):

    print(f"\nTesting /login for user {username}")
    data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=data)
    print_response(response)


def test_get_users():

    print("\nTesting /users to fetch all users")
    response = requests.get(f"{BASE_URL}/users")
    print_response(response)


def test_get_user_timestamps(username):

    print(f"\nTesting /users/{username}/timestamps")
    response = requests.get(f"{BASE_URL}/users/{username}/timestamps")
    print_response(response)


def test_delete_user(username):

    print(f"\nTesting DELETE /users/{username}")
    response = requests.delete(f"{BASE_URL}/users/{username}")
    print_response(response)


def test_manage_teachers_post(data):

    print("\nTesting POST /teachers to add a teacher")
    response = requests.post(f"{BASE_URL}/teachers", json=data)
    print_response(response)


def test_manage_teachers_get(name=None, cabin_no=None, room_no=None):

    print("\nTesting GET /teachers with filters")
    params = {
        key: value
        for key, value in [("name", name), ("cabin_no", cabin_no), ("room_no", room_no)]
        if value
    }
    response = requests.get(f"{BASE_URL}/teachers", params=params)
    print_response(response)


def test_search_teacher(teacher_name):
    print(f"\nTesting /search_teacher for teacher name {teacher_name}")
    response = requests.get(
        f"{BASE_URL}/search_teacher", params={"teacher_name": teacher_name}
    )
    print_response(response)


def print_response(response):

    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:", json.dumps(response.json(), indent=4))
    except ValueError:
        print("Response Text:", response.text)


if __name__ == "__main__":

    test_process_path(start="322", end="504", preference="Lift")
    test_load_svg(floor=1)
    test_load_shortest_path_svg(floor=2)
    test_process_path(start="A", end="B", preference="shortest")
    test_process_path_custom(
        type="teacher cabin", start="G-02", end="T004", preference="Lift"
    )
    test_register_user(username="test_user", password="test_password")
    test_login_user(username="test_user", password="test_password")
    test_get_users()
    test_get_user_timestamps(username="test_user")
    test_delete_user(username="test_user")
    # test_manage_teachers_post(
    #     data={"name": "John Doe", "cabin_no": "101", "room_no": "202"}
    # )
    test_manage_teachers_get(cabin_no="101")
    test_search_teacher(teacher_name="Dr. Vishal Singh")
