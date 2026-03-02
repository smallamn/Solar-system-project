import math
import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Tuple


G = 0.0012  # Simulation gravity constant (scaled for visualization)
TIMESTEP = 1.0
TRAIL_LENGTH = 180


@dataclass
class Body:
    name: str
    mass: float
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    color: str
    trail: List[Tuple[float, float]] = field(default_factory=list)

    def update_trail(self) -> None:
        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)


class PlanetarySimulator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("2D Planetary Motion Simulator")
        self.width = 1000
        self.height = 700
        self.center_x = self.width / 2
        self.center_y = self.height / 2

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#0b1026")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.controls = tk.Frame(root, bg="#1a1f3c")
        self.controls.pack(fill=tk.X)

        self.is_running = True
        self.speed = tk.DoubleVar(value=1.0)

        self._build_controls()
        self.bodies = self._create_default_system()

        self.root.bind("<space>", self.toggle_running)
        self.root.bind("r", self.reset_system)

        self.animate()

    def _build_controls(self) -> None:
        button_style = {"padx": 10, "pady": 6, "bg": "#2c3468", "fg": "white", "bd": 0}

        tk.Button(self.controls, text="Pause/Resume (Space)", command=self.toggle_running, **button_style).pack(
            side=tk.LEFT, padx=8, pady=8
        )
        tk.Button(self.controls, text="Reset (R)", command=self.reset_system, **button_style).pack(
            side=tk.LEFT, padx=8, pady=8
        )

        tk.Label(self.controls, text="Simulation Speed", bg="#1a1f3c", fg="white").pack(side=tk.LEFT, padx=(25, 8))
        tk.Scale(
            self.controls,
            from_=0.2,
            to=4.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.speed,
            length=220,
            bg="#1a1f3c",
            fg="white",
            highlightthickness=0,
            troughcolor="#0f1533",
        ).pack(side=tk.LEFT)

    def _create_default_system(self) -> List[Body]:
        return [
            Body("Sun", 18000, self.center_x, self.center_y, 0, 0, 15, "#ffd166"),
            Body("Mercury", 5, self.center_x + 90, self.center_y, 0, -4.8, 4, "#c0c0c0"),
            Body("Venus", 8, self.center_x + 140, self.center_y, 0, -4.0, 5, "#f7c59f"),
            Body("Earth", 10, self.center_x + 210, self.center_y, 0, -3.3, 6, "#55d6ff"),
            Body("Mars", 7, self.center_x + 290, self.center_y, 0, -2.8, 5, "#ff6b6b"),
            Body("Jupiter", 120, self.center_x + 430, self.center_y, 0, -2.0, 10, "#d9a066"),
        ]

    def toggle_running(self, event=None) -> None:
        self.is_running = not self.is_running

    def reset_system(self, event=None) -> None:
        self.bodies = self._create_default_system()

    def _update_physics(self) -> None:
        dt = TIMESTEP * self.speed.get()
        accelerations = [(0.0, 0.0) for _ in self.bodies]

        for i, body_a in enumerate(self.bodies):
            ax, ay = 0.0, 0.0
            for j, body_b in enumerate(self.bodies):
                if i == j:
                    continue

                dx = body_b.x - body_a.x
                dy = body_b.y - body_a.y
                dist_sq = dx * dx + dy * dy
                dist = math.sqrt(dist_sq)
                if dist < 1e-6:
                    continue

                force_acc = G * body_b.mass / dist_sq
                ax += force_acc * dx / dist
                ay += force_acc * dy / dist

            accelerations[i] = (ax, ay)

        for i, body in enumerate(self.bodies):
            ax, ay = accelerations[i]
            body.vx += ax * dt
            body.vy += ay * dt
            body.x += body.vx * dt
            body.y += body.vy * dt
            body.update_trail()

    def _draw(self) -> None:
        self.canvas.delete("all")

        for body in self.bodies:
            if len(body.trail) > 1:
                flattened = [coord for point in body.trail for coord in point]
                self.canvas.create_line(*flattened, fill=body.color, width=1)

        for body in self.bodies:
            x, y, r = body.x, body.y, body.radius
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=body.color, outline="")
            self.canvas.create_text(x, y - r - 10, text=body.name, fill="white", font=("Arial", 9))

        self.canvas.create_text(
            160,
            22,
            text="Tip: Space = pause/resume, R = reset",
            fill="#c9d2ff",
            font=("Arial", 11),
        )

    def animate(self) -> None:
        if self.is_running:
            self._update_physics()
        self._draw()
        self.root.after(16, self.animate)


def main() -> None:
    root = tk.Tk()
    PlanetarySimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
