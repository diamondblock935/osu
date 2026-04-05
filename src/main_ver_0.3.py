import math
import os
import pygame
import random
import json
from open_lvl import load_level


pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
transparent_surface = pygame.Surface((width, height), pygame.SRCALPHA)
clock = pygame.time.Clock()
smol_font = pygame.font.SysFont('Arial', 20)
medium_font = pygame.font.SysFont('Arial', 32)
Chonky_font = pygame.font.SysFont('Arial', 64)

running = True
score = 0
combo = 0
curent_max_combo = 0 #  highest combo possible at the moment, changes with every hit object, is used to calculate accuracy
curent_max_score = 0 #  highest score possible at the moment, changes with every hit object, is used to calculate accuracy
accuracy = 0 #  % curent max score / score, changes with every hit object
fps = 120
difficulty = 8  #1-10, 10 being the hardest, changes the approach rate
hp_diff = 5 # 1-10, 10 being the hardest, changes how much hp you lose when you miss an object and how much you gain when you hit an object
hp_loss = 2 * hp_diff / fps 
max_hp = 100
hp = max_hp
score_popup_timer = 0 
score_popup_pos = (0, 0)
score_add_text = None # changes when you hit an object (x, 50, 100 or 300 depending on your timing)
status = "menu" # starts in menu
level_start_time = 0 # time when the level starts, used to calculate time elapsed (is set when the level is opened in open_level function)
hp_loss_start = 0 # time when you start losing hp, used to calculate hp loss over time (is set when you miss an object in Circle and slider click functions)
approach_speed = 10 * difficulty / fps

sliders = []
circles = []
all_objects = []
circle_approach = []
slider_approach = []

# def position(radius):
#         pos = [random.randint(radius,width - radius) , random.randint(radius, height - radius)]
#         return pos


def Main():
    global status
    status = "menu"
    screen.fill((0,0,0))
    
    Osu = Chonky_font.render("Osu?", True, (0,106,255))
    play = smol_font.render("Press ENTER to play or press Q to exit", True, (255,255,255))
    
    screen.blit(Osu, (width / 2 - Osu.get_width() // 2, height / 4))
    

def level_select():
    global status
    status = "level_select"
    screen.fill((0,0,0))
    
    Levels = Chonky_font.render("Levels", True, (0,106,255))
    
    screen.blit(Levels, (width / 2 - Levels.get_width() // 2, height / 10))

def load_level_files():
    level_folder = "levels"
    files = []

    for filename in os.listdir(level_folder):
        if filename.endswith(".json"):
            files.append(os.path.join(level_folder, filename))

    return files

def open_level(file_path):
    global status, level_start_time, circles, sliders, all_objects, slider_approach, circle_approach, score, combo, hp, max_hp
    level_data = load_level(file_path)
   
    for i in level_data["objects"]:
        if i["type"] == "circle":
            circles.append(Circle((100, 200, 255, 167), "black", i["pos"], i["radius"], i["start_time"]))
        elif i["type"] == "slider":
            sliders.append(slider((255, 255, 255, 167), i["start_pos"], i["end_pos"], i["duration"], i["start_time"]))

    sliders.sort(key=lambda x: x.start_time, reverse=True)
    circles.sort(key=lambda x: x.start_time, reverse=True)

    for i in sliders:
        slider_approach.append(Approach_Circle("white", i.start_pos, 100))

    for i in circles:
        circle_approach.append(Approach_Circle("white", i.circle_pos, 100))
        
    all_objects.extend(circles)
    all_objects.extend(sliders)
    all_objects.sort(key=lambda x: x.start_time)

    hp = max_hp
    
    for i in all_objects:
        i.text = str(all_objects.index(i) + 1)
    level_start_time = pygame.time.get_ticks()
    status = "running"

def end_level():
    global status, score, combo, curent_max_combo, curent_max_score, circles, sliders, all_objects, slider_approach, circle_approach, hp, max_hp
    score = 0
    combo = 0
    curent_max_combo = 0
    curent_max_score = 0
    hp = max_hp
    circles.clear()
    sliders.clear()
    all_objects.clear()
    circle_approach.clear()
    slider_approach.clear()

def hp_bar():
    global hp, max_hp, hp_loss_start, hp_loss, status, combo

    if combo == 0:
        hp_loss_start = pygame.time.get_ticks()

    if hp_loss_start + 5000 >= pygame.time.get_ticks():
        hp -= hp_loss
    else:
        hp_loss_start = 0

    if hp <= 0:
        end_level()
        status = "level_select" # placehoder, will be changed to "level failed" in the future
    elif hp > max_hp:
        hp = max_hp

    pygame.draw.rect(screen, "red", (width - 210, 10, 200, 30))
    pygame.draw.rect(screen, "green", (width - 210, 10, 200 * (hp / max_hp), 30))
def hp_change(amount):
    global hp, max_hp
    hp += amount
    hp = max(0, min(hp, max_hp))
    
    
    
class menu_button():
    def __init__(self,color, text, pos, size, command):
        self.text = text
        self.pos = pos
        self.size = size
        self.color = color
        self.original_color = self.color
        self.command = command

    def draw(self):
        pygame.draw.rect(screen, self.color, (*self.pos, *self.size))
        button_text = smol_font.render(self.text, True, "black")
        text_rect = button_text.get_rect(center=(self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))
        screen.blit(button_text, text_rect)

    def handle_event(self, event):
        global status, running
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pos[0] <= mouse_pos.x <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos.y <= self.pos[1] + self.size[1]:
                if status == "level_select":
                    self.level_path = load_level_files()[level_select_buttons.index(self)]
                    self.command(self.level_path)
                else:
                    self.command()
                    self.color = "grey"
                
        if event.type == pygame.MOUSEBUTTONUP:
            self.color = self.original_color




class Circle():
    global screen, medium_font, smol_font, circle_approach, circles, score, combo, score_popup_timer, score_popup_pos, score_add_text
    def __init__(self, color, text_col, pos, radius, start_time):
        self.finished = False
        self.active = False
        self.clicked = 0
        self.circle_pos = pos
        self.radius = radius
        self.text = ""
        self.color = color
        self.text_col = text_col
        self.start_time = start_time
        self.original_color = self.color

    

    def draw(self):
        pygame.draw.circle(transparent_surface,self.color , self.circle_pos, self.radius)
        pygame.draw.circle(screen, "white", self.circle_pos, 50, 5)

        self.innertext = medium_font.render(self.text, True, self.text_col)
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
        global score, combo, score_popup_timer, score_popup_pos, score_add_text, curent_max_combo, curent_max_score

        if self.clicked == 0: 
            if circle_approach[circles.index(self)].radius - self.radius >= 32 or circle_approach[circles.index(self)].radius <= self.radius - 10:
                self.score_add = 'x'
                score_add_text = smol_font.render(self.score_add, True, "red")
                combo = 0
                hp_change(-3 * hp_diff)

            elif circle_approach[circles.index(self)].radius - self.radius <= 7:
                self.score_add = 300
                score_add_text = smol_font.render(str(self.score_add), True, "cyan")

            elif circle_approach[circles.index(self)].radius - self.radius <= 21:
                self.score_add = 100
                score_add_text = smol_font.render(str(self.score_add), True, "green")

            elif circle_approach[circles.index(self)].radius - self.radius <= 32:
                self.score_add = 50
                score_add_text = smol_font.render(str(self.score_add), True, "yellow")


            curent_max_score += 300 + 300 * combo / 10
            if type(self.score_add) == int:
                score += self.score_add + self.score_add * combo / 10
                combo += 1
                hp_change(self.score_add / (5 * hp_diff))
            
                
            score_popup_timer = 20
            score_popup_pos = (self.circle_pos[0] -score_add_text.get_width() // 2, self.circle_pos[1] - score_add_text.get_height() // 2)
            self.finished = True
            circle_approach[circles.index(self)].finished = True

            

            self.clicked += 1

            print(curent_max_combo)
        

        

class Approach_Circle():
    global difficulty, fps, screen, approach_speed
    def __init__(self, color, pos, radius):
        self.finished = False
        self.radius = radius
        self.pos = pos
        self.color = color


    def draw(self):
        pygame.draw.circle(screen,self.color , self.pos, self.radius, 3)
        self.radius -= approach_speed
        # if self.radius <= 40:
        #     Circle.click(circles[approach_circles.index(self)], None)
        #     self.radius = 100


class slider():
    global screen, slider_approach, sliders, score, combo, score_popup_timer, score_popup_pos, score_add_text
    def __init__(self, color, start_pos, end_pos, duration, start_time, text_col = "black"):
        self.finished = False
        self.active = False
        self.clicked = 0
        self.color = color
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.start_time = start_time
        self.progress = 0
        self.slider_ball_pos = self.start_pos
        self.text = ""
        self.text_col = text_col

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
        global score, combo, score_popup_timer, score_popup_pos, score_add_text, curent_max_combo, curent_max_score
        if self.clicked == 0:
        
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
                hp_change(-5 * hp_diff)

            curent_max_score += 300 + 300 * combo / 5
            if type(self.score_add) == int:
                score += self.score_add + self.score_add * combo / 5
                combo += 1
                hp_change(self.score_add / (5 * hp_diff))
                
            score_popup_timer = 20
            score_popup_pos = (self.end_pos[0] -score_add_text.get_width() // 2, self.end_pos[1] - score_add_text.get_height() // 2)

            
            self.clicked += 1

            print(curent_max_combo)
        

    def handle_event(self, event):
        global mouse_pos, time_elapsed
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_x] or keys[pygame.K_z]) and mouse_pos.distance_to(self.slider_ball_pos) <= 70 and self.progress != 1:
            slider_approach[sliders.index(self)].radius = 0
            pygame.draw.circle(screen, "white", self.slider_ball_pos, 70, 3)
            
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

        pygame.draw.line(transparent_surface, self.color, self.start_pos, self.end_pos, 100)
        pygame.draw.polygon(transparent_surface, self.color, [p1, p2, p3, p4])
        pygame.draw.circle(transparent_surface, (255, 255, 255, 167), self.start_pos, 50)
        pygame.draw.circle(transparent_surface, (255, 255, 255, 167) , self.end_pos, 50)

        pygame.draw.circle(transparent_surface, (100, 200, 255, 167), self.slider_ball_pos, 47)
        pygame.draw.circle(screen, "white", self.slider_ball_pos, 50, 5)

        if slider_approach[sliders.index(self)].radius > 0 and slider_approach[sliders.index(self)].radius <= 40:
            
            self.click(event)
            slider_approach[sliders.index(self)].finished = True
            self.finished = True

        self.innertext = medium_font.render(self.text, True, self.text_col)
        self.textPos = self.innertext.get_rect(center = self.slider_ball_pos)
        screen.blit(self.innertext, self.textPos)

    
menu_buttons = [menu_button("white", "Play", (width / 2 - 100, height / 2), (200, 50), level_select)]
level_select_buttons = []

for i in load_level_files():
    level_select_buttons.append(menu_button("white", i.split("\\")[-1].split(".")[0], (width / 2 - 100, height / 2 + 100 + load_level_files().index(i) * 75), (200, 50), open_level))



while running:
    

    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    if status == "menu":
        Main()
        
        for event in pygame.event.get():
            for button in menu_buttons:
                button.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
            
        for button in menu_buttons:
            button.draw()

        pygame.display.flip()
        screen.fill("black")

    if status == "level_select":
        level_select()
        
        for event in pygame.event.get():
            for button in level_select_buttons:
                button.handle_event(event)

            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()

        for button in level_select_buttons:
            button.draw()

        pygame.display.flip()
        screen.fill("black")

        
    if status == "running":
        time_elapsed = pygame.time.get_ticks() - level_start_time

        sliders = [s for s in sliders if s.finished == False]
        circles = [c for c in circles if c.finished == False]
        slider_approach = [a for a in slider_approach if a.finished == False]
        circle_approach = [a for a in circle_approach if a.finished == False]
        all_objects = [o for o in all_objects if o.finished == False]

        hp_bar()

        

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    running = False
                if event.key == pygame.K_m:
                    status = "menu"
                    end_level()
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
        screen.blit(transparent_surface, (0, 0))
        transparent_surface.fill((0, 0, 0, 0))
        
        for s in slider_approach:
            if sliders[slider_approach.index(s)].start_time - (50 / approach_speed) * 1000/ fps <= time_elapsed:
                s.draw()
        for c in circle_approach:
            if circles[circle_approach.index(c)].start_time - (50 / approach_speed) * 1000/ fps <= time_elapsed:
                c.draw()
        for s in sliders:
            if not s.finished and time_elapsed >= s.start_time - (50 / approach_speed) * 1000/ fps:
                s.draw()
                s.slide(event)
        for c in circles:
            if not c.finished and time_elapsed >= c.start_time - (50 / approach_speed) * 1000/ fps:
                c.draw()

        
        if score_popup_timer > 0:
            score_popup_timer -= 60 / fps
            screen.blit(score_add_text, score_popup_pos)
            
        
        score_text = medium_font.render(f"Score: {int(score)}", True, "white")
        screen.blit(score_text, (10, 10))
        accuracy = score / curent_max_score * 100 if curent_max_score > 0 else 100
        accuracy_text = medium_font.render(f"{accuracy:.2f}%", True, "white")
        screen.blit(accuracy_text, (10, 15 + score_text.get_height()))

        

        combo_text = medium_font.render(f"Combo: {combo}", True, "white")
        screen.blit(combo_text, (10, height - 10 - combo_text.get_height()))
            
        clock.tick(fps) 
