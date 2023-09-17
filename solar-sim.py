from random import randint
import pygame
import math

pygame.init()
pygame.display.set_caption("Solar System Simulation")

WIDTH = HEIGHT = 1000
FPS = 60

WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
ORANGE = (255, 165, 0)
GREY = (100, 118, 102)
DARK_GREY = (40,40,40)
LIGHT_GREY = (130,130,130)

AU = 149.6e6 * 1000

FONT = pygame.font.SysFont("Arial", 16)

scale = 250 / AU
move_camera_by = AU/30
time_setting = 0
draw_dist_line = True
draw_names = True
spawned_object_count = 0


G = 6.67428e-11
SCALE_ORIGINAL = scale
time = 3600*24


clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH,HEIGHT))

running = True
paused = False

#pixels, kgs

sun_radius, sun_mass = 30, 1.98892 * 10**30
earth_radius,earth_mass =  16, 5.9742 * 10**24
mars_radius,mars_mass = 12, 6.39 * 10**23
venus_radius,venus_mass = 14, 4.8685 * 10**24
mercury_radius,mercury_mass = 8, 3.30 * 10**23
jupiter_radius,jupiter_mass = 20,1.898 * 10**27
saturn_radius, saturn_mass = 18, 5.683 * 10**26
neptune_radius, neptune_mass = 12, 1.024 * 10**26
uranus_radius, uranus_mass = 12, 8.6 * 10**25

class Planet:
    def __init__(self,name,x,y,r,mass,color,vel_y):
        self.name = "Spawned Object"
        if len(name) != 0:
            self.name = name
        self.x = x
        self.y = y
        self.radius = r
        self.is_sun = False
        self.is_selected = False
        self.color = color
        self.mass = mass
        self.distance_to_sun = 0

        self.x_corrected = self.x * scale + WIDTH//2
        self.y_corrected = self.y * scale + WIDTH//2
        
        self.orbit = []
        self.vel_y_start = vel_y
        self.vel_x = 0
        self.vel_y = vel_y

    def draw(self):
        x = self.x * scale + WIDTH//2
        y = self.y * scale + WIDTH//2
        pygame.draw.circle(window,self.color,(x,y), self.radius*scale*10e7)
        if not self.is_sun and draw_names:
            name = FONT.render(self.name,1,WHITE)
            window.blit(name, (x,y))
        if len(self.orbit) > 2:
            corrected_points = []
            orbit_points_limit = 400 #200*(self.x/AU) #DO ZMIANY
            if len(self.orbit) > orbit_points_limit and not paused:
                self.orbit.pop(0)
            for point in self.orbit:
                x, y = point
                x_y_corrected = [x*scale+WIDTH//2, y*scale+HEIGHT//2]
                corrected_points.append(x_y_corrected)
            pygame.draw.lines(window, self.color, False, corrected_points)
        
    def draw_to_obj(self,other):
        if draw_dist_line:
            pygame.draw.line(window,WHITE,(self.x * scale + WIDTH//2, self.y * scale + HEIGHT//2), (other.x * scale + WIDTH//2, other.y * scale + HEIGHT//2))

    def draw_menu(self):
        name = FONT.render(f"Name: {self.name}",1,WHITE)
        distance = FONT.render(f"Distance: {round(self.distance_to_sun/1000)}km",1,WHITE)
        mass = FONT.render(f"Mass: {round(self.mass/10e22)} x 10^22 kg",1,WHITE)
        velocity = FONT.render(f"Velocity (avr): {round(self.vel_y_start/1000)} km/s",1,WHITE)
        blit = [name, distance, mass,velocity]
        x_pos = 6
        y_pos = 4
        menu_height = 20*len(blit)+10
        pygame.draw.rect(window,LIGHT_GREY,pygame.Rect(0, 0, 200,menu_height), 0,3)
        pygame.draw.rect(window,DARK_GREY,pygame.Rect(0, 0, 200,menu_height), 2,3)
        for b in blit:
            window.blit(b, (x_pos, y_pos))
            y_pos += 20
        y_pos = 0

    def gravity(self, other):
        distance = math.sqrt(math.pow((self.x-other.x),2)+math.pow((self.y-other.y),2))
        if other.is_sun:
            self.distance_to_sun = distance
        if self.distance_to_sun < sun.radius and not self.is_sun:
            bodies.remove(self)
        force = G*self.mass*other.mass / distance**2
        angle = math.atan2((other.y-self.y), (other.x-self.x))
        force_x = math.cos(angle)*force
        force_y = math.sin(angle)*force
        return force_x, force_y
        
    def update_pos(self,planets):
        total_x = total_y = 0
        for planet in planets:
            if self == planet:
                continue
            fx,fy = self.gravity(planet)
            total_x += fx
            total_y += fy
        self.vel_x += total_x * time / self.mass
        self.vel_y += total_y * time / self.mass

        self.x += self.vel_x * time
        self.y += self.vel_y * time
        self.orbit.append([self.x,self.y])

sun = Planet("sun",0,0,sun_radius,sun_mass,WHITE,0)
sun.is_sun = True
mercury = Planet("mercury",0.387 * AU, 0, mercury_radius, mercury_mass,GREY,47.4 * 1000)
earth = Planet("earth",AU,0,earth_radius,earth_mass,BLUE,29.783*1000)
venus = Planet("venus",0.723 * AU,0,venus_radius,venus_mass,ORANGE,35.02*1000)
mars = Planet("mars",1.524 * AU,0,mars_radius,mars_mass,RED,24.077*1000)
jupiter = Planet("jupiter",5.2*AU,0, jupiter_radius, jupiter_mass, ORANGE,13.72*1000)
saturn = Planet("saturn",9.5*AU,0, saturn_radius, saturn_mass, GREY,9.69*1000)
uranus = Planet("uranus",19.2*AU,0, uranus_radius, uranus_mass, WHITE, 6.71*1000)
neptune = Planet("neptune",30.1*AU,0,neptune_radius, neptune_mass, BLUE,5.43*1000)

mouse_pos_scale = 1

bodies = [sun,mercury,venus,earth,mars,jupiter,saturn,uranus,neptune]

def scatter_stars():
    coords = []
    for z in range(120):
        x = int(randint(0,WIDTH))
        y = int(randint(0,HEIGHT))
        coords.append((x,y))
    return coords

scattered_coords = scatter_stars()

def draw_stars(coords):
    for xy in coords:
        pygame.draw.circle(window,WHITE,xy,1)

def draw_timestep():
    pygame.draw.rect(window,LIGHT_GREY,pygame.Rect(WIDTH-88, 0, WIDTH,20), 0,3)
    pygame.draw.rect(window,DARK_GREY,pygame.Rect(WIDTH-88, 0, WIDTH,20), 2,3)
    timestep = FONT.render(f"Timestep: {time_setting}", 2, WHITE,)
    window.blit(timestep,(WIDTH-84,0))

def handle_inputs():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        for body in bodies:
            for point in body.orbit:
                point[1] += move_camera_by
            body.y += move_camera_by
    if keys[pygame.K_s]:
        for body in bodies:
            for point in body.orbit:
                point[1] -= move_camera_by
            body.y -= move_camera_by
    if keys[pygame.K_d]:
        for body in bodies:
            for point in body.orbit:
                point[0] -= move_camera_by
            body.x -= move_camera_by
    if keys[pygame.K_a]:
        for body in bodies:
            for point in body.orbit:
                point[0] += move_camera_by
            body.x += move_camera_by
    if keys[pygame.K_x]:
        x,y = pygame.mouse.get_pos()
        x,y =((x-WIDTH/2)/250)*AU*mouse_pos_scale, ((y-HEIGHT/2)/250)*AU*mouse_pos_scale
        bodies.append(Planet("",x,y,randint(5,20), randint(2*10**23, 3*10**24),(randint(0,255),randint(0,255),randint(0,255)), randint(8000,15000)))

while running:
    clock.tick(FPS)
    handle_inputs()
    window.fill((0,0,0))
    draw_stars(scattered_coords)
    for body in bodies:
        if body.distance_to_sun > 100*AU:
            bodies.remove(body)
        if not paused:
            body.update_pos(bodies)
        body.draw()
        if not body.is_sun:
            body.draw_to_obj(sun)
    for body in bodies:
        if body.is_selected:
            body.draw_menu()
    draw_timestep()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_UP:
                if time_setting < 10:
                    time *= 1.25
                    time_setting += 1
            if event.key == pygame.K_DOWN:
                if time_setting > -10:
                    time /= 1.25
                    time_setting -= 1
            if event.key == pygame.K_o:
                draw_dist_line = not draw_dist_line
            if event.key == pygame.K_n:
                draw_names = not draw_names
            if event.key == pygame.K_r:
                scale = SCALE_ORIGINAL
                move_camera_by = AU/30
                time_setting = 0
                draw_dist_line = True
                draw_names = True
                spawned_object_count = 0
                paused = False
                time = 3600*24
                sun = Planet("sun",0,0,sun_radius,sun_mass,WHITE,0)
                sun.is_sun = True
                earth = Planet("earth",AU,0,earth_radius,earth_mass,BLUE,29.783*1000)
                mars = Planet("mars",1.524 * AU,0,mars_radius,mars_mass,RED,24.077*1000)
                venus = Planet("venus",0.723 * AU,0,venus_radius,venus_mass,ORANGE,35.02*1000)
                mercury = Planet("mercury",0.387 * AU, 0, mercury_radius, mercury_mass,GREY,47.4 * 1000)
                jupiter = Planet("jupiter",5.2*AU,0, jupiter_radius, jupiter_mass, ORANGE,13.72*1000)
                saturn = Planet("saturn",9.5*AU,0, saturn_radius, saturn_mass, GREY,9.69*1000)
                neptune = Planet("neptune",30.1*AU,0,neptune_radius, neptune_mass, BLUE,5.43*1000)
                uranus = Planet("uranus",19.2*AU,0, uranus_radius, uranus_mass, WHITE, 6.71*1000)
                mouse_pos_scale = 1
                bodies = [sun, earth, mars, venus, mercury, jupiter,saturn,uranus,neptune]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                scale *= 1.25
                move_camera_by *= 0.9
                mouse_pos_scale /= 1.25
            if event.button == 5:
                scale /= 1.25
                move_camera_by /= 0.9
                mouse_pos_scale *= 1.25
            if event.button == 2:
                x,y = pygame.mouse.get_pos()
                x,y =((x-WIDTH/2)/250)*AU*mouse_pos_scale, ((y-HEIGHT/2)/250)*AU*mouse_pos_scale
                bodies.append(Planet("",x,y,randint(5,20), randint(2*10**23, 3*10**24),(randint(0,255),randint(0,255),randint(0,255)), randint(8000,15000)))
            if event.button == 1:
                x,y = pygame.mouse.get_pos()
                x,y =((x-WIDTH/2)/250)*AU*mouse_pos_scale, ((y-HEIGHT/2)/250)*AU*mouse_pos_scale
                for body in bodies:
                    if abs(body.x - x) < 10e9 and abs(body.y - y) < 10e9:
                        body.is_selected = True
                        break
                    else:
                        for body in bodies:
                            body.is_selected = False