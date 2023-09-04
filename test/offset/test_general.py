from _decimal import Decimal

from model import Face
from offset import apply_offset

def test_that_topology_is_the_same(polyhedron_cutout_sloped):
    input = polyhedron_cutout_sloped()
    output = apply_offset(polyhedron=input, offset=Decimal(10))
    assert len(output.faces) == len(input.faces), f"Expected {len(input.faces)} faces, got {len(output.faces)}"
    for face_index in range(len(input.faces)):
        input_face = input.faces[face_index]
        output_face = output.faces[face_index]
        assert len(output_face.vertices) == len(input_face.vertices), f"Face #{face_index} got {len(output_face.vertices)} instead of {len(input_face.vertices)}"
    for face1_index in range(len(input.faces)):
        input_face1 = input.faces[face1_index]
        output_face1 = output.faces[face1_index]
        vertex_count1 = len(input_face1.vertices)
        for face2_index in range(len(input.faces)):
            input_face2 = input.faces[face2_index]
            output_face2 = output.faces[face2_index]
            vertex_count2 = len(input_face2.vertices)
            for vertex1_index in range(vertex_count1):
                for vertex2_index in range(vertex_count2):
                    same_in_input = (input_face1.vertices[vertex1_index] is input_face2.vertices[vertex2_index])
                    same_in_output = (output_face1.vertices[vertex1_index] is output_face2.vertices[vertex2_index])
                    assert same_in_output == same_in_input, f"Vertex #{vertex1_index} of face #{face1_index} is the same as vertex #{vertex2_index} of face #{face2_index} in the input but not in the output"

def test_that_the_input_has_not_been_changed(polyhedron_cutout_sloped):
    input = polyhedron_cutout_sloped()
    before = [[[vertex.x, vertex.y, vertex.z] for vertex in face.vertices] for face in input.faces]
    output = apply_offset(polyhedron=input, offset=Decimal(10))
    after = [[[vertex.x, vertex.y, vertex.z] for vertex in face.vertices] for face in input.faces]
    assert after == before, f"The operation changed coordinates of the input object"

def test_that_input_and_output_do_not_reference_same_objects(polyhedron_cutout_sloped):
    input = polyhedron_cutout_sloped()
    output = apply_offset(polyhedron=input, offset=Decimal(10))
    for face1 in input.faces:
        for face2 in output.faces:
            assert face1 is not face2, "The output shares a face object with the input"
            for vertex1 in face1.vertices:
                for vertex2 in face2.vertices:
                    assert vertex1 is not vertex2, "The output shares a vertex object with the input"
