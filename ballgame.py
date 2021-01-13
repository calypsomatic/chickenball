#! /usr/bin/python3.7

import pygame
import random

pygame.init()

display_width = 800
display_height = 600
red = pygame.Color(255, 0, 0)
green = pygame.Color(0,255,0)
BLACK = pygame.Color(0,0,0)
white = pygame.Color(255,255,255)
blue = pygame.Color(0,0,255)
PHASE = "AIMING"
BALL_LIMIT = 30
CHICKEN_IMAGE = 'chicksmall.png'
CHICKEN_HP = 50

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Chicken Ball Game")
clock = pygame.time.Clock()


class BounceSprite(pygame.sprite.Sprite):
    def __init__(self, pos, radius):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (radius,radius), radius)
        self.rect = pygame.Rect(*gameDisplay.get_rect().center, 0,0).inflate(radius*2, radius*2)
        self.rect.center = pos
        self.x, self.y = pos
        self.v = [-1,-1]
        self.speed = 3
        self.live = True

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def pos(self):
        return self.rect.centerx, self.rect.centery

    def aim(self, xy):
        x,y = xy
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        norm = (dx**2 + dy**2)**.5
        self.v = [self.speed*dx/norm, self.speed*dy/norm]

    def move(self):
        dx, dy = self.v
        self.x += dx
        self.y += dy        
        self.set_pos(int(self.x), int(self.y))
        if self.y > display_height:
            self.kill()
            self.live = False

    def update(self):
        self.move()

    def reverse_v(self):
        vx, vy = self.v
        self.v = [-vx, -vy] 

    def flee(self, pos):
        self.aim(pos)
        self.reverse_v()

    def reverse_x(self):
        vx, vy = self.v
        self.v = [-vx, vy]

    def reverse_y(self):
        vx, vy = self.v
        self.v = [vx, -vy]

    def bounce(self, target_rect):
        top = target_rect.top
        left = target_rect.left
        right = target_rect.right
        bottom = target_rect.bottom
        if top < self.y < bottom:
            self.reverse_x()
        if left < self.x < right:
            self.reverse_y()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, imagefile, hp):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imagefile)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.v = [0,0]
        self.speed = 5
        self.hp = hp
        self.live = True

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def pos(self):
        return self.rect.centerx, self.rect.centery

    def move(self):
        dx, dy = self.v
        x, y = self.pos()
        if x + dx < 0 or x + dx >= display_width:
            dx = -dx
        if y + dy < 0 or y + dy >= display_height:
            dy = -dy
        self.v = [dx, dy]
        self.set_pos(x + dx, y + dy)


    def aim(self, pos):
        x, y = pos
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        norm = (dx**2 + dy**2)**.5
        self.v = [int(self.speed*dx/norm), int(self.speed*dy/norm)]

        
    def moveToCursor(self):
        self.aim(pygame.mouse.get_pos())        
        self.move()

    def reverse_x(self):
        vx, vy = self.v
        self.v = [-vx, vy]

    def reverse_y(self):
        vx, vy = self.v
        self.v = [vx, -vy]

    def take_hit(self, hit):
        self.hp = self.hp - hit
        if self.hp <= 0:
            self.kill()
            self.live = False



class VerticalWallSprite(pygame.sprite.Sprite):
    def __init__(self, height, pos, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos

class HorizontalWallSprite(pygame.sprite.Sprite):
    def __init__(self, width, pos, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, 5), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos


chicken_pos = (int(display_width * 0.5), int(display_height * 0.5))
dx = -1
dy = -1

chickensprite = Sprite(chicken_pos,CHICKEN_IMAGE, CHICKEN_HP)

crashed = False
buttondown = False

sprite_group = pygame.sprite.Group()

bounce_group = pygame.sprite.Group()

ball_group = pygame.sprite.Group()

target_group = pygame.sprite.Group()

sprite_group.add(chickensprite)
bounce_group.add(chickensprite)
target_group.add(chickensprite)

def shootBall(x, y):
    ball = BounceSprite((display_width//2, display_height), 5)
    ball.aim((x, y))
    bounce_group.add(ball)
    ball_group.add(ball)
    sprite_group.add(ball)

leftwall = VerticalWallSprite(display_height, (0,0))
topwall = HorizontalWallSprite(display_width, (0,0))
rightwall = VerticalWallSprite(display_height, (display_width-5,0))

wall_group = pygame.sprite.Group()
wall_group.add(leftwall)
wall_group.add(topwall)
wall_group.add(rightwall)
pygame.mouse.set_cursor(*pygame.cursors.diamond)
i=0

def drawTrackingLine(from_x):
    mousex, mousey = pygame.mouse.get_pos()
    pygame.draw.line(gameDisplay,BLACK, (from_x, display_height), (mousex, mousey))

while not crashed:
    i += 1
    fire = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            buttondown = True
##            mousex, mousey = pygame.mouse.get_pos()
            
        if event.type == pygame.MOUSEBUTTONUP:
            buttondown = False
            fire = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                chicken_pos = int(100+random.random()*display_width//2), int(100+random.random()*display_height//2)
                chickensprite = Sprite(chicken_pos,CHICKEN_IMAGE, CHICKEN_HP)
                sprite_group.add(chickensprite)
                bounce_group.add(chickensprite)
                target_group.add(chickensprite)


    ballchickencollide = pygame.sprite.groupcollide(target_group, ball_group, False, False)
    for target, balls in ballchickencollide.items():
        for ball in balls:
##            ball.flee(target.pos())
            ball.bounce(target.rect)
            target.take_hit(1)
##    if i % 100 == 0:
##        breakpoint()

    leftwallcollide = pygame.sprite.spritecollide(leftwall, bounce_group, False)
    for sprite in leftwallcollide:
        sprite.reverse_x()
        #breakpoint()
    
    topwallcollide = pygame.sprite.spritecollide(topwall, bounce_group, False)
    for sprite in topwallcollide:
        sprite.reverse_y()
        
    rightwallcollide = pygame.sprite.spritecollide(rightwall, bounce_group, False)
    for sprite in rightwallcollide:
        sprite.reverse_x()
        #breakpoint()
        


    
    sprite_group.update()
    for sprite in sprite_group:
        if not sprite.live:
            del sprite

    gameDisplay.fill(blue)
    if PHASE == 'AIMING' and buttondown:
        drawTrackingLine(display_width//2)
    elif PHASE == 'AIMING' and fire:
        PHASE = 'SHOOTING'
        remainingBalls = BALL_LIMIT
        aim_pos = pygame.mouse.get_pos()
    if PHASE == 'SHOOTING' and remainingBalls > 0:
        if i % 5 == 0:
            shootBall(*aim_pos)
            remainingBalls -= 1
    elif PHASE == 'SHOOTING':
        PHASE = 'AIMING'
        
    bounce_group.draw(gameDisplay)
    wall_group.draw(gameDisplay)
    
    pygame.display.update()
    clock.tick(120)

pygame.quit()
quit()
