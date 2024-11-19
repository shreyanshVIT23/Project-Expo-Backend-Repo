import sqlite3 
from typing import List ,Dict ,Any 

def get_coordinates (db_path ,description_condition ,floor_condition ):

    try :
        with sqlite3 .connect (db_path )as conn :
            cursor =conn .cursor ()
            query ="""
                SELECT apc.x_coordinate, apc.y_coordinate
                FROM anchor_point_coordinates apc
                JOIN anchor_point_description apd ON apc.id = apd.anchor_point_id
                WHERE apd.description LIKE ? AND apc.floor = ?
            """
            cursor .execute (query ,(description_condition ,floor_condition ))
            return cursor .fetchall ()
    except sqlite3 .Error as e :
        print (f"Database error: {e}")
    except Exception as e :
        print (f"Error: {e}")
    return None 


def get_description (db_path ,coordinates ,floor_condition ):

    try :
        with sqlite3 .connect (db_path )as conn :
            cursor =conn .cursor ()
            query ="""
                SELECT apd.description
                FROM anchor_point_coordinates apc
                JOIN anchor_point_description apd ON apc.id = apd.anchor_point_id
                WHERE apc.x_coordinate = ? AND apc.y_coordinate = ? AND apc.floor = ?
            """
            cursor .execute (query ,(*coordinates ,floor_condition ))
            return [row [0 ]for row in cursor .fetchall ()]
    except sqlite3 .Error as e :
        print (f"Database error: {e}")
    except Exception as e :
        print (f"Error: {e}")
    return None 


def get_teacher_data (db_path :str ,name :str =None ,cabin_no :str =None ,room_no :str =None )->List [Dict [str ,Any ]]:

    query ="SELECT name, cabin_no, room_no, phone_number, email FROM teachers WHERE 1=1"
    params =[]

    if name :
        query +=" AND name LIKE ?"
        params .append (f"%{name}%")
    if cabin_no :
        query +=" AND cabin_no = ?"
        params .append (cabin_no )
    if room_no :
        query +=" AND room_no = ?"
        params .append (room_no )

    try :
        with sqlite3 .connect (db_path )as conn :
            cursor =conn .cursor ()
            cursor .execute (query ,params )
            result =cursor .fetchall ()

        return [
        {
        "name":row [0 ],
        "cabin_no":row [1 ],
        "room_no":row [2 ],
        "phone_number":row [3 ],
        "email":row [4 ]
        }
        for row in result 
        ]
    except sqlite3 .Error as e :
        raise Exception (f"Database error: {e}")

def add_teacher_to_db (db_path :str ,data :Dict [str ,Any ]):

    try :
        with sqlite3 .connect (db_path )as conn :
            cursor =conn .cursor ()
            cursor .execute ("""
                INSERT INTO teachers (name, cabin_no, room_no, phone_number, email)
                VALUES (?, ?, ?, ?, ?);
            """,(data ["name"],data ["cabin_no"],data ["room_no"],data ["phone_number"],data ["email"]))
            conn .commit ()
    except sqlite3 .Error as e :
        raise Exception (f"Database error: {e}")