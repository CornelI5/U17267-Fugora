import pygame
import math
from pygame.locals import *


class GuiRenderer3D:
    def __init__(self, engine, width=1200, height=800):
        self.engine = engine
        self.width = width
        self.height = height
        self.running = True

        self.angle_x = 0.3
        self.angle_y = 0.0
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0

        self.dragging = False
        self.last_mouse = (0, 0)

        self.colors = {
            "Sun": (255, 220, 50),
            "Earth": (70, 130, 230),
            "Mars": (220, 100, 60),
            "Jupiter": (210, 170, 100),
            "default": (200, 200, 200),
        }

    def rotate(self, x, y, z):
        cos_y = math.cos(self.angle_y)
        sin_y = math.sin(self.angle_y)
        x1 = x * cos_y - z * sin_y
        z1 = z * cos_y + x * sin_y

        cos_x = math.cos(self.angle_x)
        sin_x = math.sin(self.angle_x)
        y2 = y * cos_x - z1 * sin_x
        z2 = z1 * cos_x + y * sin_x

        return x1, y2, z2

    def project(self, x, y, z):
        fov = 600 * self.zoom
        if abs(z) < 1:
            z = 1 if z >= 0 else -1
        factor = fov / (z + fov + 200)

        px = int(x * factor + self.width // 2 + self.pan_x)
        py = int(-y * factor + self.height // 2 + self.pan_y)
        return px, py, factor

    def get_color(self, name):
        return self.colors.get(name, self.colors["default"])

    def draw_hud(self, surface, font):
        lines = [
            f"FUGORA v1.0 | Step: {self.engine.step_count}",
            f"Time: {self.engine.time_elapsed:.2e} s",
            f"Objects: {len(self.engine.objects)}",
            f"Anomalies: {len(self.engine.anomalies)}",
            f"CPU Load: {self.engine.vcpu.current_load:.1f}%",
            "",
            "Left Drag: Rotate | Right Drag: Pan",
            "Scroll: Zoom | R: Reset View | Q: Quit",
        ]
        for i, line in enumerate(lines):
            text = font.render(line, True, (200, 200, 200))
            surface.blit(text, (10, 10 + i * 20))

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height), RESIZABLE)
        pygame.display.set_caption("FUGORA 3D Visualization")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("monospace", 16)

        while self.running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_q or event.key == K_ESCAPE:
                        self.running = False
                    elif event.key == K_r:
                        self.angle_x = 0.3
                        self.angle_y = 0.0
                        self.zoom = 1.0
                        self.pan_x = 0
                        self.pan_y = 0
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        self.last_mouse = pygame.mouse.get_pos()
                    elif event.button == 3:
                        self.dragging = "pan"
                        self.last_mouse = pygame.mouse.get_pos()
                    elif event.button == 4:
                        self.zoom *= 1.1
                    elif event.button == 5:
                        self.zoom /= 1.1
                elif event.type == MOUSEBUTTONUP:
                    self.dragging = False
                elif event.type == MOUSEMOTION:
                    if self.dragging is True:
                        mx, my = pygame.mouse.get_pos()
                        dx = mx - self.last_mouse[0]
                        dy = my - self.last_mouse[1]
                        self.angle_y += dx * 0.005
                        self.angle_x += dy * 0.005
                        self.last_mouse = (mx, my)
                    elif self.dragging == "pan":
                        mx, my = pygame.mouse.get_pos()
                        dx = mx - self.last_mouse[0]
                        dy = my - self.last_mouse[1]
                        self.pan_x += dx
                        self.pan_y += dy
                        self.last_mouse = (mx, my)
                elif event.type == VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    screen = pygame.display.set_mode(
                        (self.width, self.height), RESIZABLE
                    )

            self.engine.step()

            screen.fill((10, 10, 15))

            center_obj = None
            for obj in self.engine.objects:
                if obj.name == "Sun":
                    center_obj = obj
                    break
            if not center_obj and self.engine.objects:
                center_obj = self.engine.objects[0]

            projected = []
            if center_obj:
                for obj in self.engine.objects:
                    rx = obj.position.x - center_obj.position.x
                    ry = obj.position.y - center_obj.position.y
                    rz = obj.position.z - center_obj.position.z

                    scale = 1e-10
                    rx *= scale
                    ry *= scale
                    rz *= scale

                    rx_r, ry_r, rz_r = self.rotate(rx, ry, rz)
                    px, py, factor = self.project(rx_r, ry_r, rz_r)

                    size = max(2, int(obj.radius * 1e-8 * factor * self.zoom))
                    size = min(size, 40)
                    color = self.get_color(obj.name)

                    projected.append((px, py, size, color, obj.name, rz_r))

            projected.sort(key=lambda p: p[5])

            for px, py, size, color, name, _ in projected:
                if -size <= px <= self.width + size and -size <= py <= self.height + size:
                    pygame.draw.circle(screen, color, (px, py), size)
                    if size > 4:
                        label = font.render(name, True, color)
                        screen.blit(label, (px + size + 4, py - 8))

            self.draw_hud(screen, font)
            pygame.display.flip()

        pygame.quit()
        self.engine.stop()


def start_gui_viz(engine, width=1200, height=800):
    renderer = GuiRenderer3D(engine, width, height)
    renderer.run()
