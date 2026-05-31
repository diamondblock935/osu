import math
import os
import pygame
import random
import json
from open_lvl import load_level
from level_editor import Beatmap, Level_editor, load_beatmap, save_beatmap

pygame.init()
width, height = 1380, 770
screen = pygame.display.set_mode((width, height))
transparent_surface = pygame.Surface((width, height), pygame.SRCALPHA)
clock = pygame.time.Clock()
smol_font = pygame.font.SysFont('Arial', 20)
medium_font = pygame.font.SysFont('Arial', 32)
Chonky_font = pygame.font.SysFont('Arial', 64)

score = 0
combo = 0
highest_combo = 0 # highest combo achieved in the current level
curent_max_combo = 0 #  highest combo possible at the moment, changes with every hit object, is used to calculate accuracy
curent_max_score = 0 #  highest score possible at the moment, changes with every hit object, is used to calculate accuracy
accuracy = 0 #  % curent max score / score, changes with every hit object
fps = 120
difficulty = 9  #1-10, 10 being the hardest, changes the approach rate
hp_diff = 1 # 1-10, 10 being the hardest, changes how much hp you lose when you miss an object and how much you gain when you hit an object
hp_loss = 1 * hp_diff / fps 
max_hp = 100
hp = max_hp
score_popup_timer = 0
score_popup_pos = (0, 0)
score_add_text = smol_font.render("", True, "white")
status = "menu" # starts in menu
level_start_time = 0 # time when the level starts, used to calculate time elapsed (is set when the level is opened in open_level function)
hp_loss_start = 0 # time when you start losing hp, used to calculate hp loss over time (is set when you miss an object in Circle and slider click functions)
approach_speed = 10 * difficulty / fps
approach_time = 50 / approach_speed 

sliders = []
circles = []
all_objects = []
circle_approach = []
slider_approach = []

running = True



def Main():
    """draws the main menu"""
    global status
    status = "menu"
    screen.fill((0,0,0))
    
    Osu = Chonky_font.render("Osu?", True, (0,106,255))
    
    screen.blit(Osu, (width / 2 - Osu.get_width() // 2, 100))


def text_input_popup(prompt):
    input_text = ""
    popup_active = True

    while popup_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_text
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        # Draw popup
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (40, 40, 40), (50, 150, 540, 180))

        prompt_surf = smol_font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_surf, (60, 160))

        input_surf = smol_font.render(input_text, True, (255, 255, 0))
        screen.blit(input_surf, (60, 200))

        pygame.display.flip()
        clock.tick(30)
def level_editor_menu():
    """draws the level editor menu (here you can select a level to edit or create a new one)"""
    global status
    status = "level_editor_menu"
    screen.fill((0,0,0))
    
    Level_Editor = Chonky_font.render("Level Editor", True, (0,106,255))
    
    screen.blit(Level_Editor, (width / 2 - Level_Editor.get_width() // 2, 100))

    


def open_level_editor(file_path=None):
    """opens the level editor, if file_path is provided, it loads the beatmap from the file"""
    global status
    print(file_path)
    status = "menu"
    screen.fill((0,0,0))
    if file_path:
        level = load_beatmap(file_path)
    else:
        level_name = text_input_popup("Enter level name:")
        if level_name is None or level_name.strip() == "":
            print("Invalid level name.")
            return

        audio_file = text_input_popup("Enter audio file path:")
        if audio_file is None or not audio_file in os.listdir("audio"):
            print("Invalid audio file.")
            return
        level = Beatmap(audio_file, 0)
        file_path = level_name + ".json"
        save_beatmap(level, file_path)
    editor = Level_editor(level, file_path)
    editor.run()

    

def level_select():
    """draws the level select menu (here you can select a level to play)"""
    global status
    status = "level_select"
    screen.fill((0,0,0))
    
    Levels = Chonky_font.render("Select a level", True, (0,106,255))
    
    screen.blit(Levels, (width / 2 - Levels.get_width() // 2, 100))

def load_level_files():
    """loads all level files from the levels folder and returns a list of their paths (used to create buttons in the level select menu and level editor menu)"""
    files = []

    for filename in os.listdir("levels"):
        if filename.endswith(".json"):
            files.append(filename)

    return files

def open_level(file_path):
    """opens the level, loads the level data, creates the hit objects and starts the level song"""
    global status, level_start_time, circles, sliders, all_objects, slider_approach, circle_approach, score, combo, hp, max_hp
    level_data = load_level(file_path)

    audio_path = level_data["audio_file"]
    play_level_song(audio_path)
   
    for i in level_data["objects"]:
        if i["type"] == "circle":
            circles.append(Circle((100, 200, 255, 106), "black", i["pos"], i["time"]))
        elif i["type"] == "slider":
            sliders.append(slider((255, 255, 255, 106), i["pos"], i["end_pos"], i["duration"], i["time"]))

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

def play_level_song(song_path):
    """plays the level song, if the file is not found, it prints a warning and continues without music"""
    if song_path in os.listdir("audio"):
        pygame.mixer.music.load("audio/" + song_path)
        pygame.mixer.music.play()
    else:
        print("WARNING: audio file not found:", song_path)
    

def end_level():
    """resets the level variables"""
    global status, score, combo, highest_combo, curent_max_combo, curent_max_score, circles, sliders, all_objects, slider_approach, circle_approach, hp, max_hp
    score = 0
    combo = 0
    highest_combo = 0
    curent_max_combo = 0
    curent_max_score = 0
    hp = max_hp
    circles.clear()
    sliders.clear()
    all_objects.clear()
    circle_approach.clear()
    slider_approach.clear()

def completed_level(score, highest_combo, accuracy):
    """draws the level end screen with the final score, accuracy and highest combo achieved in the level"""
    completed_text = Chonky_font.render("Level Completed!", True, "green")
    screen.blit(completed_text, (width / 2 - completed_text.get_width() / 2, height / 2 - completed_text.get_height() / 2))
    score_text = medium_font.render(f"Score: {int(score)}", True, "white")
    screen.blit(score_text, (10, 10))
    accuracy_text = medium_font.render(f"{accuracy:.2f}%", True, "white")
    screen.blit(accuracy_text, (10, 15 + score_text.get_height()))
    combo_text = medium_font.render(f"Highest combo: {highest_combo}", True, "white")
    screen.blit(combo_text, (10, height - 10 - combo_text.get_height()))
def failed_level(score, highest_combo, accuracy):
    """draws the level end screen with the final score, accuracy and highest combo achieved in the level"""
    completed_text = Chonky_font.render("Level Failed!", True, "red")
    screen.blit(completed_text, (width / 2 - completed_text.get_width() / 2, height / 2 - completed_text.get_height() / 2))
    score_text = medium_font.render(f"Score: {int(score)}", True, "white")
    screen.blit(score_text, (10, 10))
    accuracy_text = medium_font.render(f"{accuracy:.2f}%", True, "white")
    screen.blit(accuracy_text, (10, 15 + score_text.get_height()))
    combo_text = medium_font.render(f"Highest combo: {highest_combo}", True, "white")
    screen.blit(combo_text, (10, height - 10 - combo_text.get_height()))
def hp_bar():
    """draws the hp bar and handles hp loss over time when you miss an object"""
    global hp, max_hp, hp_loss_start, hp_loss, status, combo

    if combo == 0:
        hp_loss_start = pygame.time.get_ticks()

    if hp_loss_start + 5000 >= pygame.time.get_ticks():
        hp -= hp_loss
    else:
        hp_loss_start = 0

    if hp > max_hp:
        hp = max_hp

    pygame.draw.rect(screen, "red", (width - 210, 10, 200, 30))
    pygame.draw.rect(screen, "green", (width - 210, 10, 200 * (hp / max_hp), 30))
def hp_change(amount):
    """changes your hp when you hit an object"""
    global hp, max_hp
    hp += amount
    hp = max(0, min(hp, max_hp))

def add_score(amount, pos):
    """changes your score when you hit an object, also handles the score popup and hp change when you hit or miss an object"""
    global score, combo, score_popup_timer, score_popup_pos, score_add_text, hp_diff
    

    if type(amount) == int:
        score += amount + amount * combo / 5
        hp_change(amount / (5 * hp_diff))
    if amount == 'x':
        combo = 0
        hp_change(-5 * hp_diff)
        score_add_text = smol_font.render(amount, True, "red")
    if amount == 300:
        score_add_text = smol_font.render(str(amount), True, "cyan")
    elif amount == 100:
        score_add_text = smol_font.render(str(amount), True, "green")
    elif amount == 50:
        score_add_text = smol_font.render(str(amount), True, "yellow")
        
    score_popup_timer = 20
    score_popup_pos = (pos[0] -score_add_text.get_width() // 2, pos[1] - score_add_text.get_height() // 2)
def add_combo():
    """handles combo increase and updates the highest combo achieved in the level"""
    global combo, highest_combo
    combo += 1

    if combo > highest_combo:
        highest_combo = combo
    
    
class menu_button():
    def __init__(self,color, text, pos, size, command):
        self.text = text
        self.pos = pos
        self.size = size
        self.color = color
        self.original_color = self.color
        self.command = command

    def draw(self):
        """draws the button with its text"""
        pygame.draw.rect(screen, self.color, (*self.pos, *self.size))
        button_text = smol_font.render(self.text, True, "black")
        text_rect = button_text.get_rect(center=(self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2))
        screen.blit(button_text, text_rect)

    def handle_event(self, event):
        """handles button clicks, if the button is clicked, it executes its command function (changes based on current status)"""
        global status, running
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if self.pos[0] <= mouse_pos.x <= self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos.y <= self.pos[1] + self.size[1]:
                
                if status == "level_select":
                    self.level_path = load_level_files()[level_select_buttons.index(self)]
                    self.command(self.level_path)
                    
                elif status == "level_editor_menu":
                    if editor_menu_buttons.index(self) == len(load_level_files()):
                        self.command()
                        return
                    self.level_path = load_level_files()[editor_menu_buttons.index(self)]
                    self.command(self.level_path)
                else:
                    self.command()
                    self.color = "grey"
                     
        if event.type == pygame.MOUSEBUTTONUP:
            self.color = self.original_color
           



class Circle():
    global screen, medium_font, smol_font, circle_approach, circles, score, combo, score_popup_timer, score_popup_pos, score_add_text
    def __init__(self, color, text_col, pos, start_time):
        self.finished = False
        self.active = False
        self.clicked = 0
        self.circle_pos = pos[0] + 50, pos[1] + 25
        self.radius = 50
        self.text = ""
        self.color = color
        self.text_col = text_col
        self.start_time = start_time
        self.original_color = self.color

    

    def draw(self):
        """draws the circle, its approach circle and clicks itself when you take too long to click it"""
        pygame.draw.circle(transparent_surface,self.color , self.circle_pos, self.radius)
        pygame.draw.circle(screen, "white", self.circle_pos, 50, 5)

        self.innertext = medium_font.render(self.text, True, self.text_col)
        self.textPos = self.innertext.get_rect(center = self.circle_pos)
        screen.blit(self.innertext, self.textPos)

        if circle_approach[circles.index(self)].radius <= self.radius - 15:
            self.click(None)

        

    def handle_event(self, event):
        """handles clicks on the circle"""
        global mouse_pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                if mouse_pos.distance_to(self.circle_pos) <= self.radius:
                    self.click(event)
                    

    def click(self, event):
        """calculates how accurate your click was and gives you score and hp accordingly"""
        global curent_max_score

        if self.clicked == 0: 
            if circle_approach[circles.index(self)].radius - self.radius >= 32 or circle_approach[circles.index(self)].radius <= self.radius - 10:
                self.score_add = 'x'

            elif circle_approach[circles.index(self)].radius - self.radius <= 7:
                self.score_add = 300
                
            elif circle_approach[circles.index(self)].radius - self.radius <= 21:
                self.score_add = 100
                
            elif circle_approach[circles.index(self)].radius - self.radius <= 32:
                self.score_add = 50

            curent_max_score += 300 + 300 * combo / 5
                
            add_score(self.score_add, self.circle_pos)
            if type(self.score_add) == int:
                add_combo()

            

            

            self.finished = True
            circle_approach[circles.index(self)].finished = True

            

        

        

class Approach_Circle():
    global difficulty, fps, screen, approach_speed
    def __init__(self, color, pos, radius):
        self.finished = False
        self.radius = radius
        self.pos = pos
        self.color = color


    def draw(self):
        """draws itself and shrinks over time, is called in the draw function of hit objects (Circle and slider)"""
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
        self.start_pos = start_pos[0] + 50, start_pos[1] + 25
        self.end_pos = end_pos[0] + 50, end_pos[1] + 25
        self.duration = duration
        self.start_time = start_time + approach_time
        self.progress = 0
        self.slider_ball_pos = self.start_pos
        self.text = ""
        self.text_col = text_col

    def slide(self):
        """moves the slider ball along the slider path"""
        global time_elapsed
        self.progress = (time_elapsed - self.start_time) / self.duration
        self.progress = max(0, min(1, self.progress)) 
        self.slider_ball_pos = pygame.Vector2(self.start_pos).lerp(self.end_pos, self.progress)
        if self.progress >= 1:
            self.click()
            self.finished = True
            slider_approach[sliders.index(self)].finished = True
            
    
    def click(self):
        """calculates how long you held the slider and gives you score and hp accordingly"""
        global curent_max_score, combo
        if self.clicked == 1:
        
            if self.progress >= 0.95:
                self.score_add = 300
                
            elif self. progress >= 0.85:
                self.score_add = 100
            elif self.progress >= 0.7:
                self.score_add = 50
            else:
                self.score_add = 'x'

            curent_max_score += 300 + 300 * combo / 5

            add_score(self.score_add, self.slider_ball_pos)
            if type(self.score_add) == int:
                add_combo()

            

    
            


    def handle_event(self, event):
        """handles clicks on the slider, also handles slider breaks when you release the keys or take too long to click the slider"""
        global mouse_pos, time_elapsed
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_x] or keys[pygame.K_z]) and mouse_pos.distance_to(self.slider_ball_pos) <= 80 and self.progress != 1:
            slider_approach[sliders.index(self)].radius = 0
            pygame.draw.circle(screen, "white", self.slider_ball_pos, 80, 3)
            
        elif time_elapsed > self.start_time + self.duration / 5:
            self.click()
            slider_approach[sliders.index(self)].finished = True
            self.finished = True
            
            
        if event.type == pygame.KEYUP and mouse_pos.distance_to(self.slider_ball_pos) <= 100 and self.clicked == 1:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                self.click()
                slider_approach[sliders.index(self)].finished = True
                self.finished = True
        if event.type == pygame.KEYDOWN and mouse_pos.distance_to(self.slider_ball_pos) <= 100:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                slider_approach[sliders.index(self)].radius = 0
                self.clicked = 1
        

    def draw(self):
        """draws the slider, its approach circle and the slider ball, also handles slider breaks when you take too long to click the slider"""

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
        pygame.draw.circle(transparent_surface, (255, 255, 255, 106), self.start_pos, 50)
        pygame.draw.circle(transparent_surface, (255, 255, 255, 106) , self.end_pos, 50)

        pygame.draw.circle(transparent_surface, (100, 200, 255, 106), self.slider_ball_pos, 47)
        pygame.draw.circle(screen, "white", self.slider_ball_pos, 50, 5)

        if slider_approach[sliders.index(self)].radius > 0 and slider_approach[sliders.index(self)].radius <= 40:
            
            self.click()
            slider_approach[sliders.index(self)].finished = True
            self.finished = True

        self.innertext = medium_font.render(self.text, True, self.text_col)
        self.textPos = self.innertext.get_rect(center = self.slider_ball_pos)
        screen.blit(self.innertext, self.textPos)

# creates the buttons for the main menu, level select menu and level editor menu, the buttons execute different functions based on the current status (main menu, level select menu or level editor menu) when clicked 
menu_buttons = [menu_button("white", "Play", (width / 2 - 100, height / 2), (200, 50), level_select), menu_button("white", "Level Editor", (width / 2 - 100, height / 2 + 75), (200, 50), level_editor_menu)]
level_select_buttons = []

for i in load_level_files():
    level_select_buttons.append(menu_button("white", i.split("\\")[-1].split(".")[0], (width - 320, 0 + load_level_files().index(i) * 90), (300, 80), open_level))

editor_menu_buttons = []

for i in load_level_files():
    editor_menu_buttons.append(menu_button("white", i.split("\\")[-1].split(".")[0], (width - 320, 0 + load_level_files().index(i) * 90), (300, 80), open_level_editor))

editor_menu_buttons.append(menu_button("white", "Create new level", (20, height - 100), (300, 80), open_level_editor))

def run_game():
    global running, width, height, status, mouse_pos, score, combo, highest_combo, accuracy, hp, max_hp, score_popup_timer, score_popup_pos, score_add_text, circles, sliders, all_objects, slider_approach, circle_approach, level_start_time, time_elapsed
    
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
                    if event.key == pygame.K_ESCAPE:
                        status = "menu"

            for button in level_select_buttons:
                button.draw()

            pygame.display.flip()
            screen.fill("black")
        
        if status == "level_editor_menu":
            level_editor_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                    if event.key == pygame.K_ESCAPE:
                        status = "menu"

            for button in editor_menu_buttons:
                button.handle_event(event)
            for button in editor_menu_buttons: 
                button.draw()

            
            pygame.display.flip()
            screen.fill("black")

        if status == "level_completed":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                    if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                        status = "menu"
                        end_level()
            screen.fill("black")
            completed_level(score, highest_combo, accuracy)
            pygame.display.flip()

        if status == "level_failed":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                    if event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                        status = "menu"
                        end_level()
            screen.fill("black")
            failed_level(score, highest_combo, accuracy)
            pygame.display.flip()

        if status == "running":
            time_elapsed = pygame.time.get_ticks() - level_start_time

            sliders = [s for s in sliders if s.finished == False]
            circles = [c for c in circles if c.finished == False]
            slider_approach = [a for a in slider_approach if a.finished == False]
            circle_approach = [a for a in circle_approach if a.finished == False]
            all_objects = [o for o in all_objects if o.finished == False]

            if len(all_objects) > 0:
                all_objects[0].active = True

            if len(all_objects) == 0 and hp > 0:
                status = "level_completed" # placehoder, will be changed to "level complete" in the future
                pygame.mixer.music.stop()
                print("you completed the level")
            elif hp <= 0:
                end_level()
                status = "level_failed"
                pygame.mixer.music.stop()
                print("you failed the level")

            hp_bar()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        running = False
                    if event.key == pygame.K_ESCAPE:
                        status = "menu"
                        pygame.mixer.music.stop()
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

            

            
            
            pygame.display.flip()
            screen.fill("black")
            screen.blit(transparent_surface, (0, 0))
            transparent_surface.fill((0, 0, 0, 0))
            
            for s in slider_approach:
                if sliders[slider_approach.index(s)].start_time - approach_time * 1000 / fps <= time_elapsed:
                    s.draw()
            for c in circle_approach:
                if circles[circle_approach.index(c)].start_time - approach_time * 1000 / fps <= time_elapsed:
                    c.draw()
            for s in sliders:
                if not s.finished and time_elapsed >= s.start_time - approach_time * 1000 / fps:
                    s.draw()
                    s.slide()
            for c in circles:
                if not c.finished and time_elapsed >= c.start_time - approach_time * 1000 / fps:
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


if __name__ == "__main__":
    run_game()
