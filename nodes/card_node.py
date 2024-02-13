from bpy.types import Node
from .base_node import BlendRefNode
from ..utils.draw_utils import draw_card, get_dpi_factor
# from ..ui_widgets.ui_panel import UIPanel
import bpy
import time 
import numpy as np
from mathutils import Vector

class CardNode(Node, BlendRefNode):
    '''A card'''
    bl_idname = 'CardNode'
    bl_label = "Card"
    bl_icon = 'SOUND'
    bl_width_max = 10000
    
    def image_update(self, context):
        if self.image:
            self.width = self.image.size[0] / 8
        else:
            self.width = self.bl_width_default
    image: bpy.props.PointerProperty(type=bpy.types.Image, update=image_update)
    
    scale: bpy.props.FloatProperty(name='Scale', default=1)
    rotation: bpy.props.FloatProperty(name='Rotation')
    translation_x: bpy.props.FloatProperty(name='X')
    translation_y: bpy.props.FloatProperty(name='Y')
    widgets = []
    def __init__(self):
        self.line_height = 10
        
    def init(self, context):
        pass
    
    def copy(self, node):
        pass
    def free(self):
        pass

    def draw_buttons_ext(self, context, layout):
        column = layout.column()
        column.label(text='Source')
        column.template_ID(self, 'image', open='image.open', live_icon=True)
        column.label(text='Scale')
        row = column.row(align=True)
        row.prop(self, 'scale')
        column.prop(self, 'rotation')
        column.label(text='Translation')
        row = column.row(align=True)
        row.prop(self, 'translation_x')
        row.prop(self, 'translation_y')
        
    def draw_buttons(self, context, layout):
        row = layout.row()
        if self.image:
            w, h = self.image.size
            offset = np.interp(get_dpi_factor(), [0.5, 1, 2], [18.14697265625, 30.931640625, 60.2490234375])
            size = np.interp(get_dpi_factor(), [0.5, 1, 2], [12, 20, 40])
            try:
                y = self.dimensions.x * (h / w) - offset
            except:
                y = size
            row.scale_y =  y / (size )
        else:
            row.scale_y = 1
        row.label(text='')

    def draw_label(self):
        return "Select Source"
    
    def draw(self, ntree):
        draw_card(self, ntree)
        for widget in self.widgets:
            widget.draw(self, ntree)