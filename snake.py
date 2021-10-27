'''Snake game'''

__author__ = 'Weigao Sun'
__email__ = 'swg9527666@csu.fullerton.edu'
__maintainer__ = 'WeigaoSun'


import sys
import random
import os
import time
import json
import pygame

WINDOWWIDTH = 800
WINDOWHEIGHT = 600

# board corner
BLEFT = 40
BUP = 40
BOARDR = 760
BOARDB = 560

CELLSIZE = 40
CELLX = (BOARDR - CELLSIZE)//CELLSIZE
CELLY = (BOARDB - CELLSIZE)//CELLSIZE
RADIUS = CELLSIZE//2

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
RED = (255, 0, 0)

# game status
GAME_START = 0
GAME_ON = 1
GAME_OVER = 2
GAME_QUIT = 3

FPS = 60
DIRUP = 0
DIRLEFT = 1
DIRDOWN = 2
DIRRIGHT = 3
SPEED = 2


def cellx2px(xval):
    ''' change cell x to pix x '''
    return BLEFT + xval*CELLSIZE + RADIUS


def celly2py(yval):
    '''change cell y to pix y '''
    return BUP + yval*CELLSIZE + RADIUS


class P2v:
    ''' 2d point or vector class '''

    def __init__(self, x=0, y=0):
        self.xval = x
        self.yval = y

    def __iadd__(self, rhs):
        self.xval += rhs.xval
        self.yval += rhs.yval
        return self

    def __add__(self, rhs):
        return P2v(self.xval + rhs.xval, self.yval + rhs.yval)

    def __eq__(self, rhs):
        return self.xval == rhs.xval and self.yval == rhs.yval


class Snakesegment:
    ''' body segment of the snake '''

    def __init__(self, x, y, targetx, targety):

        self.target = None
        self.celltarget = None
        self.dval = P2v()

        self.cellpos = P2v(x, y)
        self.pos = P2v(cellx2px(x), celly2py(y))

        self.settarget(targetx, targety, False)

    def update(self):
        ''' update segment pos '''
        if not self.finishmove():
            self.pos += self.dval

    def finishmove(self):
        ''' check if the movement is done '''
        return self.pos == self.target

    def draw(self, screen):
        ''' draw sement '''
        pygame.draw.circle(
            screen, GREEN, (self.pos.xval, self.pos.yval), RADIUS)

    def settarget(self, targetx, targety, updatexy=True):
        ''' set target position'''
        if updatexy:
            self.cellpos = self.celltarget
            self.pos = self.target

        self.target = P2v(cellx2px(targetx), celly2py(targety))
        self.celltarget = P2v(targetx, targety)

        # update speed
        self.dval.xval = 0
        self.dval.yval = 0

        if self.cellpos.xval < targetx:
            self.dval.xval = SPEED
        elif self.cellpos.xval > targetx:
            self.dval.xval = -SPEED

        if self.cellpos.yval < targety:
            self.dval.yval = SPEED
        elif self.cellpos.yval > targety:
            self.dval.yval = -SPEED


class Snake:
    ''' the snake class  '''

    def __init__(self):
        headx = random.randint(4, CELLX-5)
        heady = random.randint(4, CELLY-5)
        self.die = False
        self.dir = random.randint(0, 3)
        self.nextdir = self.dir
        if self.dir == DIRUP:
            self.seg = [Snakesegment(headx, heady, headx, heady - 1),
                        Snakesegment(headx, heady + 1, headx, heady),
                        Snakesegment(headx, heady + 2, headx, heady + 1)]
        elif self.dir == DIRLEFT:
            self.seg = [Snakesegment(headx, heady, headx - 1, heady),
                        Snakesegment(headx + 1, heady, headx, heady),
                        Snakesegment(headx + 2, heady, headx + 1, heady)]
        elif self.dir == DIRDOWN:
            self.seg = [Snakesegment(headx, heady, headx, heady + 1),
                        Snakesegment(headx, heady - 1, headx, heady),
                        Snakesegment(headx, heady - 2, headx, heady - 1)]
        else:
            self.seg = [Snakesegment(headx, heady, headx + 1, heady),
                        Snakesegment(headx - 1, heady, headx, heady),
                        Snakesegment(headx - 2, heady, headx - 1, heady)]

    def draw(self, screen):
        ''' draw snake '''
        for i in self.seg:
            i.draw(screen)

    def checkdir_change(self):
        ''' check if dir changed '''
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_UP] and self.dir != DIRDOWN:
            self.nextdir = DIRUP

        elif keys_pressed[pygame.K_DOWN] and self.dir != DIRUP:
            self.nextdir = DIRDOWN

        elif keys_pressed[pygame.K_LEFT] and self.dir != DIRRIGHT:
            self.nextdir = DIRLEFT

        elif keys_pressed[pygame.K_RIGHT] and self.dir != DIRLEFT:
            self.nextdir = DIRRIGHT

    def check_die(self, cellx, celly):
        ''' check if snake die '''

        for i in range(1, len(self.seg)):
            # check run into itself
            if self.seg[0].celltarget == self.seg[i].celltarget:
                self.die = True
                break

        # update next cell to go, if next cell invalid, snake die
        if self.dir == DIRUP:
            nextx = cellx
            nexty = celly - 1
            if nexty < 0:
                self.die = True

        elif self.dir == DIRLEFT:
            nextx = cellx - 1
            nexty = celly
            if nextx < 0:
                self.die = True

        elif self.dir == DIRDOWN:
            nextx = cellx
            nexty = celly + 1
            if nexty == CELLY:
                self.die = True

        elif self.dir == DIRRIGHT:
            nextx = cellx + 1
            nexty = celly
            if nextx == CELLX:
                self.die = True

        return nextx, nexty

    def update(self, food, gameobj):
        ''' update snake '''
        for i in self.seg:
            i.update()

        self.checkdir_change()

        if self.seg[0].finishmove():
            self.dir = self.nextdir  # update dir
            cellx = self.seg[0].celltarget.xval
            celly = self.seg[0].celltarget.yval
            if self.seg[0].celltarget == food.cellpos:
                self.seg.append(Snakesegment(self.seg[-1].cellpos.xval,
                                             self.seg[-1].cellpos.yval,
                                             self.seg[-1].celltarget.xval,
                                             self.seg[-1].celltarget.yval))
                food.eaten = True
                gameobj.score += 10

            nextx, nexty = self.check_die(cellx, celly)

            if self.die:
                return

            self.seg[0].settarget(nextx, nexty)
            for i in range(1, len(self.seg)):
                self.seg[i].settarget(self.seg[i-1].cellpos.xval,
                                      self.seg[i-1].cellpos.yval)


class Food:
    ''' food class '''

    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, xval, yval):
        ''' reset food info '''
        self.cellpos = P2v(xval, yval)
        self.pos = cellx2px(xval), celly2py(yval)
        self.life = 3 * FPS
        self.eaten = False

    def update(self):
        '''  update food life '''
        self.life -= 1

    def draw(self, screen):
        ''' draw food on screen '''
        if not self.eaten:
            pygame.draw.circle(screen, RED, self.pos, RADIUS)


class Snakegame:
    ''' snamegame class '''

    def __init__(self):
        self.tophistory = []
        self.loadtopscore()
        self.food = None
        self.tick = 0
        self.score = 0
        self.snake = None
        self.gamestatus = GAME_START
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    def loadtopscore(self):
        ''' load top10 score from file'''
        if os.path.exists('topscore.json'):
            with open('topscore.json', 'r') as fin:
                self.tophistory = json.load(fin)

    def startmenu(self):
        ''' show start menu'''
        bigfont = pygame.font.Font(None, 80)
        smallfont = pygame.font.Font(None, 40)

        gametitle = bigfont.render('Snake Game', True, WHITE)
        controlinfo = smallfont.render(
            'Use Arrow Key to control the snake', True, YELLOW)
        ruleinfo1 = smallfont.render(
            '         Eat food to grow and score', True, YELLOW)
        ruleinfo2 = smallfont.render(
            '         Stay alive as long as you can', True, YELLOW)
        ruleinfo3 = smallfont.render(
            'Hit the border or your body, GAME OVER! ', True, RED)
        startinfo = smallfont.render(
            'Press SPACE to Start', True, GREEN)

        self.screen.fill(BLACK)
        self.screen.blit(gametitle, (280, 100))
        self.screen.blit(controlinfo, (180, 250))
        self.screen.blit(ruleinfo1, (150, 300))
        self.screen.blit(ruleinfo2, (150, 350))
        self.screen.blit(ruleinfo3, (150, 400))
        self.screen.blit(startinfo, (280, 500))
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_SPACE]:
            self.gamestatus = GAME_ON
            self.initgame()

    def initgame(self):
        ''' init the game '''
        self.tick = 0
        self.score = 0
        self.snake = Snake()
        xval, yval = self.genfoodpos()
        self.food = Food(xval, yval)

    def genfoodpos(self):
        ''' generate food position'''
        success = False
        while not success:
            xval = random.randint(0, CELLX - 1)
            yval = random.randint(0, CELLY - 1)
            success = True
            for i in self.snake.seg:
                if xval == i.cellpos.xval and yval == i.cellpos.yval:
                    success = False
                    break
        return xval, yval

    def drawboard(self):
        ''' draw board on screen '''
        for i in range(BLEFT, BOARDR + 1, CELLSIZE):
            pygame.draw.line(self.screen, GRAY, (i, BUP), (i, BOARDB))

        for i in range(BUP, BOARDB + 1, CELLSIZE):
            pygame.draw.line(self.screen, GRAY, (BLEFT, i), (BOARDR, i))

    def update(self):
        ''' update the game'''
        self.tick += 1
        if self.tick % (3 * FPS) == 0:
            self.score += 1

        self.snake.update(self.food, self)
        self.food.update()
        if self.food.life == 0:
            xval, yval = self.genfoodpos()
            self.food = Food(xval, yval)

    def run(self):
        ''' run the game '''
        self.update()
        if self.snake.die:
            self.gamestatus = GAME_OVER
            datestr = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            self.tophistory.append({'date': datestr,
                                    'playtime': self.tick//FPS,
                                    'score': self.score})
            self.tophistory = sorted(self.tophistory,
                                     key=lambda i: i['score'], reverse=True)
            with open('topscore.json', 'w') as fout:
                json.dump(self.tophistory, fout)
        else:
            self.screen.fill(BLACK)
            self.draw()

    def drawscore(self):
        ''' show score on screen'''
        smallfont = pygame.font.Font(None, 40)
        scorestr = "score: " + str(self.score)
        scoresuf = smallfont.render(scorestr, True, WHITE)
        self.screen.blit(scoresuf, (0, 0))

    def draw(self):
        ''' draw the game'''
        self.drawboard()
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        self.drawscore()

    def gameover(self):
        ''' game over show'''
        bigfont = pygame.font.Font(None, 60)
        smallfont = pygame.font.Font(None, 40)
        gameoverinfo = bigfont.render('Game Over', True, WHITE)
        highsocreinfo = smallfont.render('High Score', True, YELLOW)
        titlestr = '{0:<10}{1:>16}{2:>10}'.format(
            'Date', 'Time-played', 'Score')
        socretitle = smallfont.render(titlestr, True, YELLOW)
        choiceinfo = smallfont.render(
            'Press SPACE to Play again or ESC to Quit', True, GREEN)
        self.screen.fill(BLACK)
        self.screen.blit(gameoverinfo, (280, 20))
        self.screen.blit(highsocreinfo, (320, 80))
        self.screen.blit(socretitle, (160, 120))
        j = 160
        top_10 = self.tophistory[:10] if len(
            self.tophistory) > 10 else self.tophistory
        for his in top_10:
            infostr = '{0:>10}{1:>10}{2:>20}'.format(
                his['date'], his['playtime'], his['score'])
            self.screen.blit(smallfont.render(infostr, True, YELLOW), (160, j))
            j += 40
        self.screen.blit(choiceinfo, (140, 560))
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_SPACE]:
            self.gamestatus = GAME_ON
            self.initgame()
        elif keys_pressed[pygame.K_ESCAPE]:
            self.gamestatus = GAME_QUIT


if __name__ == '__main__':
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    GAME = Snakegame()

    while GAME.gamestatus != GAME_QUIT:
        FPSCLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if GAME.gamestatus == GAME_START:
            GAME.startmenu()

        elif GAME.gamestatus == GAME_ON:
            GAME.run()

        else:
            GAME.gameover()

        pygame.display.update()

    pygame.quit()
