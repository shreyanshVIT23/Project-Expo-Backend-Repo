from .import db_shortest_path_maker 
from lxml import etree as ET 
from .import loader 
import os 

def modify_svg (svg_file ,output_file ,path_points ):

    break_polyline_to_lines (svg_file ,output_file )

    tree =ET .parse (output_file )
    root =tree .getroot ()
    NS ={"svg":"http://www.w3.org/2000/svg"}


    create_arrow_with_angle (root ,path_points [-2 ],path_points [-1 ])


    for line in root .xpath ("//svg:line",namespaces =NS ):
        if 'class'in line .attrib :
            del line .attrib ['class']
        modify_line (line ,path_points )


    with open (output_file ,"wb")as f :
        tree .write (f ,pretty_print =True ,xml_declaration =True ,encoding ="utf-8")


def break_polyline_to_lines (svg_file ,output_file ):


    parser =ET .XMLParser (remove_blank_text =True )
    tree =ET .parse (svg_file ,parser )
    root =tree .getroot ()
    namespace ={'svg':'http://www.w3.org/2000/svg'}


    for polyline in root .xpath ('.//svg:polyline',namespaces =namespace ):
        points =polyline .attrib .get ('points','').strip ()
        if points :

            coords =[float (c )for c in points .replace (',',' ').split ()]
            point_pairs =[(coords [i ],coords [i +1 ])
            for i in range (0 ,len (coords ),2 )]


            parent =polyline .getparent ()
            if parent is None :
                raise ValueError ("Parent element not found for the polyline")


            for i in range (len (point_pairs )-1 ):
                x1 ,y1 =point_pairs [i ]
                x2 ,y2 =point_pairs [i +1 ]
                line =ET .Element ('line',{
                'x1':str (x1 ),
                'y1':str (y1 ),
                'x2':str (x2 ),
                'y2':str (y2 ),
                'stroke':'black',
                'stroke-width':'1'
                })
                parent .insert (parent .index (polyline ),line )


            parent .remove (polyline )


    tree .write (output_file ,pretty_print =True ,xml_declaration =True ,encoding ='utf-8')


def create_arrow_with_angle (svg_root ,start_point ,end_point ,arrow_id ="dynamic-arrow"):

    namespace ={'svg':'http://www.w3.org/2000/svg'}


    defs =svg_root .find ('svg:defs',namespaces =namespace )
    if defs is None :
        defs =ET .SubElement (svg_root ,'defs')


    marker =defs .find (f".//svg:marker[@id='{arrow_id }']",namespaces =namespace )
    if marker is None :
        marker =ET .SubElement (defs ,'marker',{
        'id':arrow_id ,
        'markerWidth':'10',
        'markerHeight':'10',
        'refX':'0',
        'refY':'3',
        'orient':'auto',
        'markerUnits':'strokeWidth'
        })
        arrow_path =ET .SubElement (marker ,'path',{
        'd':'M0,0 L0,6 L9,3 z',
        'fill':'red'
        })


    x1 ,y1 =start_point 
    x2 ,y2 =end_point 

    arrow_line =ET .Element ('line',{
    'x1':str (x1 ),
    'y1':str (y1 ),
    'x2':str (x2 ),
    'y2':str (y2 ),
    'stroke':'red',
    'stroke-width':'0.8',
    'marker-end':f'url(#{arrow_id })'
    })


    svg_root .append (arrow_line )


def modify_line (line ,path_points ):

    def is_point_in_path (point ,path_points ,tolerance =1e-6 ):

        x ,y =point 
        return any (abs (float (x )-px )<tolerance and abs (float (y )-py )<tolerance for px ,py in path_points )


    try :
        x1 ,y1 =float (line .get ("x1")),float (line .get ("y1"))
        x2 ,y2 =float (line .get ("x2")),float (line .get ("y2"))
    except (ValueError ,TypeError )as e :
        raise ValueError ("Invalid line coordinates: 'x1', 'y1', 'x2', and 'y2' must be valid numbers.")from e 

    start_point =(x1 ,y1 )
    end_point =(x2 ,y2 )


    start_in_path =is_point_in_path (start_point ,path_points )
    end_in_path =is_point_in_path (end_point ,path_points )

    if start_in_path and end_in_path :

        line .set ("visibility","visible")
        line .set ("stroke","red")
        if is_point_in_path (end_point ,[path_points [-1 ]]):
            line .set ("marker-end","url(#arrowhead)")
    else :

        line .set ("visibility","hidden")


def output (val :int ):
    return os .path .join (loader .env_variables ["output_map"],f"floor {val } shortest path.svg")

def floor_svg (val :int ):
    return os .path .join (loader .env_variables ["floor_map"],f"floor {val } copy path.svg")


def main (start :str ,end :str ):

    msb_start ,msb_end =db_shortest_path_maker .validate_and_process_start_end (start ,end )
    db_path =loader .env_variables ["db_path"]
    shortest_path =db_shortest_path_maker .main (db_path =db_path ,start_description =start ,end_description =end )
    if shortest_path [2 ]=="complex":
        modify_svg (floor_svg (msb_start ),output (msb_start ),shortest_path [0 ][0 ][1 ])
        modify_svg (floor_svg (msb_end ),output (msb_end ),shortest_path [0 ][1 ][1 ])
    elif shortest_path [2 ]=="simple":
        modify_svg (floor_svg (msb_start ),output (msb_end ),shortest_path [0 ])


if __name__ =="__main__":
    main ("215","407")