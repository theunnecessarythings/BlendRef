import bpy
from bpy.types import NodeTree
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
import bgl 
import time 


class BlendRefNodes(NodeTree):
    '''BlendRef Editor'''
    bl_idname = 'BlendRefTreeType'
    bl_label = "BlendRef"
    bl_icon = 'NODETREE'

class BlendRefCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'BlendRefTreeType'
 

def draw_handler():
    context = bpy.context
    if context.space_data.tree_type == 'BlendRefTreeType': 
        then = time.time()
        ntree = context.space_data.edit_tree
        if ntree is None:
            return
        for node in ntree.nodes:
            if node.type != 'FRAME':
                node.draw(ntree)
        # print(1/(time.time() - then))

node_categories = [
    BlendRefCategory('SOMENODES', "Nodes", items=[
        NodeItem("CardNode"),
        # NodeItem("NodeFrame"),
    ])
]
_handler = None

addon_keymaps = []
def register():
    nodeitems_utils.register_node_categories('BLENDREF_NODES', node_categories)
    global _handler
    _handler = bpy.types.SpaceNodeEditor.draw_handler_add(draw_handler, (), 'WINDOW', 'POST_PIXEL')
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new('blendref.rotate', type='R', value='PRESS', shift=True)
        addon_keymaps.append([km, kmi])
        
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new('blendref.zoom_in', type='Z', value='PRESS', alt=True)
        addon_keymaps.append([km, kmi])

        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new('blendref.zoom_out', type='Z', value='PRESS', alt=True, shift=True)
        addon_keymaps.append([km, kmi])
        
        km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
        kmi = km.keymap_items.new('blendref.move', type='M', value='PRESS', shift=True)
        addon_keymaps.append([km, kmi])

    
def unregister():
    nodeitems_utils.unregister_node_categories('BLENDREF_NODES')
    bpy.types.SpaceNodeEditor.draw_handler_remove(_handler, 'WINDOW')
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)