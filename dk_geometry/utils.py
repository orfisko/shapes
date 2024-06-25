# Copyright: 2024 BV De Kastenman


def export_to_obj(polyhedron, path):
    with open(path, "w") as file:
        file = open(path, "a")
        vertex_indices = {}
        next_index = 1
        for face in polyhedron.faces:
            for vertex in face.vertices:
                if not id(vertex) in vertex_indices:
                    file.write(
                        "v "
                        + str(vertex.x)
                        + " "
                        + str(vertex.y)
                        + " "
                        + str(vertex.z)
                        + "\n"
                    )
                    vertex_indices[id(vertex)] = next_index
                    next_index += 1
            file.write("f")
            for vertex in face.vertices:
                file.write(" " + str(vertex_indices[id(vertex)]))
            file.write("\n")
