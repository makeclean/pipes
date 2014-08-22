#!/usr/env/python

from pyne.mesh import Mesh, IMeshTag
from pyne.dagmc import load, discretize_geom, get_volume_list, point_in_volume, ray_iterator
from itaps import iMesh, iBase
from math import sqrt

"""
Given the mesh instance and a tetrahedra entity handle
determine the centroid of the tet
"""                            
def get_tet_centre(mesh,tetrahedron_eh):
    coords = mesh.getVtxCoords(tetrahedron_eh)
    print len(coords)
    return coords


""" 
DAGMC function to return the current volume id given the point
xyz
"""
def determine_volid(xyz):
    vol_list = get_volume_list()
    for vol in vol_list:
        if point_in_volume(vol,xyz) == 1:
            return vol
    return 0

"""
Step along the ray finding the midpoint and therefore then all 
point in volume for the midpoint. Then return list of all cells and the time
since start

xyz list of coordinates
direction list of direction vectors
speed list of speed since start

"""
def get_all_cells(xyz,direction,speed):
    num_of_steps = len(xyz)
    time = 0.0

    volumes = {}
    
    # loop over the substeps
    for i in range(0,num_of_steps-1):
        # find the volid of the origin
        volid = determine_volid(xyz[i])
        xcomp = (xyz[i][0]-xyz[i+1][0])**2
        ycomp = (xyz[i][1]-xyz[i+1][1])**2
        zcomp = (xyz[i][2]-xyz[i+1][2])**2
        dist_lim = sqrt(xcomp+ycomp+zcomp)

        # now do the rayfire
        for (vol,dist,surf) in ray_iterator(volid, xyz[i], direction[i],dist_limit=dist_lim):
            time += dist/speed[i]
            volumes[vol]=time

    return volumes

"""
Step along the ray finding the midpoint and therefore then all 
point in volume for the midpoint. Then return list of all cells and the time
since start

xyz list of coordinates
direction list of direction vectors
speed list of speed since start

"""
def get_all_cells_detailed(mesh,xyz,direction,speed):
    num_of_steps = len(xyz)
    time = 0.0

    volumes = {}
    
    # get the tag handle
    tag1 = mesh.getTagHandle("vol_id")

    # get all tets in the mesh set
    tets = mesh.getEntities(iBase.Type.all,iMesh.Topology.tetrahedron)

    
    # loop over the substeps
    for i in range(0,num_of_steps-1):
        # find the volid of the origin
        volid = determine_volid(xyz[i])
        xcomp = (xyz[i][0]-xyz[i+1][0])**2
        ycomp = (xyz[i][1]-xyz[i+1][1])**2
        zcomp = (xyz[i][2]-xyz[i+1][2])**2
        dist_lim = sqrt(xcomp+ycomp+zcomp)


        # now do the rayfire
        for (vol,dist,surf) in ray_iterator(volid, xyz[i], direction[i],dist_limit=dist_lim):
            time += dist/speed[i]
            volumes[vol]=time
            
        # now get the tets that have volumes tags int the dictionary


    return volumes


"""
Loads an input file containg step coordinates, directions and speeds
Returns a list of list of directions, vectors and speed
"""
def load_input_file(filename):
    xyz=[]
    direction=[]
    speed=[]

    with open(filename) as f:
        lines = f.readlines()
    f.close()

    # input data reading
    for input_line in lines:
        position = [] 
        vector = []
        if '#' not in input_line:
            split_str = input_line.split( )
            # position
            position.append(float(split_str[0]))
            position.append(float(split_str[1]))
            position.append(float(split_str[2]))
            xyz.append(position)
            # direction vector
            vector.append(float(split_str[3]))
            vector.append(float(split_str[4]))
            vector.append(float(split_str[5]))
            direction.append(vector)
            # speed
            speed.append(float(split_str[6]))

    

    return xyz,direction,speed


(xyz,direction,speed) = load_input_file("input.txt")

mesh = Mesh(mesh="../geom/conv_pipe_mesh.h5m")

# load dag geometry
load("../geom/conv_pipe_geom.h5m")

# discretise geom onto mesh
cell_fracs = discretize_geom(mesh)

mesh.vol_id = IMeshTag(1,int)
mesh.source_strength = IMeshTag(1,float)
id_list = []
for element in cell_fracs:
    id_list.append(element["cell"])

mesh.vol_id[:]=id_list

# loop along path, use point in volume to determine the vol id 
volumes = get_all_cells(xyz,direction,speed)

# loop along path, use point in volume to determine the vol id 
# but tag each tet in the range with right source strength 

dump = get_all_cells_detailed(xyz,direction,speed,mesh)

sys.exit()

# now tag all intities with the appropriate
source_strength = []
for value in mesh.vol_id[:]:
    if value in volumes.keys():
        source_strength.append(volumes[value])
    else:
        source_strength.append(0.0)

mesh.source_strength[:]=source_strength

# print the cell fracs
mesh.mesh.save("../geom/test.vtk")

