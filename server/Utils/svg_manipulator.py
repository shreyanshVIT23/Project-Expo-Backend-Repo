from .import db_shortest_path_maker
from lxml import etree as ET
from .import loader
import os


def modify_svg(svg_file, output_file, path_points):

    break_polyline_to_lines(svg_file, output_file)

    tree = ET .parse(output_file)
    root = tree .getroot()
    NS = {"svg": "http://www.w3.org/2000/svg"}

    create_arrow_with_image(
        root, path_points[-2], path_points[-1], image_href=loader .env_variables["image_assets"])

    for line in root .xpath("//svg:g[@id='Path']/svg:line", namespaces=NS):
        if 'class' in line .attrib:
            del line .attrib['class']
        modify_line(line, path_points)

    g_element = root .find(".//svg:g[@id='Path']", namespaces=NS)

    if g_element is not None and 'class' in g_element .attrib:
        del g_element .attrib['class']

    with open(output_file, "wb")as f:
        tree .write(f, pretty_print=True,
                    xml_declaration=True, encoding="utf-8")

    return output_file


def parse_svg_text(svg_file):

    tree = ET .parse(svg_file)
    root = tree .getroot()
    nsmap = {'svg': 'http://www.w3.org/2000/svg'}

    text_data = []
    for text_element in root .findall(".//svg:text", namespaces=nsmap):
        transform = text_element .get("transform", "")
        if "translate" in transform:

            coords = transform .split("translate(")[1].split(")")[0].split()
            x1, y1 = float(coords[0]), float(coords[1])

            tspan = text_element .find("svg:tspan", namespaces=nsmap)
            if tspan is not None:
                text_content = tspan .text
                text_data .append((text_content, x1, y1))
    return text_data


def break_polyline_to_lines(svg_file, output_file):

    parser = ET .XMLParser(remove_blank_text=True)
    tree = ET .parse(svg_file, parser)
    root = tree .getroot()
    namespace = {'svg': 'http://www.w3.org/2000/svg'}

    for polyline in root .xpath('.//svg:polyline', namespaces=namespace):
        points = polyline .attrib .get('points', '').strip()
        if points:

            coords = [float(c)for c in points .replace(',', ' ').split()]
            point_pairs = [(coords[i], coords[i + 1])
                           for i in range(0, len(coords), 2)]

            parent = polyline .getparent()
            if parent is None:
                raise ValueError("Parent element not found for the polyline")

            for i in range(len(point_pairs)-1):
                x1, y1 = point_pairs[i]
                x2, y2 = point_pairs[i + 1]
                line = ET .Element('line', {
                    'x1': str(x1),
                    'y1': str(y1),
                    'x2': str(x2),
                    'y2': str(y2),
                    'stroke': 'black',
                    'stroke-width': '1'
                })
                parent .insert(parent .index(polyline), line)

            parent .remove(polyline)

    tree .write(output_file, pretty_print=True,
                xml_declaration=True, encoding='utf-8')


def create_arrow_with_image(svg_root, start_point, end_point, arrow_id="dynamic-arrow", image_href=None):

    nsmap = svg_root .nsmap
    svg_ns = nsmap .get(None, 'http://www.w3.org/2000/svg')
    xlink_ns = nsmap .get(
        'xlink', 'http://www.w3.org/1999/xlink')

    defs = svg_root .find(f"{{{svg_ns}}}defs")
    if defs is None:
        defs = ET .SubElement(svg_root, f"{{{svg_ns}}}defs")

    def create_marker(defs, arrow_id, image_href=None, marker_width=10, marker_height=10):

        svg_ns = "http://www.w3.org/2000/svg"
        xlink_ns = "http://www.w3.org/1999/xlink"

        marker = defs .find(f".//{{{svg_ns}}}marker[@id='{arrow_id}']")
        if marker is None:

            marker = ET .SubElement(defs, f"{{{svg_ns}}}marker", {
                'id': arrow_id,
                'markerWidth': str(marker_width),
                'markerHeight': str(marker_height),
                'refX': str(marker_width / 2),
                'refY': str(marker_height),
                'markerUnits': 'strokeWidth',
            })

            if image_href:

                ET .SubElement(marker, f"{{{svg_ns}}}image", {
                    f"{{{xlink_ns}}}href": image_href,
                    'x': '0',
                    'y': '0',
                    'width': str(marker_width),
                    'height': str(marker_height),
                    'preserveAspectRatio': 'xMidYMid meet',
                })
            else:

                ET .SubElement(marker, f"{{{svg_ns}}}path", {
                    'd': 'M0,0 L0,10 L10,5 z',
                    'fill': 'red',
                    'orient': 'auto'
                })

        return marker

    create_marker(
        defs, arrow_id, image_href=loader .env_variables["image_assets"], marker_width=20, marker_height=20)

    x1, y1 = start_point
    x2, y2 = end_point

    arrow_line = ET .Element(f"{{{svg_ns}}}line", {
        'x1': str(x1),
        'y1': str(y1),
        'x2': str(x2),
        'y2': str(y2),
        'stroke': 'red',
        'stroke-width': '0.8',
        'marker-end': f'url(#{arrow_id})'
    })

    svg_root .append(arrow_line)


def modify_line(line, path_points):

    def is_point_in_path(point, path_points, tolerance=1e-6):

        x, y = point
        return any(abs(float(x)-px) < tolerance and abs(float(y)-py) < tolerance for px, py in path_points)

    try:
        x1, y1 = float(line .get("x1")), float(line .get("y1"))
        x2, y2 = float(line .get("x2")), float(line .get("y2"))
    except (ValueError, TypeError)as e:
        raise ValueError(
            "Invalid line coordinates: 'x1', 'y1', 'x2', and 'y2' must be valid numbers.")from e

    start_point = (x1, y1)
    end_point = (x2, y2)

    start_in_path = is_point_in_path(start_point, path_points)
    end_in_path = is_point_in_path(end_point, path_points)

    if start_in_path and end_in_path:

        line .set("visibility", "visible")
        line .set("stroke", "red")

        if is_point_in_path(end_point, [path_points[-1]]):

            line .set("marker-end", "url(#arrowhead)")
    else:

        line .set("visibility", "hidden")


def output(val: int):
    return os .path .join(loader .env_variables["output_map"], f"floor {val} shortest path.svg")


def floor_svg(val: int):
    return os .path .join(loader .env_variables["floor_map"], f"floor {val} copy path.svg")


def main(start: str, end: str, preference: str = None):

    db_path = loader .env_variables["db_path"]

    shortest_path = db_shortest_path_maker .main(
        db_path=db_path, start_description=start, end_description=end, preference=preference
    )

    svg_updates = []

    if shortest_path["complexity"] == "complex":
        msb_start = shortest_path['path'][0][0]
        msb_end = shortest_path['path'][1][0]

        svg_start = modify_svg(floor_svg(msb_start), output(
            msb_start), shortest_path["path"][0][1])
        svg_end = modify_svg(floor_svg(msb_end), output(
            msb_end), shortest_path["path"][1][1])
        svg_updates .extend([svg_start, svg_end])
    elif shortest_path["complexity"] == "simple":

        msb_start = shortest_path['path'][0]
        svg_start = modify_svg(floor_svg(msb_start), output(
            msb_start), shortest_path["path"][1])
        svg_updates .append(svg_start)
    return {
        "path": shortest_path["path"],
        "total_weight": shortest_path["total_weight"],
        "complexity": shortest_path["complexity"],
        "svg_updates": svg_updates,
        "error": shortest_path["error"],
    }


if __name__ == "__main__":
    print(main("T404", "Library", "Lift"))
