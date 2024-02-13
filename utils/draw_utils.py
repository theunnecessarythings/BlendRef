import bgl, gpu
from gpu_extras.batch import batch_for_shader
import blf
import bpy
import textwrap

from mathutils import Vector, Matrix
from math import cos, sin, radians
shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

frag = '''
in vec2 texCoord_interp;
out vec4 fragColor;

uniform sampler2D image;


void main()
{
    if(texCoord_interp.x > 1 || texCoord_interp.y > 1 || texCoord_interp.x < 0 || texCoord_interp.y < 0 )
        fragColor = vec4(0.188);
    else
        fragColor = texture(image, texCoord_interp);
}
'''

vert = '''
    
uniform mat4 ModelViewProjectionMatrix;

in vec2 texCoord;
in vec2 pos;
out vec2 texCoord_interp;
uniform float rotation;
uniform vec2 location;
uniform float scale;
uniform vec2 u_resolution;

vec2 HALF = vec2(0.5);

vec2 rotate(float angle, vec2 tc) {
    float aSin = sin(angle);
    float aCos = cos(angle);

    float aspect = u_resolution.x / u_resolution.y;

    mat2 rotMat      = mat2(aCos, -aSin, aSin, aCos);
    mat2 scaleMat    = mat2(aspect, 0.0, 0.0, 1.0);
    mat2 scaleMatInv = mat2(1.0/aspect, 0.0, 0.0, 1.0);

    tc -= HALF.xy;
    tc = scaleMatInv * rotMat * scaleMat * tc;
    tc += HALF.xy;
    return tc;
}

vec3 node_mapping(vec3 VectorIn, vec3 Location, vec3 Rotation, vec3 Scale) {
    vec3 tc = ((VectorIn - vec3(0.5)) * Scale) + Location + vec3(0.5);
    return vec3(rotate(Rotation.z, tc.xy), 0);
}


void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
  gl_Position.z = 1.0;
  texCoord_interp = node_mapping(vec3(texCoord, 0), vec3(location, 0), vec3(0, 0, rotation), vec3(1/scale)).xy;
}
'''

image_shader = gpu.types.GPUShader(vert, frag)

def get_dpi_factor():
    return get_dpi() / 72

def get_dpi():
    systemPreferences = bpy.context.preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return systemPreferences.dpi * retinaFactor

def get_position(node, region, dpiFactor, offset):
    location = node.location * dpiFactor
    viewToRegion = region.view2d.view_to_region
    return Vector(viewToRegion(location.x + offset.x, location.y + offset.y, clip = False))

def getNodeTopCornerLocations(node, region, dpiFactor):
    location = node.location * dpiFactor
    if node.hide:
        location.y += 5 * dpiFactor
    dimensions = node.dimensions
    x = location.x
    y = location.y

    viewToRegion = region.view2d.view_to_region
    topLeft = Vector(viewToRegion(x, y, clip = False))
    topRight = Vector(viewToRegion(x + dimensions.x, y, clip = False))
    
    y = location.y - dimensions.y
    bottomLeft = Vector(viewToRegion(x, y, clip = False))
    bottomRight = Vector(viewToRegion(x + dimensions.x, y, clip = False))
    
    return topLeft, topRight, bottomLeft, bottomRight


def getDrawPositionAndWidth(node, region, dpiFactor):
    topLeft, topRight, bottomLeft, bottomRight = getNodeTopCornerLocations(node, region, dpiFactor)
    width = topRight.x - topLeft.x
    height = topLeft.y - bottomLeft.y
    return topLeft, width, height


def draw_image(node, ntree, coords):  
    coords = [(x, y) for x, y, z in coords[:-1]]
    texCoord = ((0, 1), (1, 1), (1, 0), (0, 0))
    image = node.image

    shader = image_shader
    batch = batch_for_shader(
        shader, 'TRI_FAN',
        {
            "pos": coords,
            "texCoord": texCoord,
        },
    )
    if image.gl_load():
        raise Exception()
    
    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)

    shader.bind()
    shader.uniform_int("image", 0)
    shader.uniform_float("rotation", radians(node.rotation))
    shader.uniform_float("location", (node.translation_x, node.translation_y))
    shader.uniform_float("scale", node.scale)
    shader.uniform_float("u_resolution", node.image.size)
    batch.draw(shader)


def draw_card(node, ntree):
    dpiFactor = get_dpi_factor()
    position, w, h = getDrawPositionAndWidth(node, bpy.context.region, dpiFactor)
    x, y = position
    coords = [(x, y, 0), (x + w, y, 0), (x, y - h, 0), (x + w, y - h, 0)]
    if node.use_custom_color:
        r, g, b = node.color * 0.9
    else:
        r, g, b = (0.188, 0.188, 0.188)
    
    indices = ((0, 1, 2), (2, 1, 3))
    batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=indices)
    # bgl.glEnable(bgl.GL_BLEND)
    shader.bind()
    shader.uniform_float("color", (r, g, b, 1))
    batch.draw(shader)
    
    if node.select:
        if ntree.nodes.active == node:
            color = (1, 1, 1, 1)
        else:
            color = (0.8, 0, 0, 1)
    else:
        color = (0.5, 0.5, 0.5, 1)
        
    coords = [(x, y, 0), (x + w, y, 0), (x + w, y - h, 0), (x, y - h, 0), (x, y, 0)]    
    batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": coords})
    bgl.glLineWidth(2)
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    bgl.glLineWidth(1)
    
    # bgl.glDisable(bgl.GL_BLEND)
    
    
    # Place Header
    if node.hide:
        offset = Vector((22, -15)) * dpiFactor
    else:
        offset = Vector((23, -15)) * dpiFactor
    x, y = get_position(node, bpy.context.region, dpiFactor, offset)
    blf.position(0, int(x), int(y), 0)
    blf.color(0, 0.9, 0.9, 0.9, 1)
    
    
    blf.size(0, int(12 / node.dimensions.x * w), int(get_dpi()))
    text = "Select Source" if not node.label else node.label
    char_width = blf.dimensions(0, "Abcde")[0] / 5
    text = text[:int((w + (position.x - x)) / char_width)]  
    blf.draw(0, text)

    
    if not node.hide and node.image:
        draw_image(node, ntree, coords)