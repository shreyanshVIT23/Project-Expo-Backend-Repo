import sqlite3 
import re 
from typing import List ,Tuple 
from .import loader 
from datetime import datetime 

def create_database (cursor ):
    cursor .execute ("""
        CREATE TABLE IF NOT EXISTS anchor_point_coordinates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            x_coordinate REAL NOT NULL,
            y_coordinate REAL NOT NULL,
            floor INTEGER
        );
    """)

    cursor .execute ("""
        CREATE TABLE IF NOT EXISTS anchor_point_description (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anchor_point_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            extra_info TEXT,
            FOREIGN KEY (anchor_point_id) REFERENCES anchor_point_coordinates (id)
        );
    """)


    cursor .execute ("""
    CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        point_a_id INTEGER NOT NULL,
        point_b_id INTEGER NOT NULL,
        distance REAL NOT NULL,
        FOREIGN KEY (point_a_id) REFERENCES anchor_points (id),
        FOREIGN KEY (point_b_id) REFERENCES anchor_points (id)
    );
    """)



    print ("Database and tables created successfully.")


def create_teachers_database (cursor ):


    cursor .execute ("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cabin_no TEXT NOT NULL,
            room_no TEXT NOT NULL,
            phone_number TEXT,
            email TEXT,
            FOREIGN KEY (room_no) REFERENCES anchor_point_description (name)
        );
    """)

    print ("Teachers database and table created successfully.")


def insert_coordinates (coordinates ,cursor ,floor ):


    for x ,y in coordinates :
        cursor .execute ("""
            INSERT INTO anchor_point_coordinates (x_coordinate, y_coordinate, floor)
            VALUES (?, ?, ?)
        """,(x ,y ,floor ))

    print (f"{len(coordinates)} coordinates inserted successfully into the anchor_point_coordinates table.")

def insert_descriptions_from_connections (
connections :List [Tuple [Tuple [Tuple [float ,float ],Tuple [float ,float ]],float ]],cursor 
):


    all_coordinates =[]
    for connection in connections :
        (point_a ,point_b ),_ =connection 
        all_coordinates .append (point_a )
        all_coordinates .append (point_b )


    coordinate_count ={}
    for coord in all_coordinates :
        coordinate_count [coord ]=coordinate_count .get (coord ,0 )+1 


    unique_coordinates =[coord for coord ,count in coordinate_count .items ()if count ==1 ]

    if not unique_coordinates :
        print ("No unique coordinates found.")
        return 


    unique_point_ids =[]
    for x ,y in unique_coordinates :

        cursor .execute (
        "SELECT id FROM anchor_point_coordinates WHERE x_coordinate = ? AND y_coordinate = ?",
        (x ,y ),
        )
        result =cursor .fetchone ()

        if result :
            point_id =result [0 ]
        else :

            cursor .execute (
            "INSERT INTO anchor_point_coordinates (x_coordinate, y_coordinate) VALUES (?, ?)",
            (x ,y ),
            )
            point_id =cursor .lastrowid 

        unique_point_ids .append ((point_id ,x ,y ))


    for anchor_id ,x ,y in unique_point_ids :
        cursor .execute (
        """
            INSERT INTO anchor_point_description (anchor_point_id, name, description, extra_info)
            VALUES (?, ?, ?, ?)
            """,
        (anchor_id ,f"Anchor at ({x}, {y})","Unique anchor point","Auto-generated description"),
        )

    print (f"{len(unique_point_ids)} unique anchor points inserted into anchor_point_description.")


def insert_connections (connections ,cursor ):


    cursor .execute ("SELECT id, x_coordinate, y_coordinate FROM anchor_point_coordinates")
    anchor_points =cursor .fetchall ()


    coordinate_to_id ={
    (row [1 ],row [2 ]):row [0 ]for row in anchor_points 
    }


    for (start_point ,end_point ),distance in connections :

        point_a_id =coordinate_to_id .get (start_point )
        point_b_id =coordinate_to_id .get (end_point )

        if point_a_id and point_b_id :
            cursor .execute ("""
                INSERT INTO connections (point_a_id, point_b_id, distance)
                VALUES (?, ?, ?)
            """,(point_a_id ,point_b_id ,distance ))
        else :
            print (f"Skipping connection: ({start_point}, {end_point}) - IDs not found")

    print (f"{len(connections)} connections inserted successfully into the connections table.")

def process_svg_data (svg_file ,coordinates ,connections ,db_path ):


    with sqlite3 .connect (db_path )as conn :
        cursor =conn .cursor ()


        create_database (cursor )


        floor_number =int (re .findall (r'\d',svg_file )[0 ])


        insert_coordinates (coordinates ,cursor ,floor_number )
        insert_connections (connections ,cursor )
        insert_descriptions_from_connections (connections ,cursor )




def create_user_db (db_path ):
    with sqlite3 .connect (db_path )as conn :
        cursor =conn .cursor ()


        cursor .execute ("PRAGMA foreign_keys = ON;")


        cursor .execute ("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """)


        cursor .execute ("""
        CREATE TABLE IF NOT EXISTS login_timestamps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """)



def add_user (username ,password ,db_path ):
    try :
        with sqlite3 .connect (db_path )as conn :
            cursor =conn .cursor ()

            cursor .execute ("INSERT INTO users (username, password) VALUES (?, ?)",(username ,password ))
            conn .commit ()
            return {"message":f"User '{username}' added successfully."}
    except sqlite3 .IntegrityError :

        return {"error":f"Username '{username}' already exists."}
    except Exception as e :

        return {"error":str (e )}


def add_login_timestamp (username ,db_path ):
    try :
        with sqlite3 .connect (db_path )as conn :
            cursor =conn .cursor ()


            cursor .execute ("SELECT id FROM users WHERE username = ?",(username ,))
            user =cursor .fetchone ()

            if user :
                user_id =user [0 ]
                timestamp =datetime .now ().isoformat ()
                cursor .execute (
                "INSERT INTO login_timestamps (user_id, login_time) VALUES (?, ?)",
                (user_id ,timestamp )
                )
                conn .commit ()
                return {"message":f"Login timestamp for user '{username}' added at {timestamp}."}
            else :
                return {"error":f"User '{username}' not found."}
    except Exception as e :

        return {"error":str (e )}


def get_all_users (db_path ):
    with sqlite3 .connect (db_path )as conn :
        cursor =conn .cursor ()
        cursor .execute ("SELECT * FROM users;")
        return cursor .fetchall ()



def get_login_timestamps (username ,db_path ):
    with sqlite3 .connect (db_path )as conn :
        cursor =conn .cursor ()

        cursor .execute ("SELECT id FROM users WHERE username = ?",(username ,))
        user =cursor .fetchone ()

        if user :
            user_id =user [0 ]
            cursor .execute ("SELECT * FROM login_timestamps WHERE user_id = ?",(user_id ,))
            return cursor .fetchall ()
        else :
            print (f"Error: User '{username}' not found.")
            return []



def delete_user (username ,db_path ):
    with sqlite3 .connect (db_path )as conn :
        cursor =conn .cursor ()
        cursor .execute ("DELETE FROM users WHERE username = ?",(username ,))
        if cursor .rowcount >0 :
            return {"message":f"User '{username}' and their login timestamps have been deleted."}
        return {"error":f"User '{username}' not found."}










































if __name__ =="__main__":
    with sqlite3 .connect (loader .env_variables ["db_path"])as cursor :
        create_teachers_database (cursor )








