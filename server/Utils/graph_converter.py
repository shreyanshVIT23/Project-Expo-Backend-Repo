import networkx as nx 
from typing import List ,Tuple 
from .import extractor 
import sqlite3 

def create_graph_from_svg_data (anchor_points :List [Tuple [float ,float ]],
connections :List [Tuple [Tuple [Tuple [float ,float ],Tuple [float ,float ]],float ]])->nx .Graph :

    G =nx .Graph ()


    for point in anchor_points :
        G .add_node (point )


    for connection in connections :
        (point1 ,point2 ),weight =connection 
        G .add_edge (point1 ,point2 ,weight =weight )

    return G 

def create_graph_from_db (db_path ):


    conn =sqlite3 .connect (db_path )
    cursor =conn .cursor ()


    cursor .execute ("SELECT id, x_coordinate, y_coordinate FROM anchor_point_coordinates")
    nodes =cursor .fetchall ()


    cursor .execute ("SELECT point_a_id, point_b_id, distance FROM connections")
    edges =cursor .fetchall ()


    G =nx .Graph ()


    for node in nodes :
        node_id ,x ,y =node 
        G .add_node (node_id ,x =x ,y =y )


    for edge in edges :
        point_a_id ,point_b_id ,distance =edge 
        G .add_edge (point_a_id ,point_b_id ,weight =distance )


    conn .close ()

    return G 


import networkx as nx 
from typing import List ,Tuple 

def find_shortest_path (graph :nx .Graph ,start :Tuple [float ,float ],end :Tuple [float ,float ])->Tuple [List [Tuple [float ,float ]],float ]:

    try :

        path =nx .dijkstra_path (graph ,source =start ,target =end ,weight ='weight')

        total_weight =nx .dijkstra_path_length (graph ,source =start ,target =end ,weight ='weight')
        return path ,total_weight 
    except nx .NetworkXNoPath :
        print (f"No path found between {start } and {end }.")
        return [],float ('inf')



def example ():
    filepath =r"floor 2 copy path.svg"
    anchor_points ,connections =extractor .process_svg_file (filepath )
    graph =create_graph_from_svg_data (anchor_points ,connections )


    start_point =(153.2 ,360.6 )
    end_point =(430.7 ,234.5 )


    shortest_path ,weight =find_shortest_path (graph ,start_point ,end_point )


    print ("Shortest path:",shortest_path ,"Weight:",weight )
    return shortest_path ,filepath 

if __name__ =="__main__":
    example ()