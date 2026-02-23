import pygame
import random


pygame.init()
width, height = 1280, 720
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Consolas', 30)


running = True


class Circle():
    def __init__(self, color, text_col, text, command):
        self.radius = 50
        self.circle_pos = self.position(self.radius)
        self.text = text
        self.color = color
        self.text_col = text_col
        self.command = command
        self.original_color = self.color

    def position(self, radius):
        self.circle_pos = [random.randint(radius,width - radius) , random.randint(radius, height - radius)]
        return self.circle_pos

    def draw(self):
        pygame.draw.circle(screen,self.color , self.circle_pos, self.radius)

        self.innertext = my_font.render(self.text, True, self.text_col)
        self.textPos = self.innertext.get_rect(center = self.circle_pos)
        screen.blit(self.innertext, self.textPos)
        

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and pygame.mouse.get_pos()[0] in range(self.circle_pos[0] - self.radius, self.circle_pos[0] + self.radius) and pygame.mouse.get_pos()[1] in range(self.circle_pos[1] - self.radius, self.circle_pos[1] + self.radius):
                self.command(event)
                self.color = "green"
                self.position(self.radius)
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_c:
                self.color = self.original_color


    
def click(event):

    print("uwu")
    circle.text = str(int(circle.text) + 1)


circle = Circle("cyan", "black", "1", click)

while running:
    

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                running = False
        circle.handle_event(event)

    
    pygame.display.flip()
    screen.fill("blue")
    circle.draw()
    clock.tick(10) 
