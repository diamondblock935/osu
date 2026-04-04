import math
import pygame
import random
import json
from open_lvl import load_level


pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
smol_font = pygame.font.SysFont('Arial', 23)
Chonky_font = pygame.font.SysFont('Arial', 32)

running = True
score = 0
combo = 0
fps = 60
difficulty = 8
mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
score_popup_timer = 0
score_popup_pos = (0, 0)
score_add_text = None
status = "menu"
level_start_time = 0

# def position(radius):
#         pos = [random.randint(radius,width - radius) , random.randint(radius, height - radius)]
#         return pos


def Main():
    screen.fill((0,0,0))
    
    Osu = Chonky_font.render("Osu", True, (0,106,255))
    play = smol_font.render("Press ENTER to play or press Q to exit", True, (255,255,255))
    
    screen.blit(Osu, (width / 2 - Osu.get_width() // 2, height / 3))
    screen.blit(play, (width / 2 - play.get_width() // 2, height / 2))
    
    pygame.display.flip()
    

class Circle():
    def __init__(self, color, text_col, text, pos, radius, start_time):
        self.finished = False
        self.active = False
        self.circle_pos = pos
        self.radius = radius
        self.text = text
        self.color = color
        self.text_col = text_col
        self.start_time = start_time
        self.original_color = self.color

    

    def draw(self):
        pygame.draw.circle(screen,self.color , self.circle_pos, self.radius)

        self.innertext = Chonky_font.render(self.text, True, self.text_col)
        self.textPos = self.innertext.get_rect(center = self.circle_pos)
        screen.blit(self.innertext, self.textPos)

        if circle_approach[circles.index(self)].radius <= self.radius - 15:
            self.click(None)

    def handle_event(self, event):
        global mouse_pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                if mouse_pos.distance_to(self.circle_pos) <= self.radius:
                    self.click(event)
                    
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                self.color = self.original_color

    def click(self, event):
        global score, combo, score_popup_timer, score_popup_pos, score_add_text
        
        if circle_approach[circles.index(self)].radius - self.radius >= 32 or circle_approach[circles.index(self)].radius <= self.radius - 10:
            self.score_add = 'x'
            score_add_text = smol_font.render(self.score_add, True, "red")
            combo = 0

        elif circle_approach[circles.index(self)].radius - self.radius <= 7:
            self.score_add = 300
            score_add_text = smol_font.render(str(self.score_add), True, "cyan")

        elif circle_approach[circles.index(self)].radius - self.radius <= 21:
            self.score_add = 100
            score_add_text = smol_font.render(str(self.score_add), True, "green")

        elif circle_approach[circles.index(self)].radius - self.radius <= 32:
            self.score_add = 50
            score_add_text = smol_font.render(str(self.score_add), True, "yellow")

        if type(self.score_add) == int:
            score += self.score_add + self.score_add * combo / 10
            combo += 1
            
        score_popup_timer = 20
        score_popup_pos = (self.circle_pos[0] -score_add_text.get_width() // 2, self.circle_pos[1] - score_add_text.get_height() // 2)
        self.finished = True
        circle_approach[circles.index(self)].finished = True
        # self.circle_pos = position(self.radius)
        # circle_approach[circles.index(self)].pos = self.circle_pos
        # circle_approach[circles.index(self)].radius = 100

        

class Approach_Circle():
    def __init__(self, color, pos, radius):
        self.finished = False
        self.radius = radius
        self.pos = pos
        self.color = color


    def draw(self):
        pygame.draw.circle(screen,self.color , self.pos, self.radius, 3)
        self.radius -= 10 * difficulty / fps
        # if self.radius <= 40:
        #     Circle.click(circles[approach_circles.index(self)], None)
        #     self.radius = 100


class slider():
    def __init__(self, color, start_pos, end_pos, duration, start_time):
        self.finished = False
        self.active = False
        self.color = color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.start_time = start_time
        self.progress = 0
        self.slider_ball_pos = self.start_pos

    def slide(self, event):
        global time_elapsed
        self.progress = (time_elapsed - self.start_time) / self.duration
        self.progress = max(0, min(1, self.progress)) 
        self.slider_ball_pos = pygame.Vector2(self.start_pos).lerp(self.end_pos, self.progress)
        if self.progress >= 1:
            self.click(event)
            self.finished = True
            slider_approach[sliders.index(self)].finished = True
            
    
    def click(self, event):
        global score, combo, score_popup_timer, score_popup_pos, score_add_text
        
        if self.progress >= 0.95:
            self.score_add = 300
            score_add_text = smol_font.render(str(self.score_add), True, "cyan")
        elif self. progress >= 0.85:
            self.score_add = 100
            score_add_text = smol_font.render(str(self.score_add), True, "green")
        elif self.progress >= 0.7:
            self.score_add = 50
            score_add_text = smol_font.render(str(self.score_add), True, "yellow")
        else:
            self.score_add = 'x'
            score_add_text = smol_font.render(self.score_add, True, "red")
            combo = 0

        
        if type(self.score_add) == int:
            score += self.score_add + self.score_add * combo / 5
            combo += 1
            
        score_popup_timer = 20
        score_popup_pos = (self.end_pos[0] -score_add_text.get_width() // 2, self.end_pos[1] - score_add_text.get_height() // 2)

    def handle_event(self, event):
        global mouse_pos, time_elapsed
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_x] or keys[pygame.K_z]) and mouse_pos.distance_to(self.slider_ball_pos) <= 70 and self.progress != 1:
            slider_approach[sliders.index(self)].radius = 0
            pygame.draw.circle(screen, "cyan", self.slider_ball_pos, 70, 3)
            
        elif time_elapsed > self.start_time + self.duration / 5:
            self.click(event)
            slider_approach[sliders.index(self)].finished = True
            self.finished = True
            
        if event.type == pygame.KEYUP and mouse_pos.distance_to(self.slider_ball_pos) <= 50:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                self.click(event)
                slider_approach[sliders.index(self)].finished = True
                self.finished = True
        if event.type == pygame.KEYDOWN and mouse_pos.distance_to(self.slider_ball_pos) <= 50:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                slider_approach[sliders.index(self)].radius = 0
        

    def draw(self):

        start = pygame.Vector2(self.start_pos)
        end = pygame.Vector2(self.end_pos)
        

        direction = (end - start).normalize()
        perpendicular = pygame.Vector2(-direction.y, direction.x) * 50

        p1 = start + perpendicular
        p2 = start - perpendicular
        p3 = end - perpendicular
        p4 = end + perpendicular

        pygame.draw.line(screen, self.color, self.start_pos, self.end_pos, 100)
        pygame.draw.polygon(screen, self.color, [p1, p2, p3, p4])
        pygame.draw.circle(screen, "white", self.start_pos, 50)
        pygame.draw.circle(screen, "white", self.end_pos, 50)

        pygame.draw.circle(screen, "green", self.slider_ball_pos, 50)

        if slider_approach[sliders.index(self)].radius > 0 and slider_approach[sliders.index(self)].radius <= 40:
            self.click(event)
            slider_approach[sliders.index(self)].finished = True
            self.finished = True

       

sliders = []
circles = []
all_objects = []
circle_approach = []
slider_approach = []

lvl_1 = load_level('lvl1.txt')

for i in lvl_1["objects"]:
    if i["type"] == "circle":
        circles.append(Circle("white", "black", str(i["text"]), i["pos"], i["radius"], i["start_time"]))
    elif i["type"] == "slider":
        sliders.append(slider("white", i["start_pos"], i["end_pos"], i["duration"], i["start_time"]))
    
all_objects.extend(circles)
all_objects.extend(sliders)
all_objects.sort(key=lambda x: x.start_time)

for i in sliders:
    slider_approach.append(Approach_Circle("white", i.start_pos, 100))

for i in circles:
    circle_approach.append(Approach_Circle("white", i.circle_pos, 100))



while running:
    

    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    if status == "menu":
        Main()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                elif event.key == pygame.K_RETURN:
                    status = "running"
                    level_start_time = pygame.time.get_ticks()
    if status == "running":
        time_elapsed = pygame.time.get_ticks() - level_start_time

        sliders = [s for s in sliders if s.finished == False]
        circles = [c for c in circles if c.finished == False]
        slider_approach = [a for a in slider_approach if a.finished == False]
        circle_approach = [a for a in circle_approach if a.finished == False]
        all_objects = [o for o in all_objects if o.finished == False]

        

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    running = False
                if event.key == pygame.K_m:
                    status = "menu"
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

            for i in circles:
                if i.active:
                    i.handle_event(event)
            for i in sliders:
                if i.active:
                    i.handle_event(event)

        if len(all_objects) > 0:
            all_objects[0].active = True

        
        
        pygame.display.flip()
        screen.fill("black")
        for i in sliders:
            if not i.finished and time_elapsed >= i.start_time - 4000 * difficulty / fps:
                i.draw()
                i.slide(event)
        for i in circles:
            if not i.finished and time_elapsed >= i.start_time - 4000 * difficulty / fps:
                i.draw()
        for s in slider_approach:
            if sliders[slider_approach.index(s)].start_time - 4000 * difficulty / fps <= time_elapsed:
                s.draw()
        for i in circle_approach:
            if circles[circle_approach.index(i)].start_time - 4000 * difficulty / fps <= time_elapsed:
                i.draw()

        
        if score_popup_timer > 0:
            score_popup_timer -= 1
            screen.blit(score_add_text, score_popup_pos)
            

        score_text = Chonky_font.render(f"Score: {int(score)}", True, "white")
        screen.blit(score_text, (10, 10))

        combo_text = Chonky_font.render(f"Combo: {combo}", True, "white")
        screen.blit(combo_text, (10, height - 10 - combo_text.get_height()))
            
        clock.tick(fps) 
