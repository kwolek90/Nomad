import xml.etree.ElementTree as ET
import numpy as np


tree = ET.parse('Trips.kml')
root = tree.getroot()

prefix = '{http://www.opengis.net/kml/2.2}'

def print_tree(root):
    for child in root:
        print(child.tag, child.attrib)
        print_tree(child)


def get_all_folders(root, folders):
    for child in root:
        if child.tag == prefix+"Folder":
            folders.append(child)
        else:
            get_all_folders(child,folders)

def get_all_placemarks(root, placemarks):
    for child in root:
        if child.tag == prefix+"Placemark":
            placemarks.append(child)
        else:
            get_all_placemarks(child,placemarks)

def difference_matrix(a):
    x = np.reshape(a, (len(a), 1))
    return x - x.transpose()
#print_tree(root)

def get_random_route(points,dist):
    route = []
    first_point = 0
    current_point = 0
    not_used_points = list(range(len(points)))
    for i in range(len(points)):
        not_used_points.remove(current_point)  
        if i == len(points) - 1:
            next_point = first_point
        else:
            next_point = np.random.choice(not_used_points)
        route.append((current_point,next_point,dist[current_point,next_point]))
        current_point = next_point
    return route

def get_optimal_randomized_route(points, dist):
    N = 10
    best_route = get_random_route(points,dist)
    best_route_dist = sum([x[2] for x in best_route])
    for i in range(N-1):
        current_route = get_random_route(points,dist)
        current_dist = sum([x[2] for x in current_route])
        if current_dist < best_route_dist:
            best_route = current_route
            best_route_dist = current_dist
    
    return best_route

def get_optimal_lacaly_route(points,dist):
    route = get_random_route(points,dist)
    
    

    return route


def get_route(points, dist):
    return get_optimal_randomized_route(points, dist)
R = 6373.0

folders = []
get_all_folders(root,folders)

s ='''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Trasa</name>
        <Style id="line-1267FF-5000-nodesc-normal">
      <LineStyle>
        <color>ffff6712</color>
        <width>5</width>
      </LineStyle>
      <BalloonStyle>
        <text><![CDATA[<h3>$[name]</h3>]]></text>
      </BalloonStyle>
    </Style>\n'''

for folder in folders:
    placemarks = []
    get_all_placemarks(folder,placemarks)
    points = []
    for placemark in placemarks:
        name = placemark.find(prefix+"name").text
        coordinates = placemark.find(prefix+"Point").find(prefix+"coordinates").text.strip()
        coordinates = [float(x) for x in coordinates.split(',')[:2]]
        points.append((name, coordinates))
    coordinates = np.array([(np.radians(x[1][0]),np.radians(x[1][1])) for x in points])
    lon = coordinates[:,0]
    lat = coordinates[:,1]
    dlon = difference_matrix(lon)
    dlat = difference_matrix(lat)

    sindlat = np.sin(dlat/2)
    sindlat = np.power(sindlat,2)
    sindlon = np.sin(dlon/2)
    sindlon = np.power(sindlon,2)
    coslat = np.cos(lat)

    a = coslat*coslat.transpose()*sindlon + sindlat
    c = 2 * np.arctan2(np.sqrt(a),np.sqrt(1-a))

    dist = R * c

    route = get_route(points,dist)

    if len(route)>1:
        s+='    <Placemark>\n'
        s+='      <name>Trasa dla '+folder.find(prefix+"name").text+'</name>\n'
        s+='      <styleUrl>#line-1267FF-5000-nodesc</styleUrl>\n'
        s+='      <LineString>\n'
        s+='        <tessellate>1</tessellate>\n'
        s+='        <coordinates>\n'
        s+='\n'.join(['           {0:.7f},{1:.7f},0'.format(points[x[0]][1][0],points[x[0]][1][1]) for x in route])
        s+='\n           {0:.7f},{1:.7f},0\n'.format(points[route[0][0]][1][0],points[route[0][0]][1][1])
        s+='        </coordinates>\n'
        s+='      </LineString>\n'
        s+='    </Placemark>\n'
    print(route)
    print(sum([x[2] for x in route]))

    for point in points:
        print(point[0], point[1])


s+='''  </Document>
</kml>
'''

f = open('test.kml','w+')
f.write(s)
f.close()
print(s)