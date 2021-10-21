import pygltflib
import numpy as np


def mesh_from_pts(pts, h):
    vs = pts[:]
    for x, y, z in pts:
        vs.append([x, y, z+h])

    vs = np.array(vs, dtype="float32")

    fis = []

    for i in range(len(pts)):
        fis.append([
            i,
            (i + 1) % len(pts),
            len(pts) + (i + 1) % len(pts),
            len(pts) + i
        ])

    if len(pts) == 4:
        fis.append([i for i in range(len(pts))][::-1])
        fis.append([i+len(pts) for i in range(len(pts))])

    tris = []
    for a, b, c, d in fis:
        tris.extend([[a, b, c], [a, c, d]])

    if len(pts) == 3:
        tris.append([i for i in range(len(pts))][::-1])
        tris.append([i+len(pts) for i in range(len(pts))])

    tris = np.array(tris, dtype="uint8")

    return vs, tris


def create_gltf_from_mesh(points, triangles):
    triangles_binary_blob = triangles.flatten().tobytes()
    points_binary_blob = points.tobytes()

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[
            pygltflib.Mesh(
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(POSITION=1), indices=0
                    )
                ]
            )
        ],
        accessors=[
            pygltflib.Accessor(
                bufferView=0,
                componentType=pygltflib.UNSIGNED_BYTE,
                count=triangles.size,
                type=pygltflib.SCALAR,
                max=[int(triangles.max())],
                min=[int(triangles.min())],
            ),
            pygltflib.Accessor(
                bufferView=1,
                componentType=pygltflib.FLOAT,
                count=len(points),
                type=pygltflib.VEC3,
                max=points.max(axis=0).tolist(),
                min=points.min(axis=0).tolist(),
            ),
        ],
        bufferViews=[
            pygltflib.BufferView(
                buffer=0,
                byteLength=len(triangles_binary_blob),
                target=pygltflib.ELEMENT_ARRAY_BUFFER,
            ),
            pygltflib.BufferView(
                buffer=0,
                byteOffset=len(triangles_binary_blob),
                byteLength=len(points_binary_blob),
                target=pygltflib.ARRAY_BUFFER,
            ),
        ],
        buffers=[
            pygltflib.Buffer(
                byteLength=len(triangles_binary_blob) + len(points_binary_blob)
            )
        ],
    )
    gltf.set_binary_blob(triangles_binary_blob + points_binary_blob)

    return gltf


def gltf_from_polyline(pts, h):
    vs, tris = mesh_from_pts(pts, h)

    return create_gltf_from_mesh(vs, tris)


def gltf_from_polylines(ptss, hs):
    vss, triss = [], []

    for i, pts in enumerate(ptss):
        loc_vs, loc_tris = mesh_from_pts(pts, hs[i])

        vss.append(loc_vs)
        triss.append(loc_tris)


def new_gltf():
    return pygltflib.GLTF2()



if __name__ == "__main__":
    a_gltf = new_gltf()

    pts = [[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]]
    pts_bis = [[0., 0., 2.], [1., 0., 2.], [1., 1., 2.], [0., 1., 2.]]

    a_gltf_from_pl = gltf_from_polyline(pts, h=1.)
    a_gltf_from_pl.save("test_new.glb")