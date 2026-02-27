import pygame
import random


pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Consolas', 30)


running = True
score = 0
combo = 0

def position(radius):
        pos = [random.randint(radius,width - radius) , random.randint(radius, height - radius)]
        return pos

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

        self.innertext = my_font.render(self.text, True, self.text_col)
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
        global score, combo
        if approach_circles[circles.index(self)].radius - self.radius >= 30 or approach_circles[circles.index(self)].radius <= self.radius - 10:
            combo = 0
        elif approach_circles[circles.index(self)].radius - self.radius <= 10:
            score += 300 + 300 * combo / 10
            combo += 1
        elif approach_circles[circles.index(self)].radius - self.radius <= 20:
            score += 100 + 100 * combo / 10
            combo += 1
        elif approach_circles[circles.index(self)].radius - self.radius <= 30:
            score += 50 + 50 * combo / 10
            combo += 1
        self.text = str(int(self.text) + 1)
        self.circle_pos = position(self.radius)
        approach_circles[circles.index(self)].pos = self.circle_pos
        approach_circles[circles.index(self)].radius = 100

class Approach_Circle():
    def __init__(self, color, pos):
        self.radius = 100
        self.pos = pos
        self.color = color
        self.original_color = self.color


    def draw(self):
        pygame.draw.circle(screen,self.color , self.pos, self.radius, 3)
        self.radius -= 1
        if self.radius <= 40:
            Circle.click(circles[approach_circles.index(self)], None)
            self.radius = 100





circles = [Circle("cyan", "black", "1", Circle.click, position(50), 50)]
approach_circles = []
for i in circles:
    approach_circles.append(Approach_Circle("white", i.circle_pos))

while running:
    

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
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

    score_text = my_font.render(f"Score: {int(score)}", True, "white")
    screen.blit(score_text, (10, 10))

    combo_text = my_font.render(f"Combo: {combo}", True, "white")
    screen.blit(combo_text, (10, height - 10 - combo_text.get_height()))
        
    clock.tick(60) 
