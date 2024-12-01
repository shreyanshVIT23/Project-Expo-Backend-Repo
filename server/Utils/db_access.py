import sqlite3
from typing import List, Dict, Any
from .loader import env_variables


def get_coordinates(db_path, description_condition, floor_condition):

    try:
        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()
            query = """
                SELECT apc.x_coordinate, apc.y_coordinate
                FROM anchor_point_coordinates apc
                JOIN anchor_point_description apd ON apc.id = apd.anchor_point_id
                WHERE TRIM(apd.description) LIKE TRIM(?) AND apc.floor = ?
            """
            cursor .execute(query, (description_condition, floor_condition))
            return cursor .fetchall()
    except sqlite3 .Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None


def get_coordinates_thorough(db_path, description_condition):

    try:
        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()
            query = """
                SELECT apc.x_coordinate, apc.y_coordinate, apc.floor
                FROM anchor_point_coordinates apc
                JOIN anchor_point_description apd ON apc.id = apd.anchor_point_id
                WHERE apd.description LIKE '%' || ? || '%' 
                   OR apd.extra_info LIKE '%' || ? || '%';
            """
            cursor .execute(
                query, (description_condition, description_condition))
            return cursor .fetchone()
    except sqlite3 .Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None


def get_description(db_path, coordinates, floor_condition):

    try:
        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()
            query = """
                SELECT apd.description
                FROM anchor_point_coordinates apc
                JOIN anchor_point_description apd ON apc.id = apd.anchor_point_id
                WHERE apc.x_coordinate = ? AND apc.y_coordinate = ? AND apc.floor = ?
            """
            cursor .execute(query, (*coordinates, floor_condition))
            return [row[0]for row in cursor .fetchall()]
    except sqlite3 .Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return None


def get_teacher_data(db_path: str, name: str = None, cabin_no: str = None, room_no: str = None) -> List[Dict[str, Any]]:

    query = "SELECT name, cabin_no, room_no, phone_number FROM teachers WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params .append(f"%{name}%")
    if cabin_no:
        query += " AND cabin_no = ?"
        params .append(cabin_no)
    if room_no:
        query += " AND room_no = ?"
        params .append(room_no)

    try:
        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()
            cursor .execute(query, params)
            result = cursor .fetchall()

        return [
            {
                "name": row[0],
                "cabin_no": row[1],
                "room_no": row[2],
                "phone_number": row[3]
            }
            for row in result
        ]
    except sqlite3 .Error as e:
        raise Exception(f"Database error: {e}")


def add_teacher_to_db(db_path: str, data: Dict[str, Any]):

    try:
        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()
            cursor .execute("""
                INSERT INTO teachers (name, cabin_no, room_no, phone_number)
                VALUES (?, ?, ?, ?, ?);
            """, (data["name"], data["cabin_no"], data["room_no"], data["phone_number"]))
            conn .commit()
    except sqlite3 .Error as e:
        raise Exception(f"Database error: {e}")


def get_password_users(db_path, username):

    try:
        with sqlite3 .connect(db_path)as conn:
            cursor = conn .cursor()

            query = "SELECT password FROM users WHERE username = ?"
            cursor .execute(query, (username,))
            result = cursor .fetchone()

            return result[0]if result else None

    except sqlite3 .Error as e:
        print(f"Database error: {e}")
        return None


def check():
    def fetch_data(db_path, table_name):
        conn = sqlite3 .connect(db_path)
        cursor = conn .cursor()
        cursor .execute(f"SELECT * FROM {table_name}")
        data = cursor .fetchall()
        conn .close()
        return data

    def update_description(db1_data, db2_path, table_name):
        conn = sqlite3 .connect(db2_path)
        cursor = conn .cursor()

        db1_dict = {row[1]: row[2]
                    for row in db1_data}

        cursor .execute(f"SELECT * FROM {table_name}")
        db2_data = cursor .fetchall()

        for row in db2_data:
            db2_achor_id, db2_id, db2_name, db2_description, db2_extra_info = row
            if db2_name in db1_dict and db2_description != db1_dict[db2_name]:
                cursor .execute(
                    f"UPDATE {table_name} SET description = ? WHERE id = ?",
                    (db1_dict[db2_name], db2_id)
                )

        conn .commit()
        conn .close()

    def find_rows_not_in_db1(db1_data, db2_data):

        db1_set = set(tuple(row)for row in db1_data)
        db2_set = set(tuple(row)for row in db2_data)
        return list(db2_set - db1_set)

    db1_path = r"DB\latest_db_1.db"
    db2_path = r"DB\latest_db_2.db"
    table_name = "anchor_point_description"

    try:

        db1_data = fetch_data(db1_path, table_name)
        db2_data = fetch_data(db2_path, table_name)

        update_description(db1_data, db2_path, table_name)

        db2_data = fetch_data(db2_path, table_name)

        rows_in_db2_not_in_db1 = find_rows_not_in_db1(db1_data, db2_data)

        print("Rows in DB2 but not in DB1:")
        for row in rows_in_db2_not_in_db1:
            print(row)
    except sqlite3 .OperationalError as e:
        print(f"Database error: {e}")


if __name__ == "__main__":
    check()
