import pygame, math

def cosd(a):
    return math.cos(a*math.pi/180)

def sind(a):
    return math.sin(a*math.pi/180)

class Sphere:
    def __init__(self, p, r, c, g):
        self.position = p
        self.radius = r
        self.color = c
        self.glossyness = g

    def collided(self, p0, p):
        return True if math.sqrt((self.position[0]-p[0])**2+(self.position[1]-p[1])**2+(self.position[2]-p[2])**2) < self.radius else False

    def color_at(self, p):
        return self.color

class Box:
    def __init__(self, p, s, c):
        self.position = p
        self.scale = s
        self.color = c

    def collided(self, p0, p):
        return True if abs(self.position[0]-p[0]) < self.scale[0]/2 and abs(self.position[1]-p[1]) < self.scale[1]/2 and abs(self.position[2]-p[2]) < self.scale[2]/2 else False

    def color_at(self, p):
        return self.color

class Plane:
    def __init__(self, p, s, c0, c1):
        self.position = p
        self.scale = s
        self.colors = (c0, c1)

    def collided(self, p0, p1):
        return True if p0[1] > self.position[1] and p1[1] < self.position[1] and abs(self.position[0]-p1[0]) < self.scale[0]/2 and abs(self.position[2]-p1[2]) < self.scale[2]/2 else False

    def color_at(self, p):
        return self.colors[int((int(self.position[0]-p[0])+int(self.position[2]-p[2]))%2)]

class Light:
    def __init__(self, p, i, r):
        self.position = p
        self.intensity = i
        self.max_range = r

class Camera:
    def __init__(self, p, r, f):
        self.position = p
        self.rotation = r
        self.fov = f

def vector_combine(v0, v1, d):
    return (v0[0]+(v1[0]-v0[0])*d, v0[1]+(v1[1]-v0[1])*d, v0[2]+(v1[2]-v0[2])*d)

def normalize(v):
    l = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return (v[0]/l, v[1]/l, v[2]/l)

class Scene:
    def __init__(self, c, o, l, b):
        self.cameras = c
        self.objects = o
        self.lights = l
        self.bg_color = b

    def add_object(self, o):
        self.objects.append(o)

    def add_light(self, l):
        self.lights.append(l)

    def collided(self, p0, p1):
        for o in self.objects:
            if o.collided(p0, p1):
                return o
        return None

    def trace_ray(self, c, d, a, m, ab):
        color = self.bg_color
        brightness = ab #ambient brightness
        max_iters = int(m/a)
        ray_pos = self.cameras[c].position
        last_pos = ray_pos
        cr = self.cameras[c].rotation
        fov = self.cameras[c].fov
        cr = (cr[0]-(d[1]-0.5)*fov[1], cr[1]+(d[0]-0.5)*fov[0], cr[0])
        ray_dir = (a*sind(cr[1])*cosd(cr[0]),
                   a*sind(cr[0]),
                   a*cosd(cr[1])*cosd(cr[0]))
        for i in range(max_iters):
            ray_pos = (ray_pos[0]+ray_dir[0], ray_pos[1]+ray_dir[1], ray_pos[2]+ray_dir[2])
            o = self.collided(last_pos, ray_pos)
            if not o == None:
                #if not type(o) == Plane:
                #    print(type(o))
                color = o.color_at(ray_pos)
                for l in self.lights:
                    dist = math.sqrt((l.position[0]-ray_pos[0])**2+(l.position[1]-ray_pos[1])**2+(l.position[2]-ray_pos[2])**2)
                    if dist < l.max_range:
                        lr2p = last_pos
                        r2p = last_pos
                        r2d = normalize((l.position[0]-ray_pos[0], l.position[1]-ray_pos[1], l.position[2]-ray_pos[2]))
                        r2d = (r2d[0]*a, r2d[1]*a, r2d[2]*a)
                        works = True
                        for i0 in range(int(dist/a)):
                            r2p = (r2p[0]+r2d[0], r2p[1]+r2d[1], r2p[2]+r2d[2])
                            if self.collided(lr2p, r2p):
                                works = False
                                break
                            lr2p = r2p
                        brightness += l.intensity*((1-dist/l.max_range)**2)*works
                break ###temporary break until reflections etc. are implemented
            last_pos = ray_pos
        return (color[0]*brightness, color[1]*brightness, color[2]*brightness)

def test_scene():
    return Scene([Camera((-3, 1, 2), (-22.5, 45, 0), (90, 45))],
                  [Plane((0, -1, 0), (10, 0, 10), (0, 0, 0), (255, 255, 255)),
                   Box((-1, -0.5, 4), (1, 1, 1), (127, 255, 127)),
                   Sphere((1, -0.5, 4), 0.5, (255, 127, 0), 0)],
                  [Light((5, 5, 3), 1, 20)],
                  (0, 127, 255))

size = (512, 256)
pygame.init()
surface = pygame.display.set_mode(size)
pygame.display.set_caption("Raytracing Test")
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(30)
    scene = test_scene()
    for x in range(size[0]):
        for y in range(size[1]):
            surface.set_at((x, y), scene.trace_ray(0, (x/size[0], y/size[1]), 0.01, 20, 0.125))
    pygame.display.flip()
