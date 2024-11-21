import xml .etree .ElementTree as ET 
from typing import List ,Tuple ,Set 
import traceback 

def process_polylines (root :ET .Element ,namespace :dict )->Tuple [Set [Tuple [float ,float ]],Set [Tuple [Tuple [float ,float ],Tuple [float ,float ]]]]:

    anchor_points =set ()
    connections =set ()


    for polyline in root .findall ('.//svg:polyline',namespace ):
        points_str =polyline .get ('points')
        if points_str :
            print (f"\nProcessing polyline: {polyline.get('id', 'unnamed')}")


            coords =points_str .strip ().split ()
            points =[]


            for i in range (0 ,len (coords ),2 ):
                try :
                    x =float (coords [i ])
                    y =float (coords [i +1 ])
                    points .append ((x ,y ))
                except (IndexError ,ValueError )as e :
                    print (f"Error parsing coordinates {coords[i:i+2]}: {e}")
                    continue 


            for i in range (len (points )):
                anchor_points .add (points [i ])
                if i <len (points )-1 :
                    connections .add ((points [i ],points [i +1 ]))

    return anchor_points ,connections 

def process_lines (root :ET .Element )->Tuple [Set [Tuple [float ,float ]],Set [Tuple [Tuple [float ,float ],Tuple [float ,float ]]]]:

    anchor_points =set ()
    connections =set ()


    for elem in root .findall ('.//*'):
        if elem .tag .endswith ('line'):
            try :
                x1 =float (elem .get ('x1',0 ))
                y1 =float (elem .get ('y1',0 ))
                x2 =float (elem .get ('x2',0 ))
                y2 =float (elem .get ('y2',0 ))

                point1 =(x1 ,y1 )
                point2 =(x2 ,y2 )

                anchor_points .add (point1 )
                anchor_points .add (point2 )
                connections .add ((point1 ,point2 ))

                print (f"\nProcessing line: {elem.get('id', 'unnamed')}")
                print (f"Points: ({x1}, {y1}) -> ({x2}, {y2})")

            except Exception as e :
                print (f"Warning: Error parsing line coordinates")
                print (f"Error: {e}")
                continue 

    return anchor_points ,connections 


from math import sqrt 
from typing import List ,Tuple 

def add_distances_to_list (
points :List [Tuple [Tuple [float ,float ],Tuple [float ,float ]]]
)->List [Tuple [Tuple [Tuple [float ,float ],Tuple [float ,float ]],float ]]:

    return [
    ((p1 ,p2 ),sqrt ((p2 [0 ]-p1 [0 ])**2 +(p2 [1 ]-p1 [1 ])**2 ))
    for p1 ,p2 in points 
    ]


def process_svg_file (filepath :str )->Tuple [list [Tuple [float ,float ]],List [Tuple [Tuple [Tuple [float ,float ],Tuple [float ,float ]],float ]]]:

    try :

        namespace ={'svg':'http://www.w3.org/2000/svg'}

        tree =ET .parse (filepath )
        root =tree .getroot ().find (".//svg:g[@id='Path']",namespace )


        polyline_points ,polyline_connections =process_polylines (root ,namespace )
        line_points ,line_connections =process_lines (root )


        all_points =polyline_points .union (line_points )
        all_connections =polyline_connections .union (line_connections )


        anchor_points_list =sorted (all_points )
        connections_list =add_distances_to_list (sorted (all_connections ))


        print ("\nAnchor Points:")
        for i ,point in enumerate (anchor_points_list ,1 ):
            print (f"{i}. ({point[0]:.2f}, {point[1]:.2f})")
        print ("\nConnections:")
        for i ,conn in enumerate (connections_list ,start =1 ):
            start_point ,end_point =conn [0 ]
            distance =conn [1 ]
            start_idx =anchor_points_list .index (start_point )+1 
            end_idx =anchor_points_list .index (end_point )+1 
            print (f"{i}. Point {start_idx} to Point {end_idx} (Distance: {distance:.2f})")
            print (f"   ({start_point[0]:.2f}, {start_point[1]:.2f}) -> ({end_point[0]:.2f}, {end_point[1]:.2f})")

        print (f"\nTotal anchor points: {len(anchor_points_list)}")
        print (f"Total connections: {len(connections_list)}")


        with open ('extracted_data.txt','w')as f :
            f .write ("Anchor Points:\n")
            for i ,point in enumerate (anchor_points_list ,1 ):
                f .write (f"{i}. ({point[0]:.2f}, {point[1]:.2f})\n")

            f .write ("\nConnections:\n")
            for i ,conn in enumerate (connections_list ,start =1 ):
                start_point ,end_point =conn [0 ]
                distance =conn [1 ]
                start_idx =anchor_points_list .index (start_point )+1 
                end_idx =anchor_points_list .index (end_point )+1 
                f .write (f"{i}. Point {start_idx} to Point {end_idx} (Distance: {distance:.2f})\n")
                f .write (f"   ({start_point[0]:.2f}, {start_point[1]:.2f}) -> ({end_point[0]:.2f}, {end_point[1]:.2f})\n")


        return anchor_points_list ,connections_list 

    except FileNotFoundError :
        print ("SVG file not found. Please check the file path.")
        return [],[]
    except ET .ParseError as e :
        print (f"Error parsing SVG file: {e}")
        return [],[]
    except Exception as e :
        print (f"An unexpected error occurred: {e}")
        traceback .print_exc ()
        return [],[]

if __name__ =="__main__":
    svg_file =r"floor 2 copy path.svg"
    process_svg_file (svg_file )