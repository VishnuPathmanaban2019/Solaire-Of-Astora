#################################################
# Developer: Vishnu Pathmanaban
# Email: vpathman@andrew.cmu.edu
# Start Date: 10/24/2019
# Last Updated: 10/26/2019
# Title: Solaire Of Astora
# Notes:
# - sidescroller fantasy game
# - pip install pillow!
#################################################

#SOLAIRE OF ASTORA

from cmu_112_graphics import *
from tkinter import *
from PIL import Image
import math, random

#Solaire class with animation spritesheets.
class Solaire(object):
    def __init__(self, app, spritestrip):
        self.app = app
        self.spritestrip = spritestrip
        #Spritesheets for four directions of motion.
        self.sprites = [([] * 1) for row in range(4)]
        for i in range(6):
            sprite = self.spritestrip.crop((80*i ,0, 80+80*i, 80))
            self.sprites[0].append(sprite)
        for i in range(6):
            sprite = self.spritestrip.crop((80*i ,0, 80+80*i, 80))
            sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
            self.sprites[1].append(sprite)
        for i in range(6):
            sprite = self.spritestrip.crop((80*i ,400, 80+80*i, 480))
            self.sprites[2].append(sprite)
        for i in range(6,12):
            sprite = self.spritestrip.crop((80*i ,400, 80+80*i, 480))
            self.sprites[3].append(sprite)
        self.deathSprite = self.spritestrip.crop((720 , 0, 800, 80))
        self.winSprite = self.spritestrip.crop((480 , 880, 560, 960))
        self.moving = False
        self.spriteCounter = 0
        self.direction = 0
        self.x = 250
        self.y = 250
        self.souls = 0

#Hollow class with random starting location.
class Hollow(object):
    def __init__(self, app, spritestrip):
        self.app = app
        self.spritestrip = spritestrip
        self.hollowSprite = self.spritestrip.crop((240 , 880, 320, 960))
        self.soulSprite = self.spritestrip.crop((320 , 880, 400, 960))
        self.sprite = self.hollowSprite
        self.initialX = random.randint(-200,700)
        self.initialY = random.randint(-200,700)
        self.x = self.initialX
        self.y = self.initialY
        self.shadowBall = None
        self.soul = False
        self.mobile = False
        self.teleporting = False
        self.visible = True

    def __hash__(self):
        return hash((self.initialX,self.initialY))

    def __eq__(self, other):
        return (isinstance(other, Hollow) and (self.soul == other.soul))

    #Conjures up a hollow projectile.
    def attack(self):
        if(self.soul==False):
            self.shadowBall=ShadowBall(self.app,self.spritestrip,self.x,self.y)

#Hollow subclass that moves toward player.
class MobileHollow(Hollow):
    def __init__(self, app, spritestrip):
        super().__init__(app, spritestrip)
        self.mobile = True

    #Move to player method.
    def move(self, speed):
        if(self.soul==False):
            self.x+=((self.app.solaire.x)-(self.x))*speed
            self.y+=((self.app.solaire.y)-(self.y))*speed

#Hollow subclass that randomly teleports.
class TeleportingHollow(Hollow):
    def __init__(self, app, spritestrip):
        super().__init__(app, spritestrip)
        self.teleporting = True

    #Teleport near player method.
    def teleport(self):
        if(self.soul==False):
            self.x = random.randint(100,400)
            self.y = random.randint(100,400)

#Hollow projectile that has a speed based on the distance between the Hollow
#and Solaire.
class ShadowBall(object):
    def __init__(self, app, spritestrip, x, y):
        self.app = app
        self.spritestrip = spritestrip
        self.sprite = self.spritestrip.crop((80 , 880, 160, 960))
        self.x = x
        self.y = y
        self.direction = ((self.app.solaire.x)-(self.x),
                          (self.app.solaire.y)-(self.y))
        self.reflected = False
        self.visible = True

    #Controls motion of hollow projectile.
    def shoot(self, speed):
        if(self.reflected == True):
            speed *= -1
        self.x += self.direction[0]*speed
        self.y += self.direction[1]*speed

#Shield class with random starting location.
class Shield(object):
    def __init__(self, app, spritestrip):
        self.app = app
        self.spritestrip = spritestrip
        self.sprite = self.spritestrip.crop((800 , 800, 960, 960))
        self.x = random.randint(-100,600)
        self.y = random.randint(-100,600)

#Cursor class with cursor sprite.
class Cursor(object):
    def __init__(self, app, spritestrip):
        self.app = app
        self.spritestrip = spritestrip
        self.sprite = self.spritestrip.crop((160, 880, 240, 960))
        self.x = 0
        self.y = 0

#Starting screen.
class SplashScreenMode(Mode):
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0,0,mode.width,mode.height,
                                fill='gray',outline='black', width=20)
        canvas.create_text(mode.width/2, 150, text='Solaire of Astora',
                           fill='gold', font='Times 28 bold italic underline')
        canvas.create_text(mode.width/2, 200,
                           text='Developed by Vishnu Pathmanaban',
                           fill='black', font='Times 14 bold')
        canvas.create_text(mode.width/2, 400, text='PRESS ANY KEY TO BEGIN',
                           fill='gold', font='Times 14 bold')

    #Switches to main game when any key is pressed.
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

#Main game.
class GameMode(Mode):
    def appStarted(mode):
        url = 'http://i.imgur.com/LGtN5jY.png?1'
        spritestrip = mode.loadImage(url)
        mode.solaire = Solaire(mode, spritestrip)
        mode.hollows = set()
        #Number of enemies to beat.
        mode.goal = 6
        #Randomization of hollow types.
        while(len(mode.hollows)<mode.goal):
            n = random.randint(0,2)
            if n == 0: mode.hollows.add(Hollow(mode, spritestrip))
            elif n == 1: mode.hollows.add(MobileHollow(mode, spritestrip))
            else: mode.hollows.add(TeleportingHollow(mode, spritestrip))
        mode.shield = Shield(mode, spritestrip)
        mode.cursor = Cursor(mode, spritestrip)
        mode.timer = 0
        mode.gameOver = False
        mode.win = False
        mode.scrollX = 0
        mode.scrollY = 0
        #Room bounds.
        mode.x1,mode.y1 = -250,-250
        mode.x2,mode.y2 = 750,750
        mode.app._root.configure(cursor='none')

    #Timer reliant actions for game.
    def timerFired(mode):
        if(mode.gameOver==False):
            mode.timer+=1
            #Winning conditions.
            if mode.solaire.souls>=mode.goal:mode.gameOver,mode.win=True,True
            if(mode.solaire.moving):
                    frames = len(mode.solaire.sprites[0])
                    counter = (1+mode.solaire.spriteCounter)%frames
                    mode.solaire.spriteCounter = counter
            #Iterates through set of Hollows to trigger Hollow actions.
            for hollow in mode.hollows:
                if (hollow.mobile):
                    hollow.move(0.005)
                if (hollow.teleporting and mode.timer%90==0):
                    hollow.teleport()
                if(abs(mode.solaire.x-hollow.x)<30 and
                   abs(mode.solaire.y-hollow.y)<30 and
                   hollow.soul==True and
                   hollow.visible==True):
                        hollow.visible = False
                        mode.solaire.souls+=1
                if(mode.timer%25==0):
                    if(abs(hollow.x-mode.solaire.x)<210 and
                       abs(hollow.y-mode.solaire.y)<210):
                        hollow.attack()
                #Hollow projectile movement and collision checks.
                if(hollow.shadowBall != None):
                    hollow.shadowBall.shoot(0.1)
                    if(abs(hollow.shadowBall.x-mode.solaire.x)<30 and
                       abs(hollow.shadowBall.y-mode.solaire.y)<30):
                        mode.gameOver = True
                    if(abs(hollow.shadowBall.x-mode.shield.x)<60 and
                       abs(hollow.shadowBall.y-mode.shield.y)<60):
                        hollow.shadowBall.reflected = True
                        hollow.shadowBall.shoot(0.1)
                    if(abs(hollow.shadowBall.x-hollow.x)<30 and
                       abs(hollow.shadowBall.y-hollow.y)<30 and
                       hollow.shadowBall.reflected==True):
                        hollow.sprite = hollow.soulSprite
                        hollow.soul = True
                        hollow.shadowBall.visible = False

    #Key actions.            
    def keyPressed(mode, event):
        if (event.key == 'h'):
            mode.app.setActiveMode(mode.app.helpMode)
        #Superhelp display in console.
        if (event.key == 'S'):
            print('''
            Controls:
            - Move Solaire with WASD
            - Move shield by dragging with mouse
            - Press R to restart

            Gameplay:
            - Help Solaire defeat the Hollows!
            - Find Solaire's shield by exploring the dungeon
            - Use Solaire's shield to reflect Hollow attacks
            - Gather all the Hollow souls to win

            Hints:
            - Hollows can move and teleport randomly
            - Hollows will only attack when in range

            Superhelp:
            1. Everything only happens within the gray rectangle,
            no need to travel outside of it
            2. First explore the area and find the shield
            3. Click and drag the shield to move it
            4. Reflect shadow balls back at Hollows with shield
            5. Collect the souls after Hollows are killed
            6. If there are souls left but no Hollows in sight
            keep searching, it is most likely a teleporting Hollow
            ''')
        #Solaire movement control with WASD.
        if(mode.gameOver==False):
            if event.key == 'd':
                mode.scrollX=5
                mode.solaire.direction=0
            if event.key == 'a':
                mode.scrollX=-5
                mode.solaire.direction=1
            if event.key == 'w':
                mode.scrollY=-5
                mode.solaire.direction=2
            if event.key == 's':
                mode.scrollY=5
                mode.solaire.direction=3
            if(mode.solaire.moving==False):
                mode.solaire.moving = True
        if (event.key == 'r'):
            mode.appStarted()
            mode.app.setActiveMode(mode.app.splashScreenMode)

    #Standing animation when key is released.
    def keyReleased(mode, event):
        if(mode.gameOver==False):
            mode.solaire.spriteCounter = 0
            mode.solaire.moving = False
            mode.scrollX = 0
            mode.scrollY = 0

    #Shield movement control with mouse.
    def mouseDragged(mode, event):
        if(abs(event.x-mode.shield.x)<60 and
           abs(event.y-mode.shield.y)<60):
            mode.shield.x = event.x
            mode.shield.y = event.y
        mode.cursor.x = event.x
        mode.cursor.y = event.y

    #Cursor movement.
    def mouseMoved(mode, event):
        mode.cursor.x = event.x
        mode.cursor.y = event.y

    #Graphical view for main game.
    def redrawAll(mode, canvas):
        #Winning and losing screens.
        if(mode.gameOver):
            canvas.create_rectangle(0,0,mode.width,mode.height,
                                fill='gray',outline='black', width=20)
            canvas.create_text(mode.width/2, 400, text='PRESS R TO RESTART',
                           fill='black', font='Times 14 bold')
            if(mode.win):
                canvas.create_image(mode.solaire.x, mode.solaire.y,
                            image=ImageTk.PhotoImage(mode.solaire.winSprite))
                canvas.create_text(mode.width/2, 350, text='PRAISE THE SUN!',
                           fill='gold', font='Times 28 bold underline')
            else:
                canvas.create_image(mode.solaire.x, mode.solaire.y,
                            image=ImageTk.PhotoImage(mode.solaire.deathSprite))
                canvas.create_text(mode.width/2, 350, text='YOU DIED',
                           fill='red', font='Times 28 bold underline')
        else:
            #Draws the gray area.
            mode.x1-=mode.scrollX
            mode.y1-=mode.scrollY
            mode.x2-=mode.scrollX
            mode.y2-=mode.scrollY
            canvas.create_rectangle(mode.x1,mode.y1,mode.x2,mode.y2,
                                    fill='gray',outline='black',width=20)
            #Draws Solaire.
            solaire=mode.solaire.sprites[mode.solaire.direction]\
                                        [mode.solaire.spriteCounter]
            canvas.create_image(mode.solaire.x, mode.solaire.y,
                                image=ImageTk.PhotoImage(solaire))
            #Draws the shield.
            mode.shield.x-=mode.scrollX
            mode.shield.y-=mode.scrollY
            canvas.create_image(mode.shield.x,mode.shield.y,
                                image=ImageTk.PhotoImage(mode.shield.sprite))
            #Iterates through set to draw each Hollow and their projectiles.
            for hollow in mode.hollows:
                if hollow.visible:
                    hollow.x-=mode.scrollX
                    hollow.y-=mode.scrollY
                    canvas.create_image(hollow.x,hollow.y,
                                        image=ImageTk.PhotoImage(hollow.sprite))
                if(hollow.shadowBall != None and hollow.shadowBall.visible):
                    hollow.shadowBall.x-=mode.scrollX
                    hollow.shadowBall.y-=mode.scrollY
                    canvas.create_image(hollow.shadowBall.x,
                                        hollow.shadowBall.y,
                       image=ImageTk.PhotoImage(hollow.shadowBall.sprite))
            #Draws screen text and cursor.
            soulsLeft=mode.goal-mode.solaire.souls
            canvas.create_text(250,50,text='Souls Left: %d' % soulsLeft,
                               fill='gold',font="Times 20 bold")
            canvas.create_text(250,450,text='PRESS H FOR HELP',
                               fill='gold',font="Times 20 bold")
            canvas.create_image(mode.cursor.x,mode.cursor.y,
                                image=ImageTk.PhotoImage(mode.cursor.sprite))

#Help screen.
class HelpMode(Mode):
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0,0,mode.width,mode.height,
                                fill='gray',outline='black', width=20)
        canvas.create_text(mode.width/2, 50, text='Help Screen',
                           fill='gold', font='Times 28 bold italic underline')
        helpMessage='''
        Controls:
        - Move Solaire with WASD
        - Move shield by dragging with mouse
        - Press R to restart

        Gameplay:
        - Help Solaire defeat the Hollows!
        - Find Solaire's shield by exploring the dungeon
        - Use Solaire's shield to reflect Hollow attacks
        - Gather all the Hollow souls to win

        Hints:
        - Hollows can move and teleport randomly
        - Hollows will only attack when in range
        '''
        canvas.create_text(mode.width/2, 250, text=helpMessage,
                           fill='black', font='Times 14 bold')
        canvas.create_text(mode.width/2, 450, text='PRESS ANY KEY TO RESUME',
                           fill='gold', font='Times 14 bold')

    #Switches back to main game when any key is pressed.
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.gameMode = GameMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)
        
def runCreativeSidescroller():
    app = MyModalApp(width=500, height=500)

runCreativeSidescroller()
