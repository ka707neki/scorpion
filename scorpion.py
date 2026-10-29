import pygame
import math
import sys
import random

# ========== Window settings ==========
W, H = 900, 650
N, D = 90, 6          # N = number of body joints, D = fixed distance (px) between neighbors
FPS = 60

# ========== Motion & performance settings ==========
SPEED_MULTIPLIER = 1.0   # global speed scale for the head
FOOT_SMOOTH = 0.35       # 0..1, how fast a foot snaps to its new target (higher = snappier)
HEAD_SPEED = 0.08        # fraction of the distance-to-mouse covered per frame (easing)

# ========== Color system ==========
COLORS = {
    "bg": (8, 8, 12),
    "accent_primary": (200, 170, 120),
    "accent_secondary": (150, 140, 130),
    "body_highlight": (240, 230, 220),
    "body_midtone": (100, 90, 85),
    "body_shadow": (40, 35, 32),
    "glow_warm": (255, 200, 100),
    "grid_subtle": (25, 20, 22),
}

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Scorpion Cursor - Luxury Edition")
clock = pygame.time.Clock()
font_info = pygame.font.Font(None, 18)


# ========== Particle system ==========
class ParticleSystem:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, vx, vy, lifetime, color, size):
        # Each particle is a plain dict. "life" counts down every frame;
        # "max_life" is kept so we can compute how faded it is (life / max_life).
        self.particles.append({
            "x": x, "y": y, "vx": vx, "vy": vy,
            "life": lifetime, "max_life": lifetime,
            "color": color, "size": size,
        })

    def update(self):
        # Iterate over a COPY (particles[:]) because we remove items
        # from the list while looping; doing it on the original would skip items.
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15          # simple gravity: velocity grows downward each frame
            p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surf):
        for p in self.particles:
            # k goes from 1.0 (just born) to 0.0 (about to die)
            k = p["life"] / p["max_life"]
            size = max(1, int(p["size"] * k))                      # shrink over time
            color = tuple(int(c * k) for c in p["color"])          # fade to black (= background)
            pygame.draw.circle(surf, color, (int(p["x"]), int(p["y"])), size)


# ========== The scorpion ==========
class ScorpionLuxury:
    def __init__(self, start_x, start_y):
        # The whole body is a chain of N points laid out in a horizontal line.
        # Index 0 = head, index N-1 = tail tip.
        self.joints = [[start_x - i * D, start_y] for i in range(N)]
        # frames_cache[i] = (tangent_x, tangent_y, normal_x, normal_y) for joint i.
        # Computed once per frame and reused by legs, body, claws and tail.
        self.frames_cache = []
        self.particles = ParticleSystem()
        self.glow_intensity = 0   # 0..1, claws glow while the scorpion moves
        self.time = 0             # frame counter, drives the tail animation

        # Legs: (joint index the leg is attached to, how far it reaches sideways).
        # Each pair is mirrored with side = -1 (left) and +1 (right).
        # "foot" is None until the first update places it.
        self.legs = []
        for idx, reach in ((8, 62), (14, 72), (20, 68), (26, 58)):
            for side in (-1, 1):
                self.legs.append({"i": idx, "s": side, "r": reach, "foot": None})

        self.cache_frames()

    def width(self, i):
        """Body thickness at joint i (the body "shape profile")."""
        t = i / (N - 1)   # 0 = head, 1 = tail tip
        if t < 0.36:
            # Front part (the thick body): a half sine wave gives a smooth
            # bell shape. The ** 0.6 power makes the bell wider/flatter.
            return 6 + 24 * math.sin(t / 0.36 * math.pi) ** 0.6
        # Tail part: thickness shrinks from 16 down to 3 toward the tip.
        # (1 - ...) goes 1 -> 0 along the tail; ** 1.2 makes it taper a bit faster.
        return 3 + 13 * (1 - (t - 0.36) / 0.64) ** 1.2

    def frame_at(self, i):
        """Local coordinate system at joint i: a tangent and a normal vector."""
        # Use the neighbors on both sides (central difference) for a smooth direction.
        a = self.joints[max(i - 1, 0)]
        b = self.joints[min(i + 1, N - 1)]
        tx, ty = a[0] - b[0], a[1] - b[1]      # points from tail side toward head side
        m = math.hypot(tx, ty) or 1            # "or 1" avoids division by zero
        tx, ty = tx / m, ty / m                # normalize to length 1
        # Normal = tangent rotated by 90 degrees: (x, y) -> (-y, x).
        # It points sideways, and is used to offset legs, ribs and claws.
        return tx, ty, -ty, tx

    def cache_frames(self):
        self.frames_cache = [self.frame_at(i) for i in range(N)]

    def update(self, mouse):
        self.time += 1
        prev_head = self.joints[0].copy()

        # ----- 1) Move the head toward the mouse -----
        hx, hy = self.joints[0]
        dx, dy = mouse[0] - hx, mouse[1] - hy
        d = math.hypot(dx, dy)

        if d > 25:   # dead zone: stop when close enough so it doesn't jitter
            # Easing: speed is proportional to distance (slows down when near),
            # capped at 7 px/frame so it never gets too fast.
            sp = min(7, d * HEAD_SPEED) * SPEED_MULTIPLIER
            self.joints[0][0] += dx / d * sp   # dx/d = unit direction toward the mouse
            self.joints[0][1] += dy / d * sp

        # ----- 2) Glow + particles depend on how much the head actually moved -----
        movement = math.hypot(self.joints[0][0] - prev_head[0],
                              self.joints[0][1] - prev_head[1])
        if movement > 1.5:
            self.glow_intensity = min(1.0, self.glow_intensity + 0.2)   # fade in
            if random.random() < 0.3:   # only ~30% of frames spawn a particle
                angle = math.atan2(dy, dx)   # direction of travel
                # Particle velocity points OPPOSITE to travel (minus sign) = a trail.
                self.particles.spawn(
                    prev_head[0], prev_head[1],
                    -math.cos(angle) * 0.5, -math.sin(angle) * 0.5,
                    15, COLORS["accent_primary"], 2)
        else:
            self.glow_intensity = max(0, self.glow_intensity - 0.1)     # fade out

        # ----- 3) Make every joint follow the one before it ("follow the leader") -----
        # For each joint, keep its direction from the previous joint but force the
        # distance to exactly D. This keeps the body a fixed length and makes it
        # curve smoothly behind the head like a snake.
        for i in range(1, N):
            p, q = self.joints[i - 1], self.joints[i]
            dx, dy = q[0] - p[0], q[1] - p[1]
            m = math.hypot(dx, dy) or 1
            q[0] = p[0] + dx / m * D
            q[1] = p[1] + dy / m * D

        # Body moved, so recompute tangents/normals once for this frame
        self.cache_frames()

        # ----- 4) Leg stepping -----
        for leg in self.legs:
            px, py = self.joints[leg["i"]]
            tx, ty, nx, ny = self.frames_cache[leg["i"]]
            # Ideal foot position: out to the side along the normal (nx, ny),
            # times side (+1/-1) and reach, plus a bit forward along the tangent.
            target = (px + nx * leg["s"] * leg["r"] + tx * 18,
                      py + ny * leg["s"] * leg["r"] + ty * 18)
            if leg["foot"] is None:
                leg["foot"] = list(target)      # first frame: place the foot directly
            else:
                dist = math.hypot(leg["foot"][0] - target[0],
                                  leg["foot"][1] - target[1])
                # The foot stays PLANTED until the body drifts more than 42px away,
                # then it glides toward the target. This makes a stepping motion
                # instead of legs that are glued to the body.
                if dist > 42:
                    leg["foot"][0] += (target[0] - leg["foot"][0]) * FOOT_SMOOTH
                    leg["foot"][1] += (target[1] - leg["foot"][1]) * FOOT_SMOOTH

        self.particles.update()

    # ---------- Drawing ----------
    def draw(self, surf):
        # Order matters: later calls are painted on top of earlier ones.
        self._draw_elegant_shadows(surf)
        self._draw_elegant_legs(surf)
        self._draw_luxury_body(surf)
        self._draw_elegant_claws(surf)
        self._draw_stinger(surf)
        self.particles.draw(surf)

    def _draw_elegant_shadows(self, surf):
        # Soft shadow under the body: every 4th joint gets concentric circles.
        # Circles are drawn from big to small, and the brighter (smaller) ones
        # are painted on top, which fakes a blurred gradient.
        for i in range(0, N, 4):
            joint = self.joints[i]
            w = self.width(i)
            for offset in range(int(w * 1.5), 0, -2):
                # Intensity is 0 at the outer edge and grows toward the center
                intensity = int(30 * (1 - offset / (w * 1.5)))
                if intensity > 0:
                    c = (intensity // 3, intensity // 3, intensity // 2)  # dark bluish shade
                    pygame.draw.circle(
                        surf, c,
                        (int(joint[0]) + 3, int(joint[1]) + int(w * 0.8)),  # shifted down-right
                        offset)

    def _draw_elegant_legs(self, surf):
        for leg in self.legs:
            hx, hy = self.joints[leg["i"]]     # hip (attached to the body)
            fx, fy = leg["foot"]               # foot (planted on the ground)
            tx, ty, nx, ny = self.frames_cache[leg["i"]]

            # Knee: halfway between hip and foot, pushed outward (normal) and
            # forward (tangent) so the leg looks bent like a real arthropod leg.
            kx = (hx + fx) / 2 + nx * leg["s"] * 14 + tx * 10
            ky = (hy + fy) / 2 + ny * leg["s"] * 14 + ty * 10

            # Two segments: hip -> knee (thicker), knee -> foot (thinner),
            # each with a thin colored line on top for a highlight.
            pygame.draw.line(surf, COLORS["accent_secondary"], (hx, hy), (kx, ky), 3)
            pygame.draw.line(surf, COLORS["body_highlight"], (hx, hy), (kx, ky), 1)
            pygame.draw.line(surf, COLORS["accent_secondary"], (kx, ky), (fx, fy), 2)
            pygame.draw.line(surf, COLORS["body_midtone"], (kx, ky), (fx, fy), 1)

            # Foot: filled circle + dark outline (last argument 1 = outline width)
            pygame.draw.circle(surf, COLORS["accent_primary"], (int(fx), int(fy)), 4)
            pygame.draw.circle(surf, COLORS["body_shadow"], (int(fx), int(fy)), 5, 1)

    def _draw_luxury_body(self, surf):
        # --- Ribs: short lines across the body, drawn from tail to head ---
        # range(N - 1, 0, -2) walks BACKWARD in steps of 2 so the head side
        # is painted last (on top).
        for i in range(N - 1, 0, -2):
            px, py = self.joints[i]
            nx, ny = self.frames_cache[i][2], self.frames_cache[i][3]
            w = self.width(i)

            # Color zones along the body: bright front, mid section, dark tail
            progress = i / N
            if progress < 0.3:
                color = COLORS["body_highlight"]
            elif progress < 0.6:
                color = COLORS["body_midtone"]
            else:
                color = COLORS["body_shadow"]

            # One line to each side along the normal; its length is the body width
            for s in (-1, 1):
                edge = (px + nx * s * w * 0.8, py + ny * s * w * 0.8)
                pygame.draw.line(surf, color, (px, py), edge, 1)

        # --- Spine: the same polyline drawn 3 times for a 3D metallic look ---
        points = [tuple(j) for j in self.joints]
        shadow_points = [(p[0] + 1, p[1] + 1) for p in points]      # shadow: offset +1px
        pygame.draw.lines(surf, COLORS["body_shadow"], False, shadow_points, 3)
        pygame.draw.lines(surf, COLORS["accent_primary"], False, points, 2)
        highlight_points = [(p[0] - 0.5, p[1] - 0.5) for p in points]  # highlight: offset -0.5px
        pygame.draw.lines(surf, COLORS["body_highlight"], False, highlight_points, 1)

    def _draw_elegant_claws(self, surf):
        # Claws are attached near the head (joint 1) and use its tangent/normal.
        tx, ty, nx, ny = self.frames_cache[1]
        hx, hy = self.joints[1]
        glow_radius = int(20 * self.glow_intensity)   # glow ring grows with movement

        for s in (-1, 1):   # left claw and right claw (mirrored)
            # joint = "elbow": 30px forward, 20px sideways
            joint = (hx + tx * 30 + nx * s * 20, hy + ty * 30 + ny * s * 20)
            # tip = claw end: further forward (58px) but closer to the center (8px)
            # so the two claws curve inward toward each other.
            tip = (hx + tx * 58 + nx * s * 8, hy + ty * 58 + ny * s * 8)

            if glow_radius > 0:
                # Dim the glow color by the intensity so it fades smoothly
                glow_color = tuple(int(c * self.glow_intensity)
                                   for c in COLORS["glow_warm"])
                pygame.draw.circle(surf, glow_color,
                                   (int(tip[0]), int(tip[1])), glow_radius, 1)

            # Shadow (offset by 1px)
            pygame.draw.line(surf, COLORS["body_shadow"],
                             (hx + 1, hy + 1), (joint[0] + 1, joint[1] + 1), 3)
            pygame.draw.line(surf, COLORS["body_shadow"],
                             (joint[0] + 1, joint[1] + 1), (tip[0] + 1, tip[1] + 1), 2)
            # Main color (upper arm thicker than the forearm)
            pygame.draw.line(surf, COLORS["accent_primary"], (hx, hy), joint, 3)
            pygame.draw.line(surf, COLORS["accent_primary"], joint, tip, 2)
            # Highlight
            pygame.draw.line(surf, COLORS["body_highlight"], (hx, hy), joint, 1)
            # Claw tip: big circle with a smaller glowing circle inside
            pygame.draw.circle(surf, COLORS["accent_primary"],
                               (int(tip[0]), int(tip[1])), 5)
            pygame.draw.circle(surf, COLORS["glow_warm"],
                               (int(tip[0]), int(tip[1])), 3)

    def _draw_stinger(self, surf):
        """Curled tail + stinger.

        Idea: start at the last body joint and walk outward in small steps,
        rotating the direction a little at every step. Because the rotation
        angle grows with each step, the points form a spiral-like curl.
        """
        tail = self.joints[N - 1]
        tx, ty, nx, ny = self.frames_cache[N - 1]

        # Flip the tangent so the tail grows AWAY from the head
        dx, dy = -tx, -ty
        # Base curl (radians per step) + a slow sine wobble so the tail "breathes"
        curl = 0.16 + math.sin(self.time * 0.06) * 0.03

        x, y = tail
        pts = [(x, y)]
        for k in range(10):
            a = curl * (1 + k * 0.15)      # angle grows -> tighter curl near the tip
            c, s = math.cos(a), math.sin(a)
            # 2D rotation of the direction vector (dx, dy) by angle a:
            #   dx' = dx*cos(a) - dy*sin(a)
            #   dy' = dx*sin(a) + dy*cos(a)
            dx, dy = dx * c - dy * s, dx * s + dy * c
            x += dx * 7                    # advance 7px in the new direction
            y += dy * 7
            pts.append((x, y))

        # Draw the tail segment by segment with decreasing thickness:
        # k // 2 is integer division, so the width drops by 1 every 2 segments;
        # max(2, ...) stops it from getting thinner than 2px.
        for k in range(len(pts) - 1):
            w = max(2, 6 - k // 2)
            p, q = pts[k], pts[k + 1]
            pygame.draw.line(surf, COLORS["body_shadow"],
                             (p[0] + 1, p[1] + 1), (q[0] + 1, q[1] + 1), w + 1)
            pygame.draw.line(surf, COLORS["accent_primary"], p, q, w)
            pygame.draw.line(surf, COLORS["body_highlight"], p, q, 1)

        # The swollen venom bulb at the end of the tail
        ex, ey = pts[-1]
        pygame.draw.circle(surf, COLORS["accent_primary"], (int(ex), int(ey)), 6)
        pygame.draw.circle(surf, COLORS["glow_warm"], (int(ex), int(ey)), 3)

        # The sharp stinger = a thin triangle.
        # (px, py) is the PERPENDICULAR of the direction (dx, dy): rotating a
        # vector by 90 degrees gives (-dy, dx). It spreads the triangle's base
        # to the left/right of the tail's axis.
        px, py = -dy, dx
        tip = (ex + dx * 16, ey + dy * 16)     # 16px ahead along the direction
        left = (ex + px * 4, ey + py * 4)      # base corner on one side
        right = (ex - px * 4, ey - py * 4)     # base corner on the other side
        pygame.draw.polygon(surf, COLORS["body_highlight"], [left, tip, right])
        pygame.draw.polygon(surf, COLORS["glow_warm"], [left, tip, right], 1)  # outline


# ========== Background grid ==========
def draw_grid(surf):
    # Faint vertical and horizontal lines every 50px across the whole window
    for x in range(0, W, 50):
        pygame.draw.line(surf, COLORS["grid_subtle"], (x, 0), (x, H), 1)
    for y in range(0, H, 50):
        pygame.draw.line(surf, COLORS["grid_subtle"], (0, y), (W, y), 1)


# ========== Main loop ==========
def main():
    scorpion = ScorpionLuxury(W // 2, H // 2)   # start in the screen center
    running = True

    while running:
        # Handle the window close button and the ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # The scorpion chases the mouse position every frame
        mouse = pygame.mouse.get_pos()
        scorpion.update(mouse)

        # Draw order: background -> grid -> scorpion -> UI text on top
        screen.fill(COLORS["bg"])
        draw_grid(screen)
        scorpion.draw(screen)

        # clock.get_fps() returns the measured FPS over the last frames
        info = font_info.render(f"FPS: {int(clock.get_fps())}  |  ESC to quit",
                                True, COLORS["accent_secondary"])
        screen.blit(info, (10, 10))

        # flip() shows the finished frame; clock.tick(FPS) caps the frame rate
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
