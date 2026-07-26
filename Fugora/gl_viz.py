import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from collections import deque


class GLRenderer3D:
    def __init__(self, engine, width=1280, height=800):
        self.engine = engine
        self.width = width
        self.height = height
        self.running = True

        self.cam_yaw = 0.6
        self.cam_pitch = 0.45
        self.cam_dist = 11.0
        self.pan_x = 0.0
        self.pan_y = 0.0

        self.dragging = False
        self.panning = False
        self.last_mouse = (0, 0)

        self.SCALE = 1e-11
        self.trails = {}
        self.max_trail = 400

        self.sphere_lists = {}
        self.star_positions = None
        self.belt_positions = None
        self.belt_angle = 0.0
        self.glow_tex = None
        self.text_cache = {}

        self.planet_colors = {
            "Sun": (1.0, 0.75, 0.25),
            "Earth": (0.3, 0.55, 1.0),
            "Mars": (0.9, 0.45, 0.25),
            "Jupiter": (0.85, 0.65, 0.4),
            "default": (0.7, 0.7, 0.75),
        }

    def visual_radius(self, obj):
        if obj.radius <= 0:
            return 0.02
        return max(0.02, (obj.radius ** 0.3) * 0.001)

    def get_color(self, name):
        return self.planet_colors.get(name, self.planet_colors["default"])

    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.98, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.12, 0.12, 0.18, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.6, 0.6, 0.6, 1.0])

        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        glClearColor(0.01, 0.01, 0.03, 1.0)

    def build_sphere(self, radius, slices=36, stacks=36):
        lst = glGenLists(1)
        glNewList(lst, GL_COMPILE)
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(radius * x * zr0, radius * y * zr0, radius * z0)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(radius * x * zr1, radius * y * zr1, radius * z1)
            glEnd()
        glEndList()
        return lst

    def get_sphere(self, obj):
        key = obj.id
        if key not in self.sphere_lists:
            self.sphere_lists[key] = self.build_sphere(self.visual_radius(obj))
        return self.sphere_lists[key]

    def build_stars(self, count=4000):
        pts = []
        for _ in range(count):
            theta = np.random.uniform(0, 2 * math.pi)
            phi = np.arccos(np.random.uniform(-1, 1))
            r = np.random.uniform(60, 120)
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            brightness = np.random.uniform(0.3, 1.0)
            size = np.random.choice([1, 1, 1, 2, 2, 3])
            pts.append((x, y, z, brightness, size))
        return pts

    def build_belt(self, count=3500):
        pts = []
        for _ in range(count):
            angle = np.random.uniform(0, 2 * math.pi)
            radius = np.random.uniform(2.1, 3.3)
            height = np.random.uniform(-0.12, 0.12)
            brightness = np.random.uniform(0.2, 0.7)
            pts.append((angle, radius, height, brightness))
        return pts

    def make_glow_texture(self, size=256, color=(255, 200, 90)):
        img = np.zeros((size, size, 4), dtype=np.uint8)
        cx = cy = size / 2
        yy, xx = np.mgrid[0:size, 0:size]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (size / 2)
        intensity = np.clip(1.0 - d, 0, 1) ** 2.2
        img[:, :, 0] = (color[0] * intensity).astype(np.uint8)
        img[:, :, 1] = (color[1] * intensity).astype(np.uint8)
        img[:, :, 2] = (color[2] * intensity).astype(np.uint8)
        img[:, :, 3] = (255 * intensity).astype(np.uint8)

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img)
        return tex

    def text_texture(self, text, color=(220, 220, 230), size=15):
        key = (text, color, size)
        if key in self.text_cache:
            return self.text_cache[key]
        surf = self.font.render(text, True, color)
        data = pygame.image.tostring(surf, "RGBA", True)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     surf.get_width(), surf.get_height(), 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, data)
        self.text_cache[key] = (tex, surf.get_width(), surf.get_height())
        return self.text_cache[key]

    def draw_text_2d(self, text, x, y, color=(220, 220, 230), size=15):
        tex, w, h = self.text_texture(text, color, size)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindTexture(GL_TEXTURE_2D, tex)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def setup_3d(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(55, self.width / self.height, 0.1, 500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        cx = self.cam_dist * math.cos(self.cam_pitch) * math.sin(self.cam_yaw)
        cy = self.cam_dist * math.sin(self.cam_pitch)
        cz = self.cam_dist * math.cos(self.cam_pitch) * math.cos(self.cam_yaw)
        gluLookAt(cx, cy, cz, self.pan_x, self.pan_y, 0, 0, 1, 0)

    def setup_2d(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

    def restore_3d(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    def world_pos(self, obj, center):
        return (
            (obj.position.x - center.position.x) * self.SCALE,
            (obj.position.y - center.position.y) * self.SCALE,
            (obj.position.z - center.position.z) * self.SCALE,
        )

    def draw_starfield(self):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glRotatef(self.belt_angle * 2, 0, 0, 1)
        glBegin(GL_POINTS)
        for x, y, z, b, s in self.star_positions:
            glPointSize(s)
            glColor3f(b, b, b * 0.95)
            glVertex3f(x, y, z)
        glEnd()
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_belt(self):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glRotatef(math.degrees(self.belt_angle), 0, 0, 1)
        glBegin(GL_POINTS)
        for angle, radius, height, b in self.belt_positions:
            glPointSize(1.5)
            glColor3f(0.55 * b, 0.5 * b, 0.45 * b)
            glVertex3f(radius * math.cos(angle), radius * math.sin(angle), height)
        glEnd()
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def draw_reference_rings(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.25, 0.3, 0.45, 0.25)
        for r in [1.0, 1.524, 2.5, 5.2]:
            glBegin(GL_LINE_LOOP)
            for i in range(128):
                a = 2 * math.pi * i / 128
                glVertex3f(r * math.cos(a), r * math.sin(a), 0)
            glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def draw_trails(self, center):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for obj in self.engine.objects:
            trail = self.trails.get(obj.id)
            if not trail or len(trail) < 2:
                continue
            color = self.get_color(obj.name)
            n = len(trail)
            glBegin(GL_LINE_STRIP)
            for i, (px, py, pz) in enumerate(trail):
                alpha = (i / n) * 0.7
                glColor4f(color[0], color[1], color[2], alpha)
                glVertex3f(
                    (px - center.position.x) * self.SCALE,
                    (py - center.position.y) * self.SCALE,
                    (pz - center.position.z) * self.SCALE,
                )
            glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def draw_objects(self, center):
        sun_pos = self.world_pos(center, center)
        glLightfv(GL_LIGHT0, GL_POSITION, [sun_pos[0], sun_pos[1], sun_pos[2], 1.0])

        for obj in self.engine.objects:
            x, y, z = self.world_pos(obj, center)
            glPushMatrix()
            glTranslatef(x, y, z)

            if obj.name == "Sun":
                glDisable(GL_LIGHTING)
                glColor3f(1.0, 0.85, 0.35)
                glCallList(self.get_sphere(obj))
                glEnable(GL_LIGHTING)
            else:
                color = self.get_color(obj.name)
                glColor3f(*color)
                glCallList(self.get_sphere(obj))

            glPopMatrix()

    def draw_screen_glow(self, center):
        self.setup_2d()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)

        for obj in self.engine.objects:
            x, y, z = self.world_pos(obj, center)
            sx, sy, sz = gluProject(x, y, z)
            if sz < 0 or sz > 1:
                continue

            color = self.get_color(obj.name)
            if obj.name == "Sun":
                size = 260 * (11.0 / self.cam_dist)
                alpha = 1.0
            else:
                size = 40 * (11.0 / self.cam_dist)
                alpha = 0.5

            glBindTexture(GL_TEXTURE_2D, self.glow_tex)
            glColor4f(color[0] * alpha, color[1] * alpha, color[2] * alpha, alpha)
            half = size / 2
            glBegin(GL_QUADS)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(sx - half, sy - half)
            glTexCoord2f(1, 0); glVertex2f(sx + half, sy - half)
            glTexCoord2f(1, 1); glVertex2f(sx + half, sy + half)
            glTexCoord2f(0, 1); glVertex2f(sx - half, sy + half)
            glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        self.restore_3d()

def start_gl_viz(engine):
    renderer = GLRenderer3D(engine)
    renderer.init_gl()
    
    renderer.star_positions = renderer.build_stars()
    renderer.belt_positions = renderer.build_belt()
    renderer.glow_tex = renderer.make_glow_texture()
    
    pygame.font.init()
    renderer.font = pygame.font.SysFont("Consolas", 15)
    
    while renderer.running:
        for event in pygame.event.get():
            if event.type == QUIT:
                renderer.running = False
        
        engine.step()
        
        renderer.setup_3d()
        center = engine.objects[0] if engine.objects else None
        if center:
            renderer.draw_starfield()
            renderer.draw_belt()
            renderer.draw_reference_rings()
            renderer.draw_trails(center)
            renderer.draw_objects(center)
            renderer.draw_screen_glow(center)
        
        pygame.display.flip()
    
    pygame.quit()
