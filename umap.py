"""
BlenderUmap v0.2.0
(C) 2020 amrsatrio. All rights reserved.
"""
import bpy
import json
import os
import time
from math import *
import shutil

# Change the value to the working directory of the Java program with the bat. I'm leaving mine here.
data_dir = r"C:\Users\epicp\Downloads\UmapToUE4-0.9\UmapToUE4-0.9"

clear_scene = True              # Deletes all objects from Blender Scene before starting an Import.
reuse_meshes = True             # Checks to see if a mesh has already been used before, reuses it instead of importing it again.
use_cube_as_fallback = True     # Places a default Cube in the place of any missing or error meshes.
use_gltf = False                # Uses GLTF File Format
verbose = True                  # Prints Debug Stats

ignore_FloorLoot = True         # Ignores Developer FloorLoot Rings (Good for Renders and General Usage)
default_ColorSpace = "sRGB"     # Uses default_ColorSpace instead of Linear for Diffuse Textures. (Default: "sRGB")

# ______________________________________________________________________________________________

# Strayfade Blender to UE4

UseBlenderToUE4 = True
ExportPath = "C:\\Users\\epicp\Desktop\\"

# These last settings can individually export .FBX meshes and/or textures alongside BlenderToUE4
EXPORT_TEXTURES = False
EXPORT_MESHES = False
# All Texture files used in the scene will be copied into this folder. Ideally, this would be a folder referenced by UE4.
UE4_MaterialsFolder = "C:\\Users\\epicp\Documents\\Unreal Projects\\ProjectName\\Content\\Materials\\"
# Example = "C:\\Users\\epicp\Documents\\Unreal Projects\\ProjectName\\Content\\Materials\\"
UE4_MeshesFolder = "C:\\Users\\epicp\Documents\\Unreal Projects\\ProjectName\\Content\\Meshes\\"

# ______________________________________________________________________________________________

def import_umap(comps: list, attach_parent: bpy.types.Object = None) -> None:
    for comp_i, comp in enumerate(comps):
        guid = comp[0]
        export_type = comp[1]
        mesh_path = comp[2]
        mats = comp[3]
        texture_data = comp[4]
        location = comp[5] or [0, 0, 0]
        rotation = comp[6] or [0, 0, 0]
        scale = comp[7] or [1, 1, 1]
        child_comps = comp[8]

        name = export_type + (("_" + guid[:8]) if guid else "")
        print("\nActor %d of %d: %s" % (comp_i + 1, len(comps), name))

        if child_comps and len(child_comps) > 0:
            bpy.ops.mesh.primitive_plane_add(size=1)
            bpy.context.active_object.data = bpy.data.meshes["__empty"]
        elif not mesh_path:
            print("WARNING: No mesh, defaulting to fallback mesh")
            fallback()
        else:
            if mesh_path.startswith("/"):
                mesh_path = mesh_path[1:]

            key = os.path.basename(mesh_path)
            td_suffix = ""

            if mats and len(mats) > 0:
                key += "_{:08x}".format(abs(string_hash_code(";".join(mats.keys()))))
            if texture_data and len(texture_data) > 0:
                td_suffix = "_{:08x}".format(abs(string_hash_code(";".join([it[0] if it else "" for it in texture_data]))))
                key += td_suffix

            existing_mesh = bpy.data.meshes.get(key) if reuse_meshes else None

            if existing_mesh:
                if verbose:
                    print("Using existing mesh")
                bpy.ops.mesh.primitive_plane_add(size=1)
                bpy.context.active_object.data = existing_mesh
            else:
                mesh_import_result = None

                if use_gltf:
                    final_dir = os.path.join(data_dir, mesh_path + ".gltf")
                    if verbose:
                        print("Mesh:", final_dir)
                    if os.path.exists(final_dir):
                        if "Tiered" in mesh_path:
                            print("Skipping FloorLoot blueprint, defaulting to fallback mesh")
                            bpy.ops.mesh.primitive_cube_add(size=0)
                            fallback_cube = bpy.context.active_object
                            fallback_cube.name = "__fallback"
                            fallback_cube.data.name = "__fallback"
                        elif not "Tiered" in mesh_path:
                            mesh_import_result = bpy.ops.import_scene.psk(bReorientBones=True, directory=data_dir, files=[{"name": mesh_path_}])
                    else:
                        print("WARNING: Mesh not found, defaulting to fallback mesh")
                        fallback()
                else:
                    final_dir = os.path.join(data_dir, mesh_path)
                    mesh_path_ = mesh_path
                    if os.path.exists(final_dir + ".psk"):
                        final_dir += ".psk"
                        mesh_path_ += ".psk"
                    elif os.path.exists(final_dir + ".pskx"):
                        final_dir += ".pskx"
                        mesh_path_ += ".pskx"
                    if verbose:
                        print("Mesh:", final_dir)
                    if os.path.exists(final_dir):
                        if "Tiered" in mesh_path:
                            print("Skipping FloorLoot blueprint, defaulting to fallback mesh")
                            bpy.ops.mesh.primitive_cube_add(size=0)
                            fallback_cube = bpy.context.active_object
                            fallback_cube.name = "__fallback"
                            fallback_cube.data.name = "__fallback"
                        elif not "Tiered" in mesh_path:
                            mesh_import_result = bpy.ops.import_scene.psk(bReorientBones=True, directory=data_dir, files=[{"name": mesh_path_}])
                    else:
                        print("WARNING: Mesh not found, defaulting to fallback mesh")
                        fallback()

                if mesh_import_result == {"FINISHED"}:
                    if verbose:
                        print("Mesh imported")
                    bpy.context.active_object.data.name = key
                    bpy.ops.object.shade_smooth()

                    for m_idx, (m_path, m_textures) in enumerate(mats.items()):
                        import_material(m_idx, m_path, td_suffix, m_textures, texture_data)
                else:
                    print("WARNING: Failure importing mesh, defaulting to fallback mesh")
                    fallback()

        created = bpy.context.active_object
        created.name = name
        created.location = [location[0] * 0.01, location[1] * 0.01 * -1, location[2] * 0.01]
        created.rotation_mode = "XYZ"
        created.rotation_euler = [radians(rotation[2] + (90 if use_gltf else 0)), radians(rotation[0] * -1), radians(rotation[1] * -1)]
        created.scale = scale

        if attach_parent:
            print("Attaching to parent", attach_parent.name)
            created.parent = attach_parent

        if child_comps:
            if use_gltf:
                print("Nested worlds aren't supported yet with GLTF")
            else:
                for child_comp in child_comps:
                    import_umap(child_comp, created)


def import_material(m_idx: int, path: str, suffix: str, base_textures: list, tex_data: dict) -> bpy.types.Material:
    # .mat is required to prevent conflicting with the empty ones imported by the PSK plugin
    m_name = os.path.basename(path + ".mat" + suffix)
    m = bpy.data.materials.get(m_name)

    if not m:
        for td_idx, td_entry in enumerate(tex_data):
            if not td_entry:
                continue
            index = {1: 3, 2: 2, 3: 2}.get(td_idx, 0)
            td_textures = td_entry[1]

            for i, tex_entry in enumerate(base_textures[index]):
                if i < len(td_textures) and td_textures[i]:
                    base_textures[index][i] = td_textures[i]

        m = bpy.data.materials.new(name=m_name)
        m.use_nodes = True
        tree = m.node_tree

        for node in tree.nodes:
            tree.nodes.remove(node)
        
        materialCone = (m_name.replace(".mat", ""))
        if "Cone" in materialCone:
            m.blend_method = "CLIP"
            m.alpha_threshold = 1
            use_backface_culling = True
        else:
            m.blend_method = "OPAQUE"
            m.use_backface_culling = True

        def group(sub_tex_idx, location):
            if UseBlenderToUE4:
                sh = tree.nodes.new("ShaderNodeBsdfPrincipled")
            else:
                sh = tree.nodes.new("ShaderNodeGroup")
            sh.location = location
            if not UseBlenderToUE4:
                sh.node_tree = tex_shader
            else:
                sh.inputs[7].default_value = 0.69
            sub_textures = base_textures[sub_tex_idx] if sub_tex_idx < len(base_textures) and base_textures[sub_tex_idx] and len(base_textures[sub_tex_idx]) > 0 else base_textures[0]

            for tex_index, sub_tex in enumerate(sub_textures):
                if sub_tex:
                    img = get_or_load_img(sub_tex) if not sub_tex.endswith("/T_EmissiveColorChart") else None

                    if img:
                        d_tex = tree.nodes.new("ShaderNodeTexImage")
                        d_tex.hide = False
                        d_tex.location = [location[0] - 320, location[1] - tex_index * 250]

                        if tex_index != 0:  # other than diffuse
                            img.colorspace_settings.name = "Non-Color"

                        d_tex.image = img
                            
                        texture_index = tex_index

                        if texture_index is 4:  # change mat blend method if there's an alpha mask texture
                            m.blend_method = "HASHED"
                            tree.links.new(d_tex.outputs[0], sh.inputs[tex_index])
                        if UseBlenderToUE4:
                            if texture_index is 0:
                                tree.links.new(d_tex.outputs[0], sh.inputs[0])
                                tree.links.new(d_tex.outputs[0], sh.inputs[3])
                            elif texture_index is 1:
                                tree.links.new(d_tex.outputs[0], sh.inputs[19])
                                tree.links.new(d_tex.outputs[0], sh.inputs[20])
                            elif texture_index is 2:
                                tree.links.new(d_tex.outputs[0], sh.inputs[5])
                                tree.links.new(d_tex.outputs[0], sh.inputs[6])
                            
                        # Strayfade Blender to UE4 Texture Export
                        if EXPORT_TEXTURES:
                            texturePath = ((data_dir + sub_tex.replace("/", "\\")) + ("." + "TGA".lower()))
                            texturePath = texturePath.replace("\\", "/")
                            texturePath = texturePath.replace("\\", "/")
                            texturePath = texturePath.replace("\\", "/")
                            texturePath = texturePath.replace("//", "/")
                            texturePath = texturePath.replace("//", "/")
                            texturePath = texturePath.replace("//", "/")
                            outputPath = (UE4_MaterialsFolder + (m_name.replace(".mat", ""))) + ("." + "TGA".lower())
                            print("Exporting to " + outputPath)
                            if not os.path.exists(outputPath):
                                print("Move file " + (m_name.replace(".mat", "")) + ("." + "TGA".lower()))
                                shutil.copyfile(texturePath, outputPath)
            return sh

        mat_out = tree.nodes.new("ShaderNodeOutputMaterial")
        mat_out.location = [300, 300]
        if UseBlenderToUE4:
            tree.links.new(group(0, [100, 300]).outputs[0], mat_out.inputs[0])
        else:
            if bpy.context.active_object.data.uv_layers.get("EXTRAUVS0"):
                uvm_ng = tree.nodes.new("ShaderNodeGroup")
                uvm_ng.location = [100, 300]
                uvm_ng.node_tree = bpy.data.node_groups["UV Shader Mix"]
                uv_map = tree.nodes.new("ShaderNodeUVMap")
                uv_map.location = [-100, 700]
                uv_map.uv_map = "EXTRAUVS0"
                tree.links.new(uv_map.outputs[0], uvm_ng.inputs[0])
                tree.links.new(group(0, [-100, 550]).outputs[0], uvm_ng.inputs[1])
                tree.links.new(group(1, [-100, 300]).outputs[0], uvm_ng.inputs[2])
                tree.links.new(group(2, [-100, 50]).outputs[0], uvm_ng.inputs[3])
                tree.links.new(group(3, [-100, -200]).outputs[0], uvm_ng.inputs[4])
                tree.links.new(uvm_ng.outputs[0], mat_out.inputs[0])
            else:
                tree.links.new(group(0, [100, 300]).outputs[0], mat_out.inputs[0])

        print("Material imported")

    if m_idx < len(bpy.context.active_object.data.materials):
        bpy.context.active_object.data.materials[m_idx] = m


def fallback() -> None:
    bpy.ops.mesh.primitive_plane_add(size=1)
    bpy.context.active_object.data = bpy.data.meshes["__fallback" if use_cube_as_fallback else "__empty"]


def get_or_load_img(img_path: str) -> bpy.types.Image:
    img_path = os.path.join(data_dir, img_path[1:] + ".tga")
    existing = bpy.data.images.get(os.path.basename(img_path))

    if existing:
        return existing
    elif os.path.exists(img_path):
        if verbose:
            print(img_path)
        return bpy.data.images.load(filepath=img_path)
    else:
        print("WARNING: " + img_path + " not found")
        return None


def cleanup() -> None:
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)


def string_hash_code(s: str) -> int:
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

# Export Individual Meshes [Blender to UE4 - Strayfade]
def ExportIndividualMeshes():
    basedir = data_dir
    
    view_layer = bpy.context.view_layer
    obj_active = view_layer.objects.active
    selection = bpy.context.selected_objects

    bpy.ops.object.select_all()
    for obj in selection:
        
        # Select each object and create a name/path from it
        obj.select_set(True)
        view_layer.objects.active = obj
        name = bpy.path.clean_name(obj.name)
        fn = os.path.join(UE4_MeshesFolder, name)
        
        # Export Selected Object
        if not os.path.exists(fn + ".fbx"):
            bpy.ops.export_scene.fbx(filepath=fn + ".fbx", use_selection=True)  
        
        # Cleanup
        obj.select_set(False)
        print("Written:", fn)


    view_layer.objects.active = obj_active
    bpy.ops.object.select_all()
    for obj in selection:
        obj.select_set(False)

start = int(time.time() * 1000.0)

# create UV shader mix node group, credits to @FriesFX
uvm = bpy.data.node_groups.get("UV Shader Mix")

if not uvm:
    uvm = bpy.data.node_groups.new(name="UV Shader Mix", type="ShaderNodeTree")
    # for node in tex_shader.nodes: tex_shader.nodes.remove(node)

    mix_1 = uvm.nodes.new("ShaderNodeMixShader")
    mix_2 = uvm.nodes.new("ShaderNodeMixShader")
    mix_3 = uvm.nodes.new("ShaderNodeMixShader")
    mix_4 = uvm.nodes.new("ShaderNodeMixShader")
    mix_1.location = [-500, 300]
    mix_2.location = [-300, 300]
    mix_3.location = [-100, 300]
    mix_4.location = [100, 300]
    uvm.links.new(mix_1.outputs[0], mix_2.inputs[1])
    uvm.links.new(mix_2.outputs[0], mix_3.inputs[1])
    uvm.links.new(mix_3.outputs[0], mix_4.inputs[1])

    x = -1700
    y = 700
    sep = uvm.nodes.new("ShaderNodeSeparateRGB")
    sep.location = [x + 200, y - 200]

    m1_1 = uvm.nodes.new("ShaderNodeMath")
    m1_2 = uvm.nodes.new("ShaderNodeMath")
    m1_3 = uvm.nodes.new("ShaderNodeMath")
    m1_1.location = [x + 400, y]
    m1_2.location = [x + 400, y - 200]
    m1_3.location = [x + 400, y - 400]
    m1_1.operation = "LESS_THAN"
    m1_2.operation = "LESS_THAN"
    m1_3.operation = "LESS_THAN"
    m1_1.inputs[1].default_value = 1.420
    m1_2.inputs[1].default_value = 1.720
    m1_3.inputs[1].default_value = 3.000
    uvm.links.new(sep.outputs[0], m1_1.inputs[0])
    uvm.links.new(sep.outputs[0], m1_2.inputs[0])
    uvm.links.new(sep.outputs[0], m1_3.inputs[0])

    add_1_2 = uvm.nodes.new("ShaderNodeMath")
    add_1_2.location = [x + 600, y - 300]
    add_1_2.operation = "ADD"
    uvm.links.new(m1_1.outputs[0], add_1_2.inputs[0])
    uvm.links.new(m1_2.outputs[0], add_1_2.inputs[1])

    m2_1 = uvm.nodes.new("ShaderNodeMath")
    m2_2 = uvm.nodes.new("ShaderNodeMath")
    m2_3 = uvm.nodes.new("ShaderNodeMath")
    m2_4 = uvm.nodes.new("ShaderNodeMath")
    m2_1.location = [x + 800, y]
    m2_2.location = [x + 800, y - 200]
    m2_3.location = [x + 800, y - 400]
    m2_4.location = [x + 800, y - 600]
    m2_1.operation = "ADD"
    m2_2.operation = "SUBTRACT"
    m2_3.operation = "SUBTRACT"
    m2_4.operation = "LESS_THAN"
    m2_1.use_clamp = True
    m2_2.use_clamp = True
    m2_3.use_clamp = True
    m2_4.use_clamp = True
    m2_1.inputs[1].default_value = 0
    m2_4.inputs[1].default_value = 0.700
    uvm.links.new(m1_1.outputs[0], m2_1.inputs[0])
    uvm.links.new(m1_2.outputs[0], m2_2.inputs[0])
    uvm.links.new(m1_1.outputs[0], m2_2.inputs[1])
    uvm.links.new(m1_3.outputs[0], m2_3.inputs[0])
    uvm.links.new(add_1_2.outputs[0], m2_3.inputs[1])
    uvm.links.new(m1_3.outputs[0], m2_4.inputs[0])

    uvm.links.new(m2_1.outputs[0], mix_1.inputs[0])
    uvm.links.new(m2_2.outputs[0], mix_4.inputs[0])
    uvm.links.new(m2_3.outputs[0], mix_2.inputs[0])
    uvm.links.new(m2_4.outputs[0], mix_3.inputs[0])

    # I/O
    g_in = uvm.nodes.new("NodeGroupInput")
    g_out = uvm.nodes.new("NodeGroupOutput")
    g_in.location = [-1700, 220]
    g_out.location = [300, 300]
    uvm.links.new(g_in.outputs[0], sep.inputs[0])
    uvm.links.new(g_in.outputs[1], mix_1.inputs[2])
    uvm.links.new(g_in.outputs[2], mix_2.inputs[2])
    uvm.links.new(g_in.outputs[3], mix_3.inputs[2])
    uvm.links.new(g_in.outputs[4], mix_4.inputs[2])
    uvm.links.new(mix_4.outputs[0], g_out.inputs[0])

# create texture shader node group, credit @Lucas7yoshi
tex_shader = bpy.data.node_groups.get("Texture Shader")

if not tex_shader:
    tex_shader = bpy.data.node_groups.new(name="Texture Shader", type="ShaderNodeTree")
    # for node in tex_shader.nodes: tex_shader.nodes.remove(node)

    g_in = tex_shader.nodes.new("NodeGroupInput")
    g_out = tex_shader.nodes.new("NodeGroupOutput")
    g_in.location = [-700, 0]
    g_out.location = [350, 300]

    principled_bsdf = tex_shader.nodes.new(type="ShaderNodeBsdfPrincipled")
    principled_bsdf.location = [50, 300]
    tex_shader.links.new(principled_bsdf.outputs[0], g_out.inputs[0])

    # diffuse
    tex_shader.links.new(g_in.outputs[0], principled_bsdf.inputs["Base Color"])

    # normal
    norm_y = -1
    norm_curve = tex_shader.nodes.new("ShaderNodeRGBCurve")
    norm_map = tex_shader.nodes.new("ShaderNodeNormalMap")
    norm_curve.location = [-500, norm_y]
    norm_map.location = [-200, norm_y]
    norm_curve.mapping.curves[1].points[0].location = [0, 1]
    norm_curve.mapping.curves[1].points[1].location = [1, 0]
    tex_shader.links.new(g_in.outputs[1], norm_curve.inputs[1])
    tex_shader.links.new(norm_curve.outputs[0], norm_map.inputs[1])
    tex_shader.links.new(norm_map.outputs[0], principled_bsdf.inputs["Normal"])
    tex_shader.inputs[1].default_value = [0.5, 0.5, 1, 1]

    # specular
    spec_y = 140
    spec_separate_rgb = tex_shader.nodes.new("ShaderNodeSeparateRGB")
    spec_separate_rgb.location = [-200, spec_y]
    tex_shader.links.new(g_in.outputs[2], spec_separate_rgb.inputs[0])
    tex_shader.links.new(spec_separate_rgb.outputs[0], principled_bsdf.inputs["Specular"])
    tex_shader.links.new(spec_separate_rgb.outputs[1], principled_bsdf.inputs["Metallic"])
    tex_shader.links.new(spec_separate_rgb.outputs[2], principled_bsdf.inputs["Roughness"])
    tex_shader.inputs[2].default_value = [0.5, 0, 0.5, 1]

    # emission
    tex_shader.links.new(g_in.outputs[3], principled_bsdf.inputs["Emission"])
    tex_shader.inputs[3].default_value = [0, 0, 0, 1]

    # alpha
    alpha_separate_rgb = tex_shader.nodes.new("ShaderNodeSeparateRGB")
    alpha_separate_rgb.location = [-200, -180]
    tex_shader.links.new(g_in.outputs[4], alpha_separate_rgb.inputs[0])
    tex_shader.links.new(alpha_separate_rgb.outputs[0], principled_bsdf.inputs["Alpha"])
    tex_shader.inputs[4].default_value = [1, 0, 0, 1]

    tex_shader.inputs[0].name = "Diffuse"
    tex_shader.inputs[1].name = "Normal"
    tex_shader.inputs[2].name = "Specular"
    tex_shader.inputs[3].name = "Emission"
    tex_shader.inputs[4].name = "Alpha"

# clear all objects except camera
if clear_scene:
    for obj in bpy.context.scene.objects:
        if obj.type != "CAMERA":
            obj.select_set(True)

    bpy.ops.object.delete()

cleanup()

# setup helper objects
# 1. fallback cube
bpy.ops.mesh.primitive_cube_add(size=2)
fallback_cube = bpy.context.active_object
fallback_cube.name = "__fallback"
fallback_cube.data.name = "__fallback"

# 2. empty mesh
bpy.ops.mesh.primitive_cube_add(size=1)
empty_mesh = bpy.context.active_object
empty_mesh.name = "__empty"
empty_mesh.data.name = "__empty"
empty_mesh.data.clear_geometry()

# do it!
if not data_dir.endswith(os.sep):
    data_dir += os.sep

with open(os.path.join(data_dir, "processed.json")) as file:
    import_umap(json.loads(file.read()))

# delete helper objects
bpy.ops.object.select_all(action="DESELECT")
fallback_cube.select_set(True)
empty_mesh.select_set(True)
bpy.ops.object.delete()
cleanup()

if ignore_FloorLoot:
    for obj in bpy.context.scene.objects:
        if obj.type != "CAMERA":
            if obj.name.startswith("Tiered_Athena"):
                obj.select_set(True)
            if obj.name.startswith("__fallback"):
                obj.select_set(True)
            if obj.name.startswith("__empty"):
                obj.select_set(True)

        bpy.ops.object.delete()
        
if EXPORT_MESHES:
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    ExportIndividualMeshes()
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    
print("All done in " + str(int((time.time() * 1000.0) - start)) + "ms")
