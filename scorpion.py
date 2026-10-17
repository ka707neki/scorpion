import pygame, math, sys

W, H = 900, 650
N, D = 110, 6            # عدد الفقرات والمسافة بينها
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Scorpion Cursor")
clock = pygame.time.Clock()

joints = [[W/2 - i*D, H/2] for i in range(N)]

def width(i):
    t = i / (N - 1)
    if t < 0.36:                      # الجسم
        return 6 + 24*math.sin(t/0.36*math.pi)**0.6
    return 3 + 13*(1 - (t-0.36)/0.64)**1.2   # الذيل

legs = []
for idx, reach in ((8, 62), (14, 72), (20, 68), (26, 58)):
    for side in (-1, 1):
        legs.append({"i": idx, "s": side, "r": reach, "foot": None})

def frame_at(i):
    a = joints[max(i-1, 0)]
    b = joints[min(i+1, N-1)]
    tx, ty = a[0]-b[0], a[1]-b[1]
    m = math.hypot(tx, ty) or 1
    tx, ty = tx/m, ty/m
    return tx, ty, -ty, tx      # الاتجاه الأمامي ثم العمودي

def update(mouse):
    hx, hy = joints[0]
    dx, dy = mouse[0]-hx, mouse[1]-hy
    d = math.hypot(dx, dy)
    if d > 25:
        sp = min(7, d*0.08)
        joints[0][0] += dx/d*sp
        joints[0][1] += dy/d*sp
    for i in range(1, N):
        p, q = joints[i-1], joints[i]
        dx, dy = q[0]-p[0], q[1]-p[1]
        m = math.hypot(dx, dy) or 1
        q[0] = p[0] + dx/m*D
        q[1] = p[1] + dy/m*D
    for L in legs:
        px, py = joints[L["i"]]
        tx, ty, nx, ny = frame_at(L["i"])
        target = (px + nx*L["s"]*L["r"] + tx*18, py + ny*L["s"]*L["r"] + ty*18)
        if L["foot"] is None:
            L["foot"] = list(target)
        elif math.hypot(L["foot"][0]-target[0], L["foot"][1]-target[1]) > 42:
            L["foot"][0] += (target[0]-L["foot"][0])*0.5
            L["foot"][1] += (target[1]-L["foot"][1])*0.5

def draw():
    screen.fill((0, 0, 0))
    for L in legs:                                   # الأرجل
        hx, hy = joints[L["i"]]
        fx, fy = L["foot"]
        tx, ty, nx, ny = frame_at(L["i"])
        kx = (hx+fx)/2 + nx*L["s"]*14 + tx*10
        ky = (hy+fy)/2 + ny*L["s"]*14 + ty*10
        pygame.draw.line(screen, (150,150,150), (hx,hy), (kx,ky), 2)
        pygame.draw.line(screen, (150,150,150), (kx,ky), (fx,fy), 2)
        pygame.draw.circle(screen, (220,220,220), (int(fx),int(fy)), 3)
    for i in range(N-1, -1, -1):                     # الأضلاع
        px, py = joints[i]
        tx, ty, nx, ny = frame_at(i)
        w = width(i)
        sweep = w*0.9
        g = int(70 + 150*(1 - i/N))
        for s in (-1, 1):
            e = (px + nx*s*w - tx*sweep, py + ny*s*w - ty*sweep)
            pygame.draw.line(screen, (g,g,g), (px,py), e, 1)
    pygame.draw.lines(screen, (235,235,235), False, [tuple(j) for j in joints], 2)
    tx, ty, nx, ny = frame_at(1)                     # الكلابات
    hx, hy = joints[1]
    for s in (-1, 1):
        a = (hx + tx*30 + nx*s*20, hy + ty*30 + ny*s*20)
        b = (hx + tx*58 + nx*s*8,  hy + ty*58 + ny*s*8)
        pygame.draw.line(screen, (200,200,200), (hx,hy), a, 2)
        pygame.draw.line(screen, (200,200,200), a, b, 2)
        pygame.draw.circle(screen, (255,255,255), (int(b[0]),int(b[1])), 3)

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    update(pygame.mouse.get_pos())
    draw()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()