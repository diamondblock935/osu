import time
import pygame
import random


pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
smol_font = pygame.font.SysFont('Arial', 23)
Chonky_font = pygame.font.SysFont('Arial', 32)

running = True
score = 0
combo = 0
score_popup_timer = 0
score_popup_pos = (0, 0)
score_add_text = None
status = "menu"

def position(radius):
        pos = [random.randint(radius,width - radius) , random.randint(radius, height - radius)]
        return pos


def Main():
    screen.fill((0,0,0))
    
    Osu = Chonky_font.render("Osu", True, (0,106,255))
    play = smol_font.render("Press ENTER to play or press Q to exit", True, (255,255,255))
    
    screen.blit(Osu, (width / 2 - Osu.get_width() // 2, height / 3))
    screen.blit(play, (width / 2 - play.get_width() // 2, height / 2))
    
    pygame.display.flip()
    

class Circle():
    def __init__(self, color, text_col, text, command, pos, radius):
        self.circle_pos = pos
        self.radius = radius
        self.text = text
        self.color = color
        self.text_col = text_col
        self.command = command
        self.original_color = self.color

    

    def draw(self):
        pygame.draw.circle(screen,self.color , self.circle_pos, self.radius)

        self.innertext = Chonky_font.render(self.text, True, self.text_col)
        self.textPos = self.innertext.get_rect(center = self.circle_pos)
        screen.blit(self.innertext, self.textPos)


        
        

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                if pygame.mouse.get_pos()[0] in range(self.circle_pos[0] - self.radius, self.circle_pos[0] + self.radius) and pygame.mouse.get_pos()[1] in range(self.circle_pos[1] - self.radius, self.circle_pos[1] + self.radius):
                    self.command(self, event)
                    self.color = "green"
                    
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_x or event.key == pygame.K_z:
                self.color = self.original_color

    def click(self, event):
        global score, combo, score_popup_timer, score_popup_pos, score_add_text
        
        if approach_circles[circles.index(self)].radius - self.radius >= 32 or approach_circles[circles.index(self)].radius <= self.radius - 10:
            self.score_add = 'x'
            score_add_text = smol_font.render(self.score_add, True, "red")
            combo = 0
        elif approach_circles[circles.index(self)].radius - self.radius <= 7:
            self.score_add = 300
            score_add_text = smol_font.render(str(self.score_add), True, "cyan")

        elif approach_circles[circles.index(self)].radius - self.radius <= 21:
            self.score_add = 100
            score_add_text = smol_font.render(str(self.score_add), True, "green")

        elif approach_circles[circles.index(self)].radius - self.radius <= 32:
            self.score_add = 50
            score_add_text = smol_font.render(str(self.score_add), True, "yellow")

        if type(self.score_add) == int:
            score += self.score_add + self.score_add * combo / 10
            combo += 1
            
        self.text = str(int(self.text) + 1)
        score_popup_timer = 20
        score_popup_pos = (self.circle_pos[0] -score_add_text.get_width() // 2, self.circle_pos[1] - score_add_text.get_height() // 2)

        self.circle_pos = position(self.radius)
        approach_circles[circles.index(self)].pos = self.circle_pos
        approach_circles[circles.index(self)].radius = 100

        

class Approach_Circle():
    def __init__(self, color, pos):
        self.radius = 100
        self.pos = pos
        self.color = color


    def draw(self):
        pygame.draw.circle(screen,self.color , self.pos, self.radius, 3)
        self.radius -= 1.3
        if self.radius <= 40:
            Circle.click(circles[approach_circles.index(self)], None)
            self.radius = 100





circles = [Circle("cyan", "black", "1", Circle.click, position(50), 50)]
approach_circles = []
for i in circles:
    approach_circles.append(Approach_Circle("white", i.circle_pos))

while running:
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
    if status == "running":
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
                i.handle_event(event)

        
        
        pygame.display.flip()
        screen.fill("black")
        for i in approach_circles:
            i.draw()
        for i in circles:
            i.draw()

        if score_popup_timer > 0:
            score_popup_timer -= 1
            screen.blit(score_add_text, score_popup_pos)
            

        score_text = Chonky_font.render(f"Score: {int(score)}", True, "white")
        screen.blit(score_text, (10, 10))

        combo_text = Chonky_font.render(f"Combo: {combo}", True, "white")
        screen.blit(combo_text, (10, height - 10 - combo_text.get_height()))
            
    clock.tick(60) 
