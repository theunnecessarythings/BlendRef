import bpy
import numpy as np
from bpy.props import IntProperty, FloatProperty
import math
from mathutils import Vector

def angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    sign = -1 if (b[0] - a[0]) * (c[1] - a[1] ) - (b[1] - a[1]) * (c[0] - a[0]) < 0 else 1
    return np.degrees(angle) * sign

class ZoomInRefOperator(bpy.types.Operator):
    """ZoomIn Reference Image"""
    bl_idname = "blendref.zoom_in"
    bl_label = "ZoomIn Reference Image"
    
    def execute(self, context):
        if context.active_node:
            context.active_node.scale += 0.1
            context.area.tag_redraw()
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

class ZoomOutRefOperator(bpy.types.Operator):
    """ZoomOut Reference Image"""
    bl_idname = "blendref.zoom_out"
    bl_label = "ZoomOut Reference Image"
    
    def execute(self, context):
        if context.active_node:
            context.active_node.scale -= 0.1
            if context.active_node.scale < 0:
                context.active_node.scale = 0
            context.area.tag_redraw()
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

class MoveRefOperator(bpy.types.Operator):
    """Move Reference Image"""
    bl_idname = "blendref.move"
    bl_label = "Move Reference Image"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            node = context.active_node
            delta_x = (self.prev_mouse[0] - event.mouse_x) / 750
            delta_y = (self.prev_mouse[1] - event.mouse_y) / 750
            self.translation_x += delta_x
            self.translation_y += delta_y
            node.translation_x += delta_x
            node.translation_y += delta_y
            context.area.tag_redraw()
            self.prev_mouse = (event.mouse_x, event.mouse_y)
            
        elif event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            context.area.tag_redraw()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.area.tag_redraw()
            return {'CANCELLED'}
        

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.active_node:
            self.prev_mouse = (event.mouse_x, event.mouse_y)
            self.init_x = context.active_node.translation_x
            self.init_y = context.active_node.translation_y
            self.translation_x = 0
            self.translation_y = 0
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

        
class RotateRefOperator(bpy.types.Operator):
    """Rotate Reference Image"""
    bl_idname = "blendref.rotate"
    bl_label = "Rotate Reference Image"

    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            if self.text_mode:
                return {'RUNNING_MODAL'}
            context.area.header_text_set("Rotation : %.4f" % self.rotation)
            node = context.active_node
            center = Vector((0,0))
            center.x = node.location.x + (node.dimensions / 2).x
            center.y = node.location.y - (node.dimensions / 2).y
            pivot = context.region.view2d.view_to_region(center.x, center.y)
            delta = angle(self.prev_mouse, pivot, (event.mouse_x, event.mouse_y))
            if not math.isnan(delta):
                node.rotation -= delta
                self.rotation += delta
            context.area.tag_redraw()
            self.prev_mouse = (event.mouse_x, event.mouse_y)
            
        elif event.type in ['NUMPAD_1', 'NUMPAD_2', 'NUMPAD_3', 'NUMPAD_4', 'NUMPAD_5', 'NUMPAD_6', 'NUMPAD_7', 'NUMPAD_8', 'NUMPAD_9', 'NUMPAD_0', 'NUMPAD_PERIOD', 'PERIOD', 'BACK_SPACE', 'NUMPAD_MINUS'] and event.value == 'PRESS':
            numap = {'NUMPAD_1':'1', 'NUMPAD_2':'2', 'NUMPAD_3':'3', 'NUMPAD_4':'4', 'NUMPAD_5':'5', 'NUMPAD_6':'6', 'NUMPAD_7':'7', 'NUMPAD_8':'8', 'NUMPAD_9':'9', 'NUMPAD_0':'0', 'NUMPAD_PERIOD':'.', 'PERIOD':'.'}
            self.text_mode = True
            if event.type == 'BACK_SPACE':
                if self.text != '0':
                    self.text = self.text[:-1]
            elif event.type == 'NUMPAD_MINUS':
                self.sign *= -1
            else:
                self.text += numap[event.type]
            node = context.active_node
            node.rotation += self.rotation
            node.rotation -= float(self.text) * self.sign 
            self.rotation = float(self.text) * self.sign
            context.area.header_text_set("Rotation : %.4f" % (float(self.text) * self.sign))
            context.area.tag_redraw()
        elif event.type in {'LEFTMOUSE', 'RET', 'NUMPAD_ENTER'}:
            context.area.header_text_set(None)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.active_node.rotation = self.init_rotation
            context.area.tag_redraw()
            context.area.header_text_set(None)
            return {'CANCELLED'}
        

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.active_node:
            self.prev_mouse = (event.mouse_x, event.mouse_y)
            self.init_rotation = context.active_node.rotation
            self.rotation = 0
            self.text = '0'
            context.window_manager.modal_handler_add(self)
            self.text_mode = False
            self.sign = 1
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


from bpy_extras.io_utils import ImportHelper

def separate_thread(self, context):
    from time import sleep
    for i in range(100):
        sleep(0.1)
        self.report({'INFO'}, f"{i}%")
    self.report({'INFO'}, "100% Finished")
    self.finished = True

import os

def load_images(self, context, filepaths):
    print('Entered')
    ntree = context.space_data.edit_tree
    # ntree = bpy.data.node_groups[self.ntree]
    nodes = []
    for i, file_elem in enumerate(filepaths):
        print('Loading ' + file_elem)
        self.report({'INFO'}, f"{int(i*100/len(filepaths))}%")
        img = bpy.data.images.load(file_elem, check_existing=True)
        node = ntree.nodes.new('CardNode')
        node.image = img
        nodes.append(node)
        
    
    if len(nodes) > 0:
        node = nodes[0]
        prev_node = node
        max_height = node.width * node.image.size[1] / node.image.size[0]
        height = 0
        for i, cnode in enumerate(nodes[1:]):
            cnode.location.x = prev_node.location.x + prev_node.width + 10
            cnode.location.y = node.location.y - height - 20
            max_height = max(cnode.width * cnode.image.size[1] / cnode.image.size[0], max_height)
            prev_node = cnode
            
            if i % 10 == 0:
                height += max_height
                max_height = 0
                prev_node = node
            
    self.report({'INFO'}, "100% Finished")
    self.finished = True

class StringProp(bpy.types.PropertyGroup):
    filename: bpy.props.StringProperty()

class WM_OT_dummy_progress(bpy.types.Operator):
    bl_idname = 'wm.dummy_progress'
    bl_label = 'Dummy Progress'
    files : bpy.props.CollectionProperty(name='File Paths', type=StringProp)
    ntree: bpy.props.StringProperty(name='Node Tree')
    
    def modal(self, context, event):
        if self.finished:
            return {'FINISHED'}
        else:
            return {'PASS_THROUGH'}
        
    def invoke(self, context, event):
        self.finished = False
        from threading import Timer
        Timer(0, load_images, (self, context)).start()
        wm = context.window_manager
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    
class ImportImageBlendRef(bpy.types.Operator, ImportHelper):
    """Import Image into BlendRef"""
    bl_idname = "blendref.import_image" 
    bl_label = "Import Image into BlendRef"

    files : bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    directory:  bpy.props.StringProperty(
            subtype='DIR_PATH',
            )
    filename_ext = "Image file"
    filter_glob : bpy.props.StringProperty(default="*.jpg;*.JPG;*.jpeg;*.JPEG;*.png;*.PNG;*.bmp;*.BMP;*.tiff;*.TIFF", options={'HIDDEN'})

    def execute(self, context):
        # load_images(self, context)
        filepaths = []
        for f in self.files:
            filepath = os.path.join(self.directory, f.name)
            filepaths.append(filepath)
        # bpy.ops.wm.dummy_progress('INVOKE_DEFAULT',files=filepaths, ntree=context.space_data.edit_tree.name)
        load_images(self, context, filepaths)
        return {'FINISHED'}

def menu_func_import(self, context):
    if context.space_data.tree_type == 'BlendRefTreeType':
        col = self.layout.column()
        col.operator(ImportImageBlendRef.bl_idname, text="Import Images")
        col.enabled = context.space_data.edit_tree is not None 
        # self.layout.operator(WM_OT_dummy_progress.bl_idname, text='Dummy Progress')
def register():
    bpy.types.NODE_HT_header.append(menu_func_import)


def unregister():
    bpy.types.NODE_HT_header.remove(menu_func_import)