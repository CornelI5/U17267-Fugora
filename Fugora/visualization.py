import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class OrbitVisualizer:
    def __init__(self, engine, interval_ms=50):
        self.engine = engine
        self.interval_ms = interval_ms
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.lines = {}
        self.dots = {}
        self.trails = {obj.id: {"x": [], "y": []} for obj in engine.objects}

        self.ax.set_aspect("equal")
        self.ax.set_facecolor("black")
        self.fig.patch.set_facecolor("black")
        self.ax.tick_params(colors="gray")
        for spine in self.ax.spines.values():
            spine.set_color("gray")

    def setup(self):
        for obj in self.engine.objects:
            line, = self.ax.plot([], [], color=obj.color, linewidth=0.8, alpha=0.6)
            dot, = self.ax.plot([], [], "o", color=obj.color, markersize=max(2, min(8, obj.radius / 1e6)))
            self.lines[obj.id] = line
            self.dots[obj.id] = dot

        self.info_text = self.ax.text(
            0.02, 0.98, "", transform=self.ax.transAxes,
            fontsize=9, color="white", verticalalignment="top",
            fontfamily="monospace",
        )

    def update(self, frame):
        self.engine.step()

        max_range = 0
        for obj in self.engine.objects:
            trail = self.trails[obj.id]
            trail["x"].append(obj.position.x)
            trail["y"].append(obj.position.y)

            max_len = 2000
            if len(trail["x"]) > max_len:
                trail["x"] = trail["x"][-max_len:]
                trail["y"] = trail["y"][-max_len:]

            self.lines[obj.id].set_data(trail["x"], trail["y"])
            self.dots[obj.id].set_data([obj.position.x], [obj.position.y])

            r = max(abs(obj.position.x), abs(obj.position.y))
            if r > max_range:
                max_range = r

        margin = max_range * 1.2 if max_range > 0 else 1e11
        self.ax.set_xlim(-margin, margin)
        self.ax.set_ylim(-margin, margin)

        info_lines = [
            f"Time: {self.engine.time_elapsed:.2e} s",
            f"Step: {self.engine.step_count}",
            f"Objects: {len(self.engine.objects)}",
            f"Anomalies: {len(self.engine.anomalies)}",
        ]
        self.info_text.set_text("\n".join(info_lines))

        return list(self.lines.values()) + list(self.dots.values()) + [self.info_text]

    def show(self, total_frames=None):
        self.setup()
        anim = FuncAnimation(
            self.fig, self.update,
            frames=total_frames,
            interval=self.interval_ms,
            blit=False,
            repeat=False,
        )
        plt.show()
        return anim
