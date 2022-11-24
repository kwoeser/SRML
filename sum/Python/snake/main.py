import pygame
import math
import random
import tkinter as tk
from tkinter import messagebox

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0,0 )
pygame.init()
class Cube(object):
    rows = 20
    w = 500
    def __init__(self, pos, dirnx = 1, dirny = 0, color = RED):
        self.pos = pos
        self.dirnx = 1
        self.dirny = 0
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)
        
    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        # i stands for row
        i = self.pos[0]
        # j stands for column
        j = self.pos[1]

        pygame.draw.rect(surface, (RED), (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius, j*dis+ 8)
            circleMiddle2 = (i*dis + dis - radius*2, j*dis+8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)



class Snake(object):
    body = []
    turns = {}
    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #pygame.QUIT()
                pygame.quit()

            keys = pygame.key.get_pressed()

            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    # TURNS SELF.TURNS INTO A DICT
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    # TURNS SELF.TURNS INTO A DICT
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_UP]:
                    self.dirnx = 0
                    self.dirny = -1
                    # TURNS SELF.TURNS INTO A DICT
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_DOWN]:
                    self.dirnx = 0
                    self.dirny = 1
                    # TURNS SELF.TURNS INTO A DICT
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            
            """if event.type == pygame.K_LEFT:
                self.dirnx = -1
                self.dirny = 0
                # TURNS SELF.TURNS INTO A DICT
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

            elif event.type == pygame.K_RIGHT:
                self.dirnx = 1
                self.dirny = 0
                # TURNS SELF.TURNS INTO A DICT
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

            elif event.type == pygame.K_UP:
                self.dirnx = 0
                self.dirny = -1 
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            
            elif event.type == pygame.K_DOWN:
                self.dirnx = 0
                self.dirny = 1
                # TURNS SELF.TURNS INTO A DICT
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]"""

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
                
            else:
                if c.dirnx == -1 and c.pos[0] <= 0:
                    c.pos = (c.rows-1, c.pos[1])

                elif c.dirnx == 1 and c.pos[0] >= c.rows-1:
                    c.pos = (0, c.pos[1])

                elif c.dirny == 1 and c.pos[1] >= c.rows-1:
                    c.pos = (c.pos[0], 0)

                elif c.dirny == -1 and c.pos[1] <= 0: 
                    c.pos = (c.pos[0], c.rows-1)

                else:
                    c.move(c.dirnx, c.dirny)



    def reset(self, pos):
        self.head = Cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1


    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)


def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0

    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, WHITE, (x, 0), (x, w))
        pygame.draw.line(surface, WHITE, (0, y), (w, y))

def redrawWindow(surface):
    global rows, width, s, snack
    surface.fill(BLACK)
    s.draw(surface)
    snack.draw(surface)
    drawGrid(width, rows, surface)
    pygame.display.update()


def randomSnack(rows, item: Snake):
    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)

        if len(list(filter(lambda z:z.pos == (x,y), positions))) > 0:
            continue
        else:
            break
    
    return (x,y)


# HOW TO CREATE MESSAGE BOX ON TOP OF SCREEN
def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()

    except:
        pass

def main():
    global rows, width, s, snack
    width = 500
    #height = 500
    # MAKE SURE THE ROW NUMBER IS DIVISIBLE BY WIDTH AND HEIGHT
    rows = 20
    win = pygame.display.set_mode((width, width))
    s = Snake(RED, (10, 10))
    snack = Cube(randomSnack(rows, s), color = GREEN)
    flag = True

    clock = pygame.time.Clock()

    while flag:
        pygame.time.delay(50)
        # CLOCK MAKES IT SO THE GAME DOESN'T GO OVER 10 FPS)
        clock.tick(10)
        s.move()
        if s.body[0].pos == snack.pos:
            s.addCube()
            snack = Cube(randomSnack(rows, s), color = GREEN)   
        
        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z:z.pos, s.body[x+1 :])):
                #print(f"Score: {len(s.body) - 1}")
                print(f"Score: {len(s.body)}")
                message_box("You Lost!", "Play Again")
                s.reset((10,10))
                break

        redrawWindow(win)


        # CREATE BORDERS LATER
    pass
main()
