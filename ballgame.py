#! /usr/bin/python3.7

import pygame
import random
import math
import time

pygame.init()

## DEFINE CONSTANTS ##

#COLORS
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0,255,0)
BLACK = pygame.Color(0,0,0)
WHITE = pygame.Color(255,255,255)
BLUE = pygame.Color(0,0,255)
GRAY = pygame.Color(128,128,128)
YELLOW = pygame.Color(255, 255, 0)

#CHICKEN PARAMETERS
CHICKEN_IMAGE = pygame.image.load('chicksmall.png')
CHICKEN_WIDTH = CHICKEN_IMAGE.get_rect().width
CHICKEN_HEIGHT = CHICKEN_IMAGE.get_rect().height
CHICKEN_SPACING = 5
CHICKEN_HP = 1
CHICKEN_NUMBER = 8

# DISPLAY PARAMETERS
VW_WIDTH = 40
HW_HEIGHT = 50
ARENA_WIDTH = CHICKEN_NUMBER*(CHICKEN_WIDTH+CHICKEN_SPACING) + CHICKEN_SPACING
ARENA_HEIGHT = 8*(CHICKEN_HEIGHT+CHICKEN_SPACING)
DISPLAY_WIDTH = ARENA_WIDTH + 2*VW_WIDTH
DISPLAY_HEIGHT = ARENA_HEIGHT + HW_HEIGHT
RIGHT_WALL_EDGE = DISPLAY_WIDTH - VW_WIDTH

#BALL PARAMETERS
BALL_POS = (DISPLAY_WIDTH//2, DISPLAY_HEIGHT)
BALL_LIMIT = 1
BALL_SPEED = 4
BALL_SIZE = 5

#SCORE PARAMETERS
PT_PER_HIT = 10
PT_PER_CHICKEN = 10*PT_PER_HIT
global score
score = 0

WAVE = 1
PHASE = "AIMING"

#INITIALIZE DISPLAY
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
pygame.display.set_caption("Chicken Ball Game")
clock = pygame.time.Clock()

#FONTS
##fonts = pygame.font.get_fonts()
hp_font = pygame.font.SysFont("monospace", 12)
score_font = pygame.font.SysFont("monospace", 25)
display_font = pygame.font.SysFont("monospace", 18)
lose_font = pygame.font.SysFont("monospace", 50)


## DEFINE SPRITES ##
class BallSprite(pygame.sprite.Sprite):
    def __init__(self, pos, radius, color = RED, bonus = False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius,radius), radius)
        self.rect = pygame.Rect(*gameDisplay.get_rect().center, 0,0).inflate(radius*2, radius*2)
        self.rect.center = pos
        self.x, self.y = pos
        self.v = [0,0]
        self.speed = BALL_SPEED
        self.live = True
        self.bonus = bonus

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

    def move(self, dx, dy):
        global BALL_POS
##        dx, dy = self.v
        self.x += dx
        self.y += dy        
        self.set_pos(int(self.x), int(self.y))
        if self.y > DISPLAY_HEIGHT:
            self.kill()
            self.live = False
            if len(ball_group) == 0 and not self.bonus:
                BALL_POS = [self.x, DISPLAY_HEIGHT]
                if BALL_POS[0] < VW_WIDTH + BALL_SIZE:
                    BALL_POS[0] = VW_WIDTH + BALL_SIZE
                if BALL_POS[0] > RIGHT_WALL_EDGE - BALL_SIZE:
                    BALL_POS[0] = RIGHT_WALL_EDGE - BALL_SIZE

    def update(self):
        self.move(*self.v)

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


class ChickenSprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, hp):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface.copy(image)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.v = [0,0]
        self.hp = hp
        self.live = True
        self.display_hp()

    def display_hp(self):
        hp_str = str(self.hp)
        spaces = 3 - len(hp_str)
        self.hp_text = hp_font.render(spaces*' ' + hp_str, True, RED)
        hp_surf = pygame.Surface((self.hp_text.get_rect().width, self.hp_text.get_rect().height), pygame.SRCALPHA)
        hp_surf.fill(WHITE)
        hp_surf.blit(self.hp_text, (0,0))
        self.image.blit(hp_surf, (self.rect.width//2,0))

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def pos(self):
        return self.rect.centerx, self.rect.centery

    def move(self, dx, dy):
        x, y = self.pos()
        self.set_pos(x + dx, y + dy)

##    def aim(self, pos):
##        x, y = pos
##        dx = x - self.rect.centerx
##        dy = y - self.rect.centery
##        norm = (dx**2 + dy**2)**.5
##        self.v = [int(self.speed*dx/norm), int(self.speed*dy/norm)]
##
##        
##    def moveToCursor(self):
##        self.aim(pygame.mouse.get_pos())        
##        self.move()
##
##    def reverse_x(self):
##        vx, vy = self.v
##        self.v = [-vx, vy]
##
##    def reverse_y(self):
##        vx, vy = self.v
##        self.v = [vx, -vy]

    def take_hit(self, hit):
        global score
        score += PT_PER_HIT*hit
        self.hp = self.hp - hit
        self.display_hp()
        if self.hp <= 0:
            score += PT_PER_CHICKEN
            self.kill()
            self.live = False


class VerticalWallSprite(pygame.sprite.Sprite):
    def __init__(self, height, pos, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((VW_WIDTH, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos

class HorizontalWallSprite(pygame.sprite.Sprite):
    def __init__(self, width, pos, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, HW_HEIGHT), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos

    def display_score(self):
        global score
        score_str = str(score)
        zeros = 7 - len(score_str)
        score_text = score_font.render(zeros*'0' + score_str, True, WHITE)
        score_surf = pygame.Surface((score_text.get_rect().width, score_text.get_rect().height), pygame.SRCALPHA)
        score_surf.fill(BLACK)
        score_surf.blit(score_text, (0,0))
        self.image.blit(score_surf, (DISPLAY_WIDTH - score_text.get_rect().width - VW_WIDTH,10))

    def display_wave(self, wave):
        wave_str = 'WAVE: ' + str(wave)
        wave_text = display_font.render(wave_str, True, WHITE)
        wave_surf = pygame.Surface((wave_text.get_rect().width, wave_text.get_rect().height), pygame.SRCALPHA)
        wave_surf.fill(BLACK)
        wave_surf.blit(wave_text, (0,0))
        self.image.blit(wave_surf, (VW_WIDTH,10))

    def display_balls(self, balls):
        ball_str = 'BALLS: ' + str(balls)
        ball_text = display_font.render(ball_str, True, RED)
        ball_surf = pygame.Surface((ball_text.get_rect().width, ball_text.get_rect().height), pygame.SRCALPHA)
        ball_surf.fill(BLACK)
        ball_surf.blit(ball_text, (0,0))
        self.image.blit(ball_surf, (190,10))


##def addRandomChicken():
##    chicken_pos = int(100+random.random()*DISPLAY_WIDTH//2), int(100+random.random()*DISPLAY_HEIGHT//2)
##    addChicken(chicken_pos)


## DEFINE SPRITE GROUPS ##
sprite_group = pygame.sprite.Group()
bounce_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
target_group = pygame.sprite.Group()

## DEFINE FUNCTIONS ##

def spawnBall(location):
    ball = BallSprite(location, BALL_SIZE, YELLOW, True)
    target_group.add(ball)
    sprite_group.add(ball)    
        
def addChicken(pos):
    chickensprite = ChickenSprite(pos,CHICKEN_IMAGE, CHICKEN_HP)
    sprite_group.add(chickensprite)
    bounce_group.add(chickensprite)
    target_group.add(chickensprite)

def spawnChickens():
    num = random.randint(1, CHICKEN_NUMBER//2)
    all_spots = list(range(CHICKEN_NUMBER))
    random.shuffle(all_spots)
    spots = all_spots[:num]
    for i in spots:
        addChicken((VW_WIDTH + CHICKEN_SPACING + i*(CHICKEN_WIDTH + CHICKEN_SPACING),HW_HEIGHT + CHICKEN_SPACING))
    if random.random() < .4:
        spot = all_spots[num]
        location = (VW_WIDTH + CHICKEN_SPACING + spot*(CHICKEN_WIDTH + CHICKEN_SPACING) + 0.5*CHICKEN_WIDTH,HW_HEIGHT + CHICKEN_SPACING + 0.5*CHICKEN_HEIGHT)
        spawnBall(location)

def shootBall(x, y):
    ball = BallSprite(BALL_POS, BALL_SIZE)
    ball.aim((x, y))
    bounce_group.add(ball)
    ball_group.add(ball)
    sprite_group.add(ball)

def drawTrackingLine(from_x):
    mousex, mousey = pygame.mouse.get_pos()
    dx = mousex - from_x
    dy = DISPLAY_HEIGHT - mousey
    angle = math.atan2(dy, dx)
    # prevent flat shooting
    if  0.25 < angle < math.pi - 0.25 and  5 < mousex < DISPLAY_WIDTH -5 and 5 < mousey < DISPLAY_HEIGHT - 5:
        pygame.draw.line(gameDisplay,BLACK, (from_x, DISPLAY_HEIGHT), (mousex, mousey), width=2)
        return True
    else:
        pygame.draw.line(gameDisplay,GRAY, (from_x, DISPLAY_HEIGHT), (mousex, mousey))
        return False

def chickenInside(target_group):
    for chicken in target_group:
        if chicken.rect.bottom >= DISPLAY_HEIGHT:
            return True
    return False

def gameOver():
    youlose = "GAME OVER"
    lose_text = lose_font.render(youlose, True, RED)
    lose_surf = pygame.Surface((lose_text.get_rect().width, lose_text.get_rect().height), pygame.SRCALPHA)
    lose_surf.fill(BLACK)
    lose_surf.blit(lose_text, (0,0))
    gameDisplay.blit(lose_surf, (DISPLAY_WIDTH//2 - lose_text.get_rect().width//2,DISPLAY_HEIGHT//2 - lose_text.get_rect().height))


## INITIALIZE SPRITES ##
leftwall = VerticalWallSprite(DISPLAY_HEIGHT, (0,0))
topwall = HorizontalWallSprite(DISPLAY_WIDTH, (0,0))
rightwall = VerticalWallSprite(DISPLAY_HEIGHT, (DISPLAY_WIDTH-VW_WIDTH,0))
wall_group = pygame.sprite.Group()
wall_group.add(leftwall)
wall_group.add(topwall)
wall_group.add(rightwall)

source_ball = BallSprite((BALL_POS[0], DISPLAY_HEIGHT - 5), BALL_SIZE)
wall_group.add(source_ball)

CHICKEN_HP = WAVE
spawnChickens()

## INITIALIZE VARIABLES ##

pygame.mouse.set_cursor(*pygame.cursors.diamond)
i=0
crashed = False
buttondown = False


## START GAME ##
while not crashed:
    i += 1
    fire = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            buttondown = True
            
        if event.type == pygame.MOUSEBUTTONUP:
            buttondown = False
            fire = True
##        if event.type == pygame.KEYDOWN:
##            if event.key == pygame.K_c:
##                addRandomChicken()

    # DETECT COLLISIONS #
    balltargetcollide = pygame.sprite.groupcollide(target_group, ball_group, False, False)
    for target, balls in balltargetcollide.items():
        if type(target) ==  BallSprite:
            target.kill()
            BALL_LIMIT += 1
        else:
            for ball in balls:
                ball.bounce(target.rect)
                target.take_hit(1)

    leftwallcollide = pygame.sprite.spritecollide(leftwall, bounce_group, False)
    for sprite in leftwallcollide:
        sprite.reverse_x()
    
    topwallcollide = pygame.sprite.spritecollide(topwall, bounce_group, False)
    for sprite in topwallcollide:
        sprite.reverse_y()
        
    rightwallcollide = pygame.sprite.spritecollide(rightwall, bounce_group, False)
    for sprite in rightwallcollide:
        sprite.reverse_x()

    # remove dead sprites
    sprite_group.update()
    for sprite in sprite_group:
        if not sprite.live:
            del sprite

    # background must be drawn before action so tracking line can appear
    gameDisplay.fill(BLUE)

    # determine phase and take appropriate action
    if PHASE == 'AIMING' and buttondown:
        allowShoot = drawTrackingLine(BALL_POS[0])
    elif PHASE == 'AIMING' and fire and allowShoot:
        allowShoot = drawTrackingLine(BALL_POS[0])
        if allowShoot:
            PHASE = 'SHOOTING'
            source_ball.kill()
            remainingBalls = BALL_LIMIT
            aim_pos = pygame.mouse.get_pos()
    if PHASE == 'SHOOTING' and remainingBalls > 0:
        # space out the balls
        if i % 5 == 0:
            shootBall(*aim_pos)
            remainingBalls -= 1
    elif PHASE == 'SHOOTING' and len(ball_group) == 0:
        PHASE = 'ADVANCING'
        source_ball = BallSprite((BALL_POS[0], DISPLAY_HEIGHT - 5), BALL_SIZE)
        wall_group.add(source_ball)
        remainingSteps = CHICKEN_HEIGHT + CHICKEN_SPACING
    elif PHASE == 'ADVANCING' and remainingSteps > 0:
        for sprite in target_group:
            sprite.move(0,2)
        remainingSteps -= 2
    elif PHASE == 'ADVANCING':
        if chickenInside(target_group):
            gameOver()
            break
        WAVE += 1
        CHICKEN_HP = WAVE
        spawnChickens()
        PT_PER_CHICKEN += 5*PT_PER_HIT
##        if random.random() < .35:
##            BALL_LIMIT += 1
        PHASE = 'AIMING'
        
    # draw sprites #
    #bounce_group.draw(gameDisplay)
    #wall_group.draw(gameDisplay)
    sprite_group.draw(gameDisplay)
    wall_group.draw(gameDisplay)
    topwall.display_score()
    topwall.display_wave(WAVE)
    topwall.display_balls(BALL_LIMIT)
    
    pygame.display.update()
    clock.tick(120)

wall_group.draw(gameDisplay)
pygame.display.update()
time.sleep(4)
pygame.quit()
quit()
