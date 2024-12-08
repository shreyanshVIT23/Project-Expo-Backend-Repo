import pandas as pd
import sqlite3
from . import db_maker, loader
import re


def validate_room_no(cursor, room_no):

    cursor.execute(
        """
        SELECT 1 
        FROM anchor_point_description 
        WHERE TRIM(extra_info) = ? 
    """,
        (room_no,),
    )
    return cursor.fetchone() is not None


def transform_room_no(original_room_no):

    match = re.match(r".*-(\d+)([A-Za-z]*)$", original_room_no)

    if match:
        room_no = match.group(1)
        section_no = match.group(2)
        if section_no:
            return f"T{room_no}({section_no.upper()})"
        else:
            return f"T{room_no}"
    return None


def excel_to_sqlite(excel_file, db_file):

    try:
        df = pd.read_excel(excel_file)
        print("Excel file read successfully!")
    except Exception as e:
        print("Error reading Excel file:", e)
        return

    required_columns = ["Room No.", "Cabin No.", "Name", "Mobile No.", "Status"]
    if not all(col in df.columns for col in required_columns):
        print(f"Missing required columns. Ensure the file has: {required_columns}")
        return

    df = df[required_columns]
    df.rename(
        columns={
            "Room No.": "room_no",
            "Cabin No.": "cabin_no",
            "Name": "name",
            "Mobile No.": "phone_number",
        },
        inplace=True,
    )

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cabin_no TEXT,
            room_no TEXT,
            phone_number TEXT,
            FOREIGN KEY (room_no) REFERENCES anchor_point_description (name)
        )
        """
        )
        print("Database connected and table ensured!")

    except Exception as e:
        print("Error connecting to the database:", e)
        return

    try:
        for _, row in df.iterrows():
            original_room_no = row["room_no"]
            transformed_room_no = transform_room_no(original_room_no)

            if not transformed_room_no:
                print(f"Skipping invalid room number format: {original_room_no}")
                continue

            if not validate_room_no(cursor, transformed_room_no):
                print(
                    f"Skipping room number not found in anchor_point_description: {transformed_room_no}"
                )
                continue

            cursor.execute(
                """
            INSERT INTO teachers (name, cabin_no, room_no, phone_number)
            VALUES (?, ?, ?, ?)
            """,
                (
                    row["name"],
                    row["cabin_no"],
                    transformed_room_no,
                    row["phone_number"],
                ),
            )

        conn.commit()
        print("Data inserted successfully into the database!")
    except Exception as e:
        print("Error inserting data into the database:", e)
    finally:
        conn.close()


def test():
    excel_file = loader.env_variables["teacher_data"]
    db_file = loader.env_variables["db_path"]
    excel_to_sqlite(excel_file, db_file)


if __name__ == "__main__":
    test()
