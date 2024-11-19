from flask import Flask ,request ,jsonify ,send_file 
from .Utils .db_shortest_path_maker import validate_and_process_start_end as get_start_end 
from .Utils .svg_manipulator import main as make_svg ,output as output_svg_location 
import os 
from flask_cors import CORS 
from .Utils .loader import env_variables 
from .Utils .db_access import get_teacher_data ,add_teacher_to_db 
from .Utils .db_maker import (
create_user_db ,
add_user ,
add_login_timestamp ,
get_all_users ,
get_login_timestamps ,
delete_user ,
)

app =Flask (__name__ )
CORS (app )


@app .route ("/load_svg",methods =["GET"])
def load_svg ():

    floor =request .args .get ("floor")
    if not floor :
        return jsonify ({"error":"Floor parameter is required"}),400 

    svg_path =os .path .join (
    env_variables ["floor_map"],f"Floor {floor } copy path.svg")
    if not os .path .exists (svg_path ):
        return jsonify ({"error":f"SVG file for floor {floor } not found"}),404 

    return send_file (svg_path ,mimetype ="image/svg+xml")


@app .route ("/load_shortest_path_svg",methods =["GET"])
def load_shortest_path_svg ():

    floor =request .args .get ("floor")
    if not floor :
        return jsonify ({"error":"Floor parameter is required"}),400 


    svg_path =output_svg_location (floor )
    if not os .path .exists (svg_path ):
        return jsonify ({"error":f"SVG file for floor {floor } not found"}),404 


    return send_file (svg_path ,mimetype ="image/svg+xml")


@app .route ("/process_path",methods =["POST"])
def process_path ():


    data =request .json 
    start =data .get ("start")
    end =data .get ("end")


    print ("Received JSON:",request .json )
    print ("Request Headers:",request .headers )


    if not start or not end :
        return jsonify ({"error":"Start and end points are required"}),400 

    try :

        start_floor_no ,end_floor_no =get_start_end (start ,end )


        input_svg_start =os .path .join (
        env_variables ["floor_map"],f"floor {start_floor_no } copy path.svg"
        )
        input_svg_end =os .path .join (
        env_variables ["floor_map"],f"floor {end_floor_no } copy path.svg"
        )
        print (
        f"Input SVG Paths: Start: {input_svg_start }, End: {input_svg_end }")


        if not os .path .exists (input_svg_start ):
            return jsonify ({"error":f"SVG file for floor {start_floor_no } not found"}),404 
        if not os .path .exists (input_svg_end ):
            return jsonify ({"error":f"SVG file for floor {end_floor_no } not found"}),404 


        print ("Processing and modifying SVGs for the path visualization")
        make_svg (start ,end )


        if start_floor_no ==end_floor_no :
            print ("Path within a single floor, returning SVG for floor",
            start_floor_no )
            output_svg =output_svg_location (start_floor_no )
            return send_file (output_svg ,mimetype ="image/svg+xml")


        print ("Path spans multiple floors, returning URLs for start and end floor SVGs")
        return jsonify ({
        "files":{
        "start_floor":f"/load_shortest_path_svg?floor={start_floor_no }",
        "end_floor":f"/load_shortest_path_svg?floor={end_floor_no }"
        }
        })
    except Exception as e :

        print ("Error occurred:",e )
        return jsonify ({"error":"An unexpected error occurred"}),500 


@app .route ("/teachers",methods =["GET","POST"])
def manage_teachers ():

    if request .method =="POST":

        data =request .get_json ()
        required_fields =["name","cabin_no",
        "room_no","phone_number","email"]


        if not data or not all (field in data for field in required_fields ):
            return jsonify ({"error":"Missing required fields"}),400 

        try :

            db_path =env_variables ["db_path"]
            add_teacher_to_db (db_path ,data )
            return jsonify ({"message":"Teacher added successfully"}),201 
        except Exception as e :
            return jsonify ({"error":str (e )}),500 

    elif request .method =="GET":

        name =request .args .get ("name")
        cabin_no =request .args .get ("cabin_no")
        room_no =request .args .get ("room_no")

        try :

            db_path =env_variables ["db_path"]
            teachers =get_teacher_data (db_path ,name ,cabin_no ,room_no )
            return jsonify (teachers ),200 
        except Exception as e :
            return jsonify ({"error":str (e )}),500 




@app .route ('/register',methods =['POST'])
def register_user ():
    data =request .json 
    username =data .get ('username')
    password =data .get ('password')

    if not username or not password :
        return jsonify ({"error":"Username and password are required"}),400 

    result =add_user (username ,password ,env_variables ["user_db_path"])
    return jsonify (result ),201 if "message"in result else 400 




@app .route ('/login',methods =['POST'])
def login_user ():
    data =request .json 
    username =data .get ('username')

    if not username :
        return jsonify ({"error":"Username is required"}),400 

    result =add_login_timestamp (username ,env_variables ["user_db_path"])
    return jsonify (result ),200 if "message"in result else 404 




@app .route ('/users',methods =['GET'])
def get_users ():
    users =get_all_users (env_variables ["user_db_path"])
    return jsonify ({"users":[{"id":user [0 ],"username":user [1 ]}for user in users ]}),200 




@app .route ('/users/<username>/timestamps',methods =['GET'])
def get_timestamps (username ):
    result =get_login_timestamps (username ,env_variables ["user_db_path"])
    if isinstance (result ,dict ):
        return jsonify (result ),404 
    return jsonify ({"timestamps":[{"id":ts [0 ],"login_time":ts [2 ]}for ts in result ]}),200 




@app .route ('/users/<username>',methods =['DELETE'])
def delete_user_route (username ):
    result =delete_user (username ,env_variables ["user_db_path"])
    return jsonify (result ),200 if "message"in result else 404 


if __name__ =="__main__":
    app .run (debug =True )
