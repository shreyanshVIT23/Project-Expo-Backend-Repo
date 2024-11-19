import sqlite3 
from .import db_access 
from .import graph_converter 
from .import loader 

class AmbiguousValueError (Exception ):

    pass 

def get_msb (description :str )->int :


    digits =''.join (filter (str .isdigit ,description ))


    return int (digits [0 ])if digits else None 


def is_valid_digit (description :str )->bool :

    digits =''.join (filter (str .isdigit ,description ))
    return len (digits )>0 and len (digits )<=3 


def validate_and_process_start_end (start :str ,end :str ):


    msb_start =get_msb (start )
    msb_end =get_msb (end )


    if not is_valid_digit (start )and not is_valid_digit (end ):
        if msb_start is None and msb_end is None :
            raise AmbiguousValueError ("Both `start` and `end` are invalid or non-digit descriptions.")
        elif msb_start is None :
            msb_start =msb_end 
        elif msb_end is None :
            msb_end =msb_start 
    elif not is_valid_digit (start ):
        msb_start =msb_end 
        if msb_start is None :
            raise AmbiguousValueError ("Cannot derive MSB from `end` as it is invalid.")
    elif not is_valid_digit (end ):
        msb_end =msb_start 
        if msb_end is None :
            raise AmbiguousValueError ("Cannot derive MSB from `start` as it is invalid.")


    if msb_start !=msb_end :
        if start .isalpha ()or " "in start :
            msb_start =msb_end 
        elif end .isalpha ()or " "in end :
            msb_end =msb_start 


    if msb_start is None or msb_end is None :
        raise AmbiguousValueError ("Invalid MSB values derived from input.")


    if start .isdigit ()and len (start )>3 :
        raise AmbiguousValueError ("Digit length of `start` exceeds the allowed limit (3).")
    if end .isdigit ()and len (end )>3 :
        raise AmbiguousValueError ("Digit length of `end` exceeds the allowed limit (3).")

    return msb_start ,msb_end 

def get_exact_node (graph ,coordinates ):

    for node ,data in graph .nodes (data =True ):
        if data ['x']==coordinates [0 ]and data ['y']==coordinates [1 ]:
            return node 
    print ("Exact node not found for the given coordinates.")
    return None 


def interpret_path (graph ,path ):

    return [(graph .nodes [node ]['x'],graph .nodes [node ]['y'])for node in path ]


def handle_different_msb (db_path ,start ,end ,msb_start ,msb_end ):


    graph =graph_converter .create_graph_from_db (db_path )


    lifts_stairs_start =(
    db_access .get_coordinates (db_path ,"Lift %",msb_start )
    +db_access .get_coordinates (db_path ,"Stairs %",msb_start )
    )
    if not lifts_stairs_start :
        raise AmbiguousValueError (f"No lifts or stairs found on floor {msb_start }.")


    shortest_path_to_lift =None 
    min_weight =float ("inf")
    lift_description =None 

    for lift in lifts_stairs_start :
        lift_node =get_exact_node (graph ,lift )
        start_coords =db_access .get_coordinates (db_path ,start ,msb_start )
        if not start_coords :
            raise AmbiguousValueError (f"Start location '{start }' not found on floor {msb_start }.")
        start_node =get_exact_node (graph ,start_coords [0 ])

        path ,weight =graph_converter .find_shortest_path (graph ,start_node ,lift_node )
        if weight <min_weight :
            min_weight =weight 
            shortest_path_to_lift =path 
            lift_description =lift 


    lift_description =db_access .get_description (db_path ,lift_description ,msb_start )


    lift_floor_coords =db_access .get_coordinates (db_path ,lift_description [0 ],msb_end )
    if not lift_floor_coords :
        raise AmbiguousValueError (f"Matching lift/stair '{lift_description }' not found on floor {msb_end }.")


    lift_node_end =get_exact_node (graph ,lift_floor_coords [0 ])
    end_coords =db_access .get_coordinates (db_path ,end ,msb_end )
    if not end_coords :
        raise AmbiguousValueError (f"End location '{end }' not found on floor {msb_end }.")
    end_node =get_exact_node (graph ,end_coords [0 ])

    shortest_path_from_lift ,weight_from_lift =graph_converter .find_shortest_path (
    graph ,lift_node_end ,end_node 
    )


    combined_path =[
    [msb_start ,interpret_path (graph ,shortest_path_to_lift )],
    [msb_end ,interpret_path (graph ,shortest_path_from_lift )],
    ]
    total_weight =min_weight +weight_from_lift 

    return combined_path ,total_weight ,"complex"



def main (start_description ,end_description ,db_path =loader .env_variables ["db_path"]):

    try :

        msb_start ,msb_end =validate_and_process_start_end (start_description ,end_description )
    except AmbiguousValueError as e :
        print (f"Validation Error: {e }")
        return None 


    graph =graph_converter .create_graph_from_db (db_path )

    if msb_start ==msb_end :

        try :

            start_coordinates =db_access .get_coordinates (db_path ,start_description ,msb_start )
            end_coordinates =db_access .get_coordinates (db_path ,end_description ,msb_end )

            if not start_coordinates :
                raise AmbiguousValueError (f"Start location '{start_description }' not found on floor {msb_start }.")
            if not end_coordinates :
                raise AmbiguousValueError (f"End location '{end_description }' not found on floor {msb_end }.")


            start_node =get_exact_node (graph ,start_coordinates [0 ])
            end_node =get_exact_node (graph ,end_coordinates [0 ])

            if start_node is None or end_node is None :
                raise AmbiguousValueError ("Could not determine start or end node in the graph.")


            shortest_path ,weight =graph_converter .find_shortest_path (graph ,start_node ,end_node )
            return interpret_path (graph ,shortest_path ),weight ,"simple"
        except AmbiguousValueError as e :
            print (f"Pathfinding Error: {e }")
            return None 
    else :

        try :
            return handle_different_msb (db_path ,start_description ,end_description ,msb_start ,msb_end )
        except AmbiguousValueError as e :
            print (f"Cross-Floor Pathfinding Error: {e }")
            return None 

def example ():
    start_description ="407"
    end_description ="206"
    result =main (start_description ,end_description ,loader .env_variables ["db_path"])
    if result :
        path ,weight =result 
        print (f"Combined Path: {path }")
        print (f"Total Path Weight: {weight }")
    return result 

if __name__ =="__main__":
    example ()
