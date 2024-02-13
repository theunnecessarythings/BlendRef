import bpy

class BlendRefNode:
    
    def __init__(self):
        self.line_height = 1
    
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'BlendRefTreeType'
    
    def draw_buttons(self, context, layout):
        # for i in range(self.line_height):
        #     layout.label(text='')
        pass
    def draw(self):
        pass
    
    