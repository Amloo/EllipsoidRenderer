import pygame
import math
import numpy
import copy

FOV = 5
RENDER_DISTANCE = 50

pygame.init()
screen = pygame.display.set_mode((320, 240))
clock = pygame.time.Clock()
running = True

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Transform:
    def __init__(self, position, rotation, scale):
        self.position = position
        self.rotation = rotation
        self.scale = scale

    def translate(self, x, y, z):
        return Transform(Vector3(self.position.x + x, self.position.y + y, self.position.z + z), self.rotation, self.scale)

    def rotate(self, x, y, z):
        return Transform(self.position, Vector3(self.rotation.x + x, self.rotation.y + y, self.rotation.z + z), self.scale)

    def rescale(self, x, y, z):
        return Transform(self.position, self.rotation, Vector3(self.scale.x * x, self.scale.y * y, self.scale.z * z))

def rotate_x(v, a):
    ca = math.cos(a)
    sa = math.sin(a)
    return Vector3(v.x, v.y * ca - v.z * sa, v.y * sa + v.z * ca)

def rotate_y(v, a):
    ca = math.cos(a)
    sa = math.sin(a)
    return Vector3(v.x * ca + v.z * sa, v.y, -v.x * sa + v.z * ca)

def rotate_z(v, a):
    ca = math.cos(a)
    sa = math.sin(a)
    return Vector3(v.x * ca - v.y * sa, v.x * sa + v.y * ca, v.z)

class Ellipsoid:
    def __init__(self, position, rotation, scale, color):
        self.transform = Transform(position, rotation, scale)
        self.c = color

class GameObject:
    def __init__(self, transform, ellipsoids):
        self.transform = transform
        self.ellipsoids = ellipsoids

def normalize(vector):
    magnitude = math.sqrt(pow(vector.x, 2) + pow(vector.y, 2) + pow(vector.z, 2))
    return Vector3(vector.x / abs(magnitude), vector.y / abs(magnitude), vector.z / abs(magnitude))

def ndcX(x, w):
    return ((2 * (x + 0.5)) / w) - 1

def ndcY(y, h):
    return 1 - ((2 * (y + 0.5)) / h)

def ray(origin, direction, length, ellipsoids):
    for i in ellipsoids:
        P = Vector3(origin.x - i.transform.position.x, origin.y - i.transform.position.y, origin.z - i.transform.position.z)

        D = Vector3(direction.x, direction.y, direction.z)
        
        r = i.transform.rotation
        P = rotate_x(P, -r.x)
        P = rotate_y(P, -r.y)
        P = rotate_z(P, -r.z)

        D = rotate_x(D, -r.x)
        D = rotate_y(D, -r.y)
        D = rotate_z(D, -r.z)

        sx = i.transform.scale.x
        sy = i.transform.scale.y
        sz = i.transform.scale.z

        P = Vector3(P.x / sx, P.y / sy, P.z / sz)
        D = Vector3(D.x / sx, D.y / sy, D.z / sz)

        A = D.x * D.x + D.y * D.y + D.z * D.z
        B = 2 * (P.x * D.x + P.y * D.y + P.z * D.z)
        C = (P.x * P.x + P.y * P.y + P.z * P.z) - 1
        
        discriminant = B * B - 4 * A * C

        if(discriminant < 0):
            continue

        t1 = ((0 - B) - math.sqrt(discriminant)) / (2 * A)
        t2 = ((0 - B) + math.sqrt(discriminant)) / (2 * A)

        if(t1 >= 0 and t2 >= 0):
            t = min(t1, t2)
        elif(t1 >= 0):
            t = t1
        elif(t2 >= 0):
            t = t2
        else:
            continue

        return i.c

    return pygame.Color(0, 0, 0, 0)

def objectTransform(transform, ellipsoids):
    for i in ellipsoids:
        i.transform = i.transform.translate(transform.position.x, transform.position.y, transform.position.z)
        i.transform = i.transform.rotate(transform.rotation.x, transform.rotation.y, transform.rotation.z)
        i.transform = i.transform.rescale(transform.scale.x, transform.scale.y, transform.scale.z)
    return ellipsoids

def viewTransform(transform, ellipsoids):
    for i in ellipsoids:
        r = camera.rotation
        i.transform = i.transform.rotate(-r.x, -r.y, -r.z)
        p = camera.position
        i.transform = i.transform.translate(-p.x, -p.y, -p.z)
    return ellipsoids

def perspectiveProjection(ellipsoids):
    buffer = pygame.surfarray.pixels2d(screen)
    for i in range(1, 320):
        for j in range(1, 240):
            buffer[i][j] = ray(camera.position, normalize(Vector3(ndcX(i, 320), ndcY(j, 240), FOV)), RENDER_DISTANCE, ellipsoids)
    del buffer

camera = Transform(Vector3(0, 0, -25), Vector3(0, 0, 0), Vector3(1, 1, 1))
character = GameObject(Transform(Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(1, 1, 1)), [
    Ellipsoid(Vector3(0, 0, 0), Vector3(0, 0, 0), Vector3(3, 3, 3), pygame.Color(255, 0, 0)),
    Ellipsoid(Vector3(5, 5, 0), Vector3(90, 90, 0), Vector3(5, 1, 1), pygame.Color(0, 255, 0))])

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera = camera.translate(0, 0, 1)
    if keys[pygame.K_a]:
        camera = camera.translate(-1, 0, 0)
    if keys[pygame.K_s]:
        camera = camera.translate(0, 0, -1)
    if keys[pygame.K_d]:
        camera = camera.translate(1, 0, 0)
    if keys[pygame.K_UP]:
        camera = camera.rotate(0, 0, 1)
    if keys[pygame.K_LEFT]:
        camera = camera.rotate(-1, 0, 0)
    if keys[pygame.K_DOWN]:
        camera = camera.rotate(0, 0, -1)
    if keys[pygame.K_RIGHT]:
        camera = camera.rotate(1, 0, 0)

    screen.fill("black")

    objectSpace = copy.deepcopy(character.ellipsoids)
    worldSpace = objectTransform(character.transform, objectSpace)
    #cameraSpace = viewTransform(camera, worldSpace)
    perspectiveProjection(worldSpace)
    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
