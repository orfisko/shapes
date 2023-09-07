from _decimal import Decimal

from source.panel_shapes import generate_panel_shapes
from source.geometry import *
from source.utils import *

import math

def test_panel_generation(polyhedron_cutout_sloped):
    outer = polyhedron_cutout_sloped()
    inner = outer.apply_offset(offset=Decimal(-10))
    def prioritize(face_indices):
        #0 - horizontal
        #1 - side
        #2 - front/back
        #3 - sloped
        types=[]
        for face_index in face_indices:
            normal=outer.faces[face_index].compute_plane().normal
            if math.fabs(normal.y)>normal.length()*0.99:
                types.append(0)
            elif math.fabs(normal.x)>normal.length()*0.99:
                types.append(1)
            elif math.fabs(normal.z)>normal.length()*0.99:
                types.append(2)
            else:
                types.append(3)
        priorities=[]
        for type in types:
            if type==0:
                priorities.append(3)
            elif type==1:
                priorities.append(2)
            elif type==2:
                priorities.append(1)
            else:#sloped takes 2 or 3 whatever is present
                priorities.append(3 if 0 in types else 2)
        return priorities
    panels = generate_panel_shapes(outer, inner, prioritize)
    export_to_obj(outer,"outer.obj")
    export_to_obj(inner,"inner.obj")
    for panel_index in range(len(panels)):
        export_to_obj(panels[panel_index],"panel."+str(panel_index)+".obj")
