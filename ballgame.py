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
ORANGE = pygame.Color(255, 128, 0)
PURPLE = pygame.Color(153, 51, 255)

#CHICKEN PARAMETERS
CHICKEN_IMAGE = pygame.image.load('chicksmall.png')
GREEN_CHICKEN_IMAGE = pygame.image.load('chicksmallgreen.png')
ORANGE_CHICKEN_IMAGE = pygame.image.load('chicksmallorange.png')
PURPLE_CHICKEN_IMAGE = pygame.image.load('chicksmallpurple.png')
BONUS_CHICKENS = {None: CHICKEN_IMAGE, 'SLIME': GREEN_CHICKEN_IMAGE, 'FIRE': ORANGE_CHICKEN_IMAGE, 'DOUBLE' : PURPLE_CHICKEN_IMAGE}
CHICKEN_WIDTH = CHICKEN_IMAGE.get_rect().width
CHICKEN_HEIGHT = CHICKEN_IMAGE.get_rect().height
HZ_CHICKEN_SPACING = 5
VT_CHICKEN_SPACING = 3
CHICKEN_HP = 2
CHICKEN_NUMBER = 8

# DISPLAY PARAMETERS
VW_WIDTH = 100
HW_HEIGHT = 50
ARENA_WIDTH = CHICKEN_NUMBER*(CHICKEN_WIDTH+HZ_CHICKEN_SPACING) + HZ_CHICKEN_SPACING
ARENA_HEIGHT = 8*(CHICKEN_HEIGHT+VT_CHICKEN_SPACING) + CHICKEN_HEIGHT//2
DISPLAY_WIDTH = ARENA_WIDTH + 2*VW_WIDTH
DISPLAY_HEIGHT = ARENA_HEIGHT + HW_HEIGHT
RIGHT_WALL_EDGE = DISPLAY_WIDTH - VW_WIDTH

#BALL PARAMETERS
BALL_POS = (DISPLAY_WIDTH//2, DISPLAY_HEIGHT)
BALL_LIMIT = 5
BALL_SPEED = 4 #Should always be less than BALL_SIZE
BALL_SIZE = 5
BALL_COLORS = {None: RED, 'SLIME': GREEN, 'FIRE': ORANGE, 'DOUBLE': PURPLE}

#Bonus Parameters
BONUS_BALL_CHANCE = .4
POWERUP_CHANCE = .8
BONUS_IN_EFFECT = None
BONUS_DROPPED = None
POWERUPS = ['SLIME', 'FIRE', 'DOUBLE']
DISPLAY_BONUS_FRAMES = 0
BONUS_TO_DISPLAY = None

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
hp_font = pygame.font.SysFont("monospace", 12, bold=True)
score_font = pygame.font.SysFont("monospace", 25, bold=True)
display_font = pygame.font.SysFont("monospace", 18,bold=True)
lose_font = pygame.font.SysFont("monospace", 50,bold=True)
powerup_font = pygame.font.SysFont("monospace", 25,bold=True)


class GameState():
    def __init__(self):
        self.powerup_state = {'SLIME': {'available': False, 'selected':False},
                              'FIRE': {'available': False, 'selected':False},
                              'DOUBLE': {'available': False, 'selected':False}}

    def set_powerup(self, powerup, key, value):
        #TODO: Cannot have more than one selected at a time -
        # enforce
        self.powerup_state[powerup][key] = value

    def get_selected(self):
        for pu, state in self.powerup_state.items():
            if state['selected']:
                return pu
        return None
    
## DEFINE SPRITES ##
class MobileSprite(pygame.sprite.Sprite):

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
        x, y = self.pos()
        x += dx
        y += dy
        self.set_pos(x, y)
        if y > DISPLAY_HEIGHT:
            self.destroy()

    def destroy(self):
        self.kill()
        self.live = False

    def update(self):
        self.move(*self.v)

    def reverse_x(self):
        vx, vy = self.v
        self.v = [-vx, vy]

    def reverse_y(self):
        vx, vy = self.v
        self.v = [vx, -vy]



class BouncySprite(MobileSprite):
    def __init__(self, pos, radius, color = RED):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius,radius), radius)
        self.rect = pygame.Rect(*gameDisplay.get_rect().center, 0,0).inflate(radius*2, radius*2)
        self.rect.center = pos
        self.x, self.y = pos
        self.v = [0,0]
        self.speed = BALL_SPEED
        self.damage = 1
        self.live = True

    def set_pos(self, x, y):
        self.x, self.y = x, y
        self.rect.centerx = x
        self.rect.centery = y

    def pos(self):
        return self.x, self.y

    def destroy(self):
        self.kill()
        self.live = False
        global BALL_POS
        if len(ball_group) == 0:
            BALL_POS = [self.x, DISPLAY_HEIGHT]
            # avoid getting stuck in corner
            if BALL_POS[0] < VW_WIDTH + BALL_SIZE:
                BALL_POS[0] = VW_WIDTH + BALL_SIZE
            if BALL_POS[0] > RIGHT_WALL_EDGE - BALL_SIZE:
                BALL_POS[0] = RIGHT_WALL_EDGE - BALL_SIZE        

    def bounce(self, target_rect):
        top = target_rect.top
        left = target_rect.left
        right = target_rect.right
        bottom = target_rect.bottom
        vx, vy = self.v
        if top < self.y < bottom:
            self.reverse_x()
        elif left < self.x < right:
            self.reverse_y()
        elif self.x < left and self.y < top:
            #top left
            if vy > 0:
                self.reverse_y()
            else:
                self.reverse_x()
        elif self.x > right and self.y < top:
            #top right
            if vy > 0:
                self.reverse_y()
            else:
                self.reverse_x()
        elif self.x < left and self.y > bottom:
            #bottom left
            if vy < 0:
                self.reverse_y()
            else:
                self.reverse_x()
        else:
            #bottom right
            if vy < 0:
                self.reverse_y()
            else:
                self.reverse_x()
##
##    def bounce(self, target_rect):
##        top = target_rect.top
##        left = target_rect.left
##        right = target_rect.right
##        bottom = target_rect.bottom
##        if top < self.y < bottom:
##            self.reverse_x()
##        elif left < self.x < right:
##            self.reverse_y()
##        elif self.x < left and self.y < top:
##            #top left
##            dy = top - self.y
##            dx = left - self.x
##            print("topleft")
##            if dy > dx:
##                self.reverse_y()
##            else:
##                self.reverse_x()
##        elif self.x > right and self.y < top:
##            #top right
##            dy = top - self.y
##            dx = self.x - right
##            print("topright")
##            if dy > dx:
##                self.reverse_y()
##            else:
##                self.reverse_x()
##        elif self.x < left and self.y > bottom:
##            #bottom left
##            vx, vy = self.v
##            if vy < 0:
##                self.reverse_y()
##                return
##            dy = self.y - bottom
##            dx = left - self.x
##            print("bottomleft")
##            if dy > dx:
##                self.reverse_y()
##            else:
##                self.reverse_x()
####        elif self.x > right and self.y > bottom:
##        else:
##            #bottom right
##            vx, vy = self.v
##            if vy < 0:
##                self.reverse_y()
##                return
##            dy = self.y - bottom
##            dx = self.x - right
##            print("bottomright")
##            if dy > dx:
##                self.reverse_y()
##            else:
##                self.reverse_x()
            
##            tcx,tcy = target_rect.center
##            vx, vy = self.v
##            cvx, cvy = tcx - self.x, tcy - self.y
##            dotp = cvx*vx + cvy*vy
##            scale = dotp/(cvx**2 + cvy**2)
##            compx, compy = cvx*scale, cvy*scale
##            self.v = [vx - 2*compx, vy - 2*compy]


class SlimeBallSprite(BouncySprite):
    def __init__(self, pos, radius, color = GREEN):
        super().__init__(pos, radius, color = GREEN)

    def destroy(self):
        self.kill()
        self.live = False
        ball = BouncySprite(self.pos(), BALL_SIZE)
        ball.v = self.v
        ball.reverse_y()
        bounce_group.add(ball)
        ball_group.add(ball)
        sprite_group.add(ball)

class DoubleBallSprite(BouncySprite):
    def __init__(self, pos, radius, color = PURPLE):
        super().__init__(pos, radius, color = PURPLE)
        self.damage = 2

class FireBallSprite(BouncySprite):
     def __init__(self, pos, radius=BALL_SIZE*2, color = ORANGE):
        super().__init__(pos, radius=BALL_SIZE*2, color = ORANGE)

     def destroy(self):
        self.kill()
        self.live = False
        ball = BouncySprite(self.pos(), BALL_SIZE)
        ball.v = self.v
        bounce_group.add(ball)
        ball_group.add(ball)
        sprite_group.add(ball)

class TargetSprite(MobileSprite):
    def __init__(self, pos, hp = 0, image = None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface.copy(image)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
##        self.x, self.y = pos
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
        

    def take_hit(self, hit, gamestate):
        global score
        score += PT_PER_HIT*hit
        self.hp = self.hp - hit
        self.display_hp()
        if self.hp <= 0:
            score += PT_PER_CHICKEN
            self.kill()
            self.live = False

class EnemySprite(TargetSprite):

    def move(self, dx, dy):
        global chickenInside
        x, y = self.pos()
        x += dx
        y += dy
        self.set_pos(x, y)
        if self.rect.bottom >= DISPLAY_HEIGHT:
            chickenInside = True

class BonusChickenSprite(EnemySprite):
    def __init__(self, pos, hp = 0, image = None, bonus = 'SLIME'):
        super().__init__(pos, hp, image)
        self.bonus = bonus

    def take_hit(self, hit, gamestate):
        super().take_hit(hit, gamestate)
        #breakpoint()
        if not self.live:
            global DISPLAY_BONUS_FRAMES, BONUS_TO_DISPLAY
            gamestate.set_powerup(self.bonus, 'available', True)
            DISPLAY_BONUS_FRAMES = 150
            BONUS_TO_DISPLAY = self.bonus



class BonusBallSprite(TargetSprite):
    def __init__(self, pos):
        radius = BALL_SIZE
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (radius,radius), radius)
        self.rect = pygame.Rect(*gameDisplay.get_rect().center, 0,0).inflate(radius*2, radius*2)
        self.rect.center = pos
        self.x, self.y = pos
        self.v = [0,0]
        self.live = True
    

class VerticalWallSprite(pygame.sprite.Sprite):
    def __init__(self, height, pos, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((VW_WIDTH, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos

    def display_power_balls(self, gamestate):
##    def display_power_balls(self, color):
        radius = BALL_SIZE*3
        box_height = radius*13
        box_width = radius*4
        bonus_info_image = pygame.Surface((radius*4, box_height), pygame.SRCALPHA)
        offset = 1
        for pu in POWERUPS:
            if gamestate.powerup_state[pu]['available']:
                self.display_powerball_full(bonus_info_image, BALL_COLORS[pu], radius, offset)
            else:
                self.display_powerball_empty(bonus_info_image, radius, offset)
            if gamestate.powerup_state[pu]['selected']:
                self.display_powerball_selected(bonus_info_image, radius, offset)
            offset += 2        
        
        self.image.blit(bonus_info_image, (VW_WIDTH//2 - box_width//2, DISPLAY_HEIGHT - box_height))

    def erase(self):
        self.image.fill(BLACK)

    def display_powerball_empty(self, image, radius, offset):
        pygame.draw.circle(image, WHITE, (radius*2,radius*2*offset), radius, radius//4)

    def display_powerball_full(self, image, color, radius, offset):
        pygame.draw.circle(image, color, (radius*2,radius*2*offset), radius)

    def display_powerball_selected(self, image, radius, offset):
        pygame.draw.circle(image, RED, (radius*2,radius*2*offset), 6*radius//4, radius//4)
##        pygame.draw.circle(image, color, (radius*2,radius*2*offset), radius)


class HorizontalWallSprite(pygame.sprite.Sprite):
    def __init__(self, width, pos, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, HW_HEIGHT), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_bounding_rect()
        self.rect.topleft = pos

    def display_score(self):
        self.image.fill(BLACK)
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
        self.ball_surf = pygame.Surface((ball_text.get_rect().width, ball_text.get_rect().height), pygame.SRCALPHA)
        self.ball_surf.fill(BLACK)
        self.ball_surf.blit(ball_text, (0,0))
        self.image.blit(self.ball_surf, (230,10))

    def display_powerup(self, powerup):
        ball_text = powerup_font.render(powerup + "BALL!!", True, BALL_COLORS[powerup])
        self.ball_surf = pygame.Surface((ball_text.get_rect().width, ball_text.get_rect().height), pygame.SRCALPHA)
        self.ball_surf.fill(BLACK)
        self.ball_surf.blit(ball_text, (0,0))
        self.image.blit(self.ball_surf, (170,10))


## DEFINE SPRITE GROUPS ##
sprite_group = pygame.sprite.Group()
bounce_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
target_group = pygame.sprite.Group()

## DEFINE FUNCTIONS ##

def spawnBonusBall(location):
    ball = BonusBallSprite(location)
    target_group.add(ball)
    sprite_group.add(ball)    
        
def addChicken(pos, bonus = None):
    if bonus is None:
        chickensprite = EnemySprite(pos,CHICKEN_HP, CHICKEN_IMAGE)
    else:
        chickensprite = BonusChickenSprite(pos,2*CHICKEN_HP, BONUS_CHICKENS[bonus], bonus = bonus)
    sprite_group.add(chickensprite)
    target_group.add(chickensprite)

def spawnChickens():
    num = random.randint(1, CHICKEN_NUMBER//2 - 1)
    all_spots = list(range(CHICKEN_NUMBER))
    random.shuffle(all_spots)
    spots = all_spots[:num]
##    spots = [0]
    for i in spots:
        if random.random() < POWERUP_CHANCE:
            bonus = random.choice(POWERUPS)
        else:
            bonus = None
        addChicken((VW_WIDTH + HZ_CHICKEN_SPACING + i*(CHICKEN_WIDTH + HZ_CHICKEN_SPACING),HW_HEIGHT + VT_CHICKEN_SPACING), bonus = bonus)
    if random.random() < BONUS_BALL_CHANCE:
        spot = all_spots[num]
        location = (VW_WIDTH + HZ_CHICKEN_SPACING + spot*(CHICKEN_WIDTH + HZ_CHICKEN_SPACING) + 0.5*CHICKEN_WIDTH,HW_HEIGHT + VT_CHICKEN_SPACING + 0.5*CHICKEN_HEIGHT)
        spawnBonusBall(location)


def shootBall(x, y, gamestate):
    BONUS_IN_EFFECT = gamestate.get_selected()
    if BONUS_IN_EFFECT == 'SLIME':
        ball = SlimeBallSprite(BALL_POS, BALL_SIZE)
    elif BONUS_IN_EFFECT == 'FIRE':
        ball = FireBallSprite(BALL_POS, BALL_SIZE)
        BONUS_IN_EFFECT = None
    elif BONUS_IN_EFFECT == 'DOUBLE':
        ball = DoubleBallSprite(BALL_POS, BALL_SIZE)
    else:    
        ball = BouncySprite(BALL_POS, BALL_SIZE)
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

##def chickenInside(target_group):
##    for chicken in target_group:
##        if chicken.rect.bottom >= DISPLAY_HEIGHT:
##            return True
##    return False

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

source_ball = BouncySprite((BALL_POS[0], DISPLAY_HEIGHT - 5), BALL_SIZE)
wall_group.add(source_ball)

CHICKEN_HP = WAVE
spawnChickens()

## INITIALIZE VARIABLES ##

pygame.mouse.set_cursor(*pygame.cursors.diamond)
i=0
crashed = False
buttondown = False
chickenInside = False

game_state = GameState()

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

    # DETECT COLLISIONS #
    balltargetcollide = pygame.sprite.groupcollide(target_group, ball_group, False, False)
    for target, balls in balltargetcollide.items():
        if type(target) == BonusBallSprite:
            target.kill()
            BALL_LIMIT += 1
        else:
            for ball in balls:
                ball.bounce(target.rect)
                if type(ball) == FireBallSprite:
                    ball.destroy()
                    target.take_hit(target.hp, game_state)
                else:
                    target.take_hit(ball.damage, game_state)

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
            rightwall.erase()
            remainingBalls = BALL_LIMIT
            aim_pos = pygame.mouse.get_pos()
    if PHASE == 'SHOOTING' and remainingBalls > 0:
        # space out the balls
        if i % 5 == 0:
            shootBall(*aim_pos)
            remainingBalls -= 1
    elif PHASE == 'SHOOTING' and len(ball_group) == 0:
        PHASE = 'ADVANCING'
        if BONUS_DROPPED:
            BONUS_IN_EFFECT = BONUS_DROPPED
            BONUS_DROPPED = None
        else:
            BONUS_IN_EFFECT = None
        
        source_ball = BouncySprite((BALL_POS[0], DISPLAY_HEIGHT - 5), BALL_SIZE, BALL_COLORS[BONUS_IN_EFFECT])
        wall_group.add(source_ball)
        remainingSteps = CHICKEN_HEIGHT + VT_CHICKEN_SPACING
    elif PHASE == 'ADVANCING' and remainingSteps > 0:
        for sprite in target_group:
            sprite.move(0,2)
        remainingSteps -= 2
    elif PHASE == 'ADVANCING':
        if chickenInside:
            gameOver()
            break
        WAVE += 1
        CHICKEN_HP = WAVE
        spawnChickens()
        PT_PER_CHICKEN += 5*PT_PER_HIT
        PHASE = 'AIMING'

    # draw sprites #
    sprite_group.draw(gameDisplay)
    wall_group.draw(gameDisplay)
    topwall.display_score()
    topwall.display_wave(WAVE)
    if DISPLAY_BONUS_FRAMES > 0:
        topwall.display_powerup(BONUS_TO_DISPLAY)
        DISPLAY_BONUS_FRAMES -= 1
    else:
        BONUS_TO_DISPLAY = None
        topwall.display_balls(BALL_LIMIT)

##    if BONUS_TO_DISPLAY:
##        rightwall.display_power_balls(BALL_COLORS[BONUS_TO_DISPLAY])
    rightwall.display_power_balls(game_state)
    pygame.display.update()
    clock.tick(120)

wall_group.draw(gameDisplay)
pygame.display.update()
time.sleep(4)
pygame.quit()
quit()
