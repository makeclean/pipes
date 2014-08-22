#!/usr/env/python

from pyne.mesh import Mesh,IMeshTag
from itaps import iBase,iMesh

def get_tet_centre(mesh,tetrahedron_eh):
    coords = mesh.getVtxCoords(tetrahedron_eh)
    print len(coords)
    return coords
    
# new instance
mesh = iMesh.Mesh()

# load the mesh
mesh.load("../geom/test.vtk")

# get tag handle
#tag1 = mesh.createTag("vol_id",1,int)
tag1 = mesh.getTagHandle("vol_id")

# tets
tets = mesh.getEntities(iBase.Type.all,iMesh.Topology.tetrahedron)

tet_w_val = []
# get all tets with tag value of a given value
for tet in tets:
    if ( tag1[tet] == 31 ):
        tet_w_val.append(tet)
        tc = get_tet_centre(mesh,tet)
        print tc

print len(tets), len(tet_w_val)
#print tag1[tets]
#print len(tets)


