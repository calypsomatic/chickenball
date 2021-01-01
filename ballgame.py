import pygame

pygame.init()

display_width = 800
display_height = 600
red = pygame.Color(255, 0, 0)
green = pygame.Color(0,255,0)
BLACK = pygame.Color(0,0,0)
white = pygame.Color(255,255,255)
blue = pygame.Color(0,0,255)

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption("Chicken Ball Game")
clock = pygame.time.Clock()


class BounceSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (size,size), size)
        self.rect = pygame.Rect(*gameDisplay.get_rect().center, 0,0).inflate(size, size)
        self.rect.center = pos
        self.v = [-1,-1]

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def pos(self):
        return self.rect.centerx, self.rect.centery

    def aim(self, pos):
        x, y = pos
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        norm = (dx**2 + dy**2)**.5
        self.v = [int(10*dx/norm), int(10*dy/norm)]

    def move(self):
        dx, dy = self.v
        x, y = self.pos()
        if x + dx < 0 or x + dx >= display_width:
            dx = -dx
        if y + dy < 0:
            dy = -dy
        self.v = [dx, dy]
        self.set_pos(x + dx, y + dy)
        if y > display_height:
            self.kill()

    def update(self):
        self.move()

    def reverse_v(self):
        vx, vy = self.v
        self.v = [-vx, -vy]

    def flee(self, pos):
        x,y = pos
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        norm = (dx**2 + dy**2)**.5
        self.v = [-int(10*dx/norm), -int(10*dy/norm)]

    def reverse_x(self):
        vx, vy = self.v
        self.v = [-vx, vy]

    def reverse_y(self):
        vx, vy = self.v
        self.v = [vx, -vy]

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, imagefile):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imagefile)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.v = [0,0]

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

    def moveToCursor(self):
        mousex, mousey = pygame.mouse.get_pos()
        x,y = self.pos()
        if x < mousex:
            dx = 1
        else:
            dx = -1
        if y < mousey:
            dy = 1
        else:
            dy = -1
        self.v = [dx,dy]
        self.move()

    def reverse_x(self):
        vx, vy = self.v
        self.v = [-vx, vy]

    def reverse_y(self):
        vx, vy = self.v
        self.v = [vx, -vy]

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


chicken_pos = (int(display_width * 0.2), int(display_height * 0.2))
dx = -1
dy = -1

chickensprite = Sprite(chicken_pos,'chicken2.png')
##bouncesprite = BounceSprite((x+10, y+20), 10)

crashed = False
buttondown = False

sprite_group = pygame.sprite.Group()
sprite_group.add(chickensprite)

bounce_group = pygame.sprite.Group()
bounce_group.add(chickensprite)

ball_group = pygame.sprite.Group()


def shootBall(x, y):
    ball = BounceSprite((display_width//2, display_height), 10)
    ball.aim((mousex, mousey))
    bounce_group.add(ball)
    ball_group.add(ball)

leftwall = VerticalWallSprite(display_height, (0,0))
topwall = HorizontalWallSprite(display_width, (0,0))
rightwall = VerticalWallSprite(display_height, (display_width-5,0))

wall_group = pygame.sprite.Group()
wall_group.add(leftwall)
wall_group.add(topwall)
wall_group.add(rightwall)

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            buttondown = True
            mousex, mousey = pygame.mouse.get_pos()
            shootBall(mousex, mousey)
        if event.type == pygame.MOUSEBUTTONUP:
            buttondown = False


    if buttondown:
        chickensprite.moveToCursor()
    else:
        chickensprite.move()

    collide = pygame.sprite.spritecollide(chickensprite, ball_group, False)
    for ball in collide:
        ball.flee(chickensprite.pos())

    leftwallcollide = pygame.sprite.spritecollide(leftwall, bounce_group, False)
    for sprite in leftwallcollide:
        print(type(sprite))
        sprite.reverse_x()
    
    topwallcollide = pygame.sprite.spritecollide(topwall, bounce_group, False)
    for sprite in topwallcollide:
        print(type(sprite))
        sprite.reverse_y()
        
    rightwallcollide = pygame.sprite.spritecollide(rightwall, bounce_group, False)
    for sprite in rightwallcollide:
        print(type(sprite))
        sprite.reverse_x()
        

    gameDisplay.fill(blue)
    bounce_group.update()
    ball_group.update()
##    sprite_group.draw(gameDisplay)
    bounce_group.draw(gameDisplay)
    wall_group.draw(gameDisplay)
    
    pygame.display.update()
    clock.tick(20)

pygame.quit()
quit()
