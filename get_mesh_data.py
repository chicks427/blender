import bpy
import mathutils
import bmesh
import numpy as np
import json

def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=True):
    assert(obj.type == 'MESH')

    if apply_modifiers and obj.modifiers:
        me = obj.to_mesh(bpy.context.scene, True, 'PREVIEW', calc_tessface=False)
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    # Remove custom data layers to save memory
    for elem in (bm.faces, bm.edges, bm.verts, bm.loops):
        for layers_name in dir(elem.layers):
            if not layers_name.startswith("_"):
                layers = getattr(elem.layers, layers_name)
                for layer_name, layer in layers.items():
                    layers.remove(layer)

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm

def get_verts_in_group(obj, group_name):
    vg_idx = obj.vertex_groups[group_name].index
    vs = [ v for v in obj.data.vertices if vg_idx in [ vg.group for vg in v.groups ] ]
    return vs

def get_bmesh_verts(bmesh, group_vertices):
    bmesh.verts.ensure_lookup_table()

    bmesh_verts = []

    for i in range(len(group_vertices)):
        bmesh_verts.append(bmesh.verts[group_vertices[i].index])

    return bmesh_verts

def calculate_distance(inner, outer, group = '', range = False):
    bpy.context.scene.update()

    inner_bm, inner_tree = get_bmesh_and_tree(inner)
    outer_bm, outer_tree = get_bmesh_and_tree(outer)

    if group == '':
        bmesh_verts = get_bmesh_verts(outer_bm, outer.data.vertices)
    else:
        group_verts = get_verts_in_group(outer, group)
        bmesh_verts = get_bmesh_verts(outer_bm, group_verts)

    distances = []

    for v in bmesh_verts:
        loc, norm, index, dist = inner_tree.find_nearest(v.co)
        distances.append(dist)

    if range:
        return max(distances)
    else:
        return sum(distances)

def get_bmesh_and_tree(object):
    object_bmesh = bmesh_copy_from_object(object)

    object_tree = mathutils.bvhtree.BVHTree.FromBMesh(object_bmesh)

    return object_bmesh, object_tree

def select_objects():
    inner = bpy.context.object
    outer = (ob for ob in bpy.context.selected_objects if ob != inner).__next__()

    return inner, outer

def random_bone_movement(armature, bone_name, factor = 0.01):
    bone = armature.pose.bones[bone_name]

    bone.location.z += factor * (np.random.uniform() - .5)
    bone.location.y += factor * (np.random.uniform() - .5)
    bone.location.x += factor * (np.random.uniform() - .5)

def get_bone_locs(armature, bone_name):
    bone = armature.pose.bones[bone_name]
    return bone.location.x, bone.location.y, bone.location.z

def get_default_positions(armature, bone_list):
    default_position = {}
    for bone in bone_list:
        x = armature.pose.bones[bone].location.x
        y = armature.pose.bones[bone].location.y
        z = armature.pose.bones[bone].location.z
        vector = mathutils.Vector((x,y,z))
        default_position[bone] = vector
    return default_position

def reset_positions(armature, default_position):
    for bone in default_position:
        armature.pose.bones[bone].location = default_position[bone]

def collect_bone_data(armature, bone_name, factor, inner, outer, subdiv, axis):
    bone = armature.pose.bones[bone_name]

    axis_no = -1

    if axis == 'x':
        axis_no = 0
    elif axis == 'y':
        axis_no = 1
    elif axis == 'z':
        axis_no = 2

    distances = []

    default_loc = bone.location[axis_no]

    distances.append([bone.location[axis_no], calculate_distance(inner, outer, 'raycast2')])

    movement_amount = factor/subdiv

    for i in range(subdiv):
        bone.location[axis_no] += ((i+1) * movement_amount)
        distances.append([bone.location[axis_no], calculate_distance(inner, outer, 'raycast2')])

        bone.location[axis_no] = default_loc

        bone.location[axis_no] -= ((i+1) * movement_amount)
        distances.append([bone.location[axis_no], calculate_distance(inner, outer, 'raycast2')])

        bone.location[axis_no] = default_loc

    return distances

def get_mesh_data(object):
    """We want lists of the vertices and their positions; the edges formed from
    each vertex; the faces formed by each vertex"""
    bmesh, tree = get_bmesh_and_tree(object)
    bmesh_verts = get_bmesh_verts(bmesh, object.data.vertices)

    mesh_data_dictionary = {'Vertices': [],
    'Edges': [],
    'Faces': []}

    for v in bmesh_verts:
        coordinates = (v.co.x, v.co.y, v.co.z)
        mesh_data_dictionary['Vertices'].append((v.index, coordinates))

    for e in object.data.edges:
        vertices_in_edge = []
        for v in e.vertices:
            vertices_in_edge.append(v)
        mesh_data_dictionary['Edges'].append(tuple(vertices_in_edge))

    for f in object.data.polygons:
        vertices_in_face = []
        for v in f.vertices:
            vertices_in_face.append(v)
        mesh_data_dictionary['Faces'].append(tuple(vertices_in_face))

    return mesh_data_dictionary

datapoints = 10
armature = bpy.data.objects["Armature.001"]

data_set = []

"""default = get_default_positions(armature, list_of_bones)

with open('data.txt', 'w') as f:
    for item in data_set:
        f.write("%s\n" % item)"""


body = bpy.data.objects['24_body_0.9_1_1.001']
thighhighs = bpy.data.objects['24_tights_0.6_1_1.001']
shoes = bpy.data.objects['24_shoes_0.7_1_1.001']
suit = bpy.data.objects['24_suit_0.4_1_1.001']
tie = bpy.data.objects['24_necktief_0.5_1_1.001']
collar = bpy.data.objects['24_collarf_0.6_1_1.001']
face = bpy.data.objects['24_face_0.9_1_1.001']
lips = bpy.data.objects['24_lips_0.4_1_1.001']
teeth = bpy.data.objects['24_teeth_0.9_1_1.001']
hair_front = bpy.data.objects['25_fronthair_0.4_1_1.001']
hair_back = bpy.data.objects['25_backhair1_0.4_1_1']
hair_back2 = bpy.data.objects['25_backhair2_0.4_1_1']
hair_back3 = bpy.data.objects['25_backhair3_0.4_1_1']
hair_base = bpy.data.objects['25_Hairbase_0.4_1_1']
eyeballs = bpy.data.objects['24_eyesballs_0.4_1_1.001']
iris = bpy.data.objects['24_eyes_0.8_1_1.001']

mesh_objects = [body, thighhighs, shoes, suit, tie, collar, face,
lips, teeth, hair_front, hair_back, hair_back2, hair_back3, hair_base,
eyeballs, iris]

#mesh_data = get_mesh_data(lips)
mesh_data = {}

for i in range(len(mesh_objects)):
    mesh_data[i] =get_mesh_data(mesh_objects[i])

with open("mesh_data.json", "w") as w:
    json.dump(mesh_data, w)
