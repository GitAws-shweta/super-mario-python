class Animation:
    def __init__(self, images, idleSprite=None, airSprite=None, deltaTime=7):
        self.images = images
        self.timer = 0
        self.index = 0
        self.image = self.images[self.index]
        self.idleSprite = idleSprite
        self.airSprite = airSprite
        self.deltaTime = deltaTime

    def update(self):
        self.timer += 1
        if self.timer % self.deltaTime == 0:
            if self.index < len(self.images) - 1:
                self.index += 1
            else:
                self.index = 0
        self.image = self.images[self.index]

    def idle(self):
        self.image = self.idleSprite

    def inAir(self):
        self.image = self.airSprite

from classes.Maths import Vec2D


class Camera:
    def __init__(self, pos, entity):
        self.pos = Vec2D(pos.x, pos.y)
        self.entity = entity
        self.x = self.pos.x * 32
        self.y = self.pos.y * 32

    def move(self):
        xPosFloat = self.entity.getPosIndexAsFloat().x
        if 10 < xPosFloat < 50:
            self.pos.x = -xPosFloat + 10
        self.x = self.pos.x * 32
        self.y = self.pos.y * 32


class Collider:
    def __init__(self, entity, level):
        self.entity = entity
        self.level = level.level
        self.levelObj = level
        self.result = []

    def checkX(self):
        if self.leftLevelBorderReached() or self.rightLevelBorderReached():
            return
        try:
            rows = [
                self.level[self.entity.getPosIndex().y],
                self.level[self.entity.getPosIndex().y + 1],
                self.level[self.entity.getPosIndex().y + 2],
            ]
        except Exception:
            return
        for row in rows:
            tiles = row[self.entity.getPosIndex().x : self.entity.getPosIndex().x + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.x > 0:
                            self.entity.rect.right = tile.rect.left
                            self.entity.vel.x = 0
                        if self.entity.vel.x < 0:
                            self.entity.rect.left = tile.rect.right
                            self.entity.vel.x = 0

    def checkY(self):
        self.entity.onGround = False
        
        try:
            rows = [
                self.level[self.entity.getPosIndex().y],
                self.level[self.entity.getPosIndex().y + 1],
                self.level[self.entity.getPosIndex().y + 2],
            ]
        except Exception:
            try:
                self.entity.gameOver()
            except Exception:
                self.entity.alive = None
            return
        for row in rows:
            tiles = row[self.entity.getPosIndex().x : self.entity.getPosIndex().x + 2]
            for tile in tiles:
                if tile.rect is not None:
                    if self.entity.rect.colliderect(tile.rect):
                        if self.entity.vel.y > 0:
                            self.entity.onGround = True
                            self.entity.rect.bottom = tile.rect.top
                            self.entity.vel.y = 0
                            # reset jump on bottom
                            if self.entity.traits is not None:
                                if "JumpTrait" in self.entity.traits:
                                    self.entity.traits["JumpTrait"].reset()
                                if "bounceTrait" in self.entity.traits:
                                    self.entity.traits["bounceTrait"].reset()
                        if self.entity.vel.y < 0:
                            self.entity.rect.top = tile.rect.bottom
                            self.entity.vel.y = 0

    def rightLevelBorderReached(self):
        if self.entity.getPosIndexAsFloat().x > self.levelObj.levelLength - 1:
            self.entity.rect.x = (self.levelObj.levelLength - 1) * 32
            self.entity.vel.x = 0
            return True

    def leftLevelBorderReached(self):
        if self.entity.rect.x < 0:
            self.entity.rect.x = 0
            self.entity.vel.x = 0
            return True


import pygame

from classes.Font import Font


class Dashboard(Font):
    def __init__(self, filePath, size, screen):
        Font.__init__(self, filePath, size)
        self.state = "menu"
        self.screen = screen
        self.levelName = ""
        self.points = 0
        self.coins = 0
        self.ticks = 0
        self.time = 0

    def update(self):
        self.drawText("MARIO", 50, 20, 15)
        self.drawText(self.pointString(), 50, 37, 15)

        self.drawText("@x{}".format(self.coinString()), 225, 37, 15)

        self.drawText("WORLD", 380, 20, 15)
        self.drawText(str(self.levelName), 395, 37, 15)

        self.drawText("TIME", 520, 20, 15)
        if self.state != "menu":
            self.drawText(self.timeString(), 535, 37, 15)

        # update Time
        self.ticks += 1
        if self.ticks == 60:
            self.ticks = 0
            self.time += 1

    def drawText(self, text, x, y, size):
        for char in text:
            charSprite = pygame.transform.scale(self.charSprites[char], (size, size))
            self.screen.blit(charSprite, (x, y))
            if char == " ":
                x += size//2
            else:
                x += size

    def coinString(self):
        return "{:02d}".format(self.coins)

    def pointString(self):
        return "{:06d}".format(self.points)

    def timeString(self):
        return "{:03d}".format(self.time)


class EntityCollider:
    def __init__(self, entity):
        self.entity = entity

    def check(self, target):
        if self.entity.rect.colliderect(target.rect):
            return self.determineSide(target.rect, self.entity.rect)
        return CollisionState(False, False)

    def determineSide(self, rect1, rect2):
        if (
            rect1.collidepoint(rect2.bottomleft)
            or rect1.collidepoint(rect2.bottomright)
            or rect1.collidepoint(rect2.midbottom)
        ):
            if rect2.collidepoint(
                (rect1.midleft[0] / 2, rect1.midleft[1] / 2)
            ) or rect2.collidepoint((rect1.midright[0] / 2, rect1.midright[1] / 2)):
                return CollisionState(True, False)
            else:
                if self.entity.vel.y > 0:
                    return CollisionState(True, True)
        return CollisionState(True, False)


class CollisionState:
    def __init__(self, _isColliding, _isTop):
        self.isColliding = _isColliding
        self.isTop = _isTop


from classes.Spritesheet import Spritesheet
import pygame


class Font(Spritesheet):
    def __init__(self, filePath, size):
        Spritesheet.__init__(self, filename=filePath)
        self.chars = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        self.charSprites = self.loadFont()

    def loadFont(self):
        font = {}
        row = 0
        charAt = 0

        for char in self.chars:
            if charAt == 16:
                charAt = 0
                row += 1
            font.update(
                {
                    char: self.image_at(
                        charAt,
                        row,
                        2,
                        colorkey=pygame.color.Color(0, 0, 0),
                        xTileSize=8,
                        yTileSize=8
                    )
                }
            )
            charAt += 1
        return font


import pygame
from scipy.ndimage.filters import *


class GaussianBlur:
    def __init__(self, kernelsize=7):
        self.kernel_size = kernelsize

    def filter(self, srfc, xpos, ypos, width, height):
        nSrfc = pygame.Surface((width, height))
        pxa = pygame.surfarray.array3d(srfc)
        blurred = gaussian_filter(pxa, sigma=(self.kernel_size, self.kernel_size, 0))
        pygame.surfarray.blit_array(nSrfc, blurred)
        del pxa
        return nSrfc

import pygame
from pygame.locals import *
import sys


class Input:
    def __init__(self, entity):
        self.mouseX = 0
        self.mouseY = 0
        self.entity = entity

    def checkForInput(self):
        events = pygame.event.get()
        self.checkForKeyboardInput()
        self.checkForMouseInput(events)
        self.checkForQuitAndRestartInputEvents(events)

    def checkForKeyboardInput(self):
        pressedKeys = pygame.key.get_pressed()

        if pressedKeys[K_LEFT] or pressedKeys[K_h] and not pressedKeys[K_RIGHT]:
            self.entity.traits["goTrait"].direction = -1
        elif pressedKeys[K_RIGHT] or pressedKeys[K_l] and not pressedKeys[K_LEFT]:
            self.entity.traits["goTrait"].direction = 1
        else:
            self.entity.traits['goTrait'].direction = 0

        isJumping = pressedKeys[K_SPACE] or pressedKeys[K_UP] or pressedKeys[K_k]
        self.entity.traits['jumpTrait'].jump(isJumping)

        self.entity.traits['goTrait'].boost = pressedKeys[K_LSHIFT]

    def checkForMouseInput(self, events):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.isRightMouseButtonPressed(events):
            self.entity.levelObj.addKoopa(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
            self.entity.levelObj.addGoomba(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
            self.entity.levelObj.addRedMushroom(
                mouseY / 32, mouseX / 32 - self.entity.camera.pos.x
            )
        if self.isLeftMouseButtonPressed(events):
            self.entity.levelObj.addCoin(
                mouseX / 32 - self.entity.camera.pos.x, mouseY / 32
            )

    def checkForQuitAndRestartInputEvents(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and \
                (event.key == pygame.K_ESCAPE or event.key == pygame.K_F5):
                self.entity.pause = True
                self.entity.pauseObj.createBackgroundBlur()

    def isLeftMouseButtonPressed(self, events):
        return self.checkMouse(events, 1)

    def isRightMouseButtonPressed(self, events):
        return self.checkMouse(events, 3)

    def checkMouse(self, events, button):
        for e in events:
            if e.type == pygame.MOUSEBUTTONUP and e.button == button:
                return True
        return False


import json
import pygame

from classes.Sprites import Sprites
from classes.Tile import Tile
from entities.Coin import Coin
from entities.CoinBrick import CoinBrick
from entities.Goomba import Goomba
from entities.Mushroom import RedMushroom
from entities.Koopa import Koopa
from entities.CoinBox import CoinBox
from entities.RandomBox import RandomBox


class Level:
    def __init__(self, screen, sound, dashboard):
        self.sprites = Sprites()
        self.dashboard = dashboard
        self.sound = sound
        self.screen = screen
        self.level = None
        self.levelLength = 0
        self.entityList = []

    def loadLevel(self, levelname):
        with open("./levels/{}.json".format(levelname)) as jsonData:
            data = json.load(jsonData)
            self.loadLayers(data)
            self.loadObjects(data)
            self.loadEntities(data)
            self.levelLength = data["length"]

    def loadEntities(self, data):
        try:
            [self.addCoinBox(x, y) for x, y in data["level"]["entities"]["CoinBox"]]
            [self.addGoomba(x, y) for x, y in data["level"]["entities"]["Goomba"]]
            [self.addKoopa(x, y) for x, y in data["level"]["entities"]["Koopa"]]
            [self.addCoin(x, y) for x, y in data["level"]["entities"]["coin"]]
            [self.addCoinBrick(x, y) for x, y in data["level"]["entities"]["coinBrick"]]
            [self.addRandomBox(x, y, item) for x, y, item in data["level"]["entities"]["RandomBox"]]
        except:
            # if no entities in Level
            pass

    def loadLayers(self, data):
        layers = []
        for x in range(*data["level"]["layers"]["sky"]["x"]):
            layers.append(
                (
                        [
                            Tile(self.sprites.spriteCollection.get("sky"), None)
                            for y in range(*data["level"]["layers"]["sky"]["y"])
                        ]
                        + [
                            Tile(
                                self.sprites.spriteCollection.get("ground"),
                                pygame.Rect(x * 32, (y - 1) * 32, 32, 32),
                            )
                            for y in range(*data["level"]["layers"]["ground"]["y"])
                        ]
                )
            )
        self.level = list(map(list, zip(*layers)))

    def loadObjects(self, data):
        for x, y in data["level"]["objects"]["bush"]:
            self.addBushSprite(x, y)
        for x, y in data["level"]["objects"]["cloud"]:
            self.addCloudSprite(x, y)
        for x, y, z in data["level"]["objects"]["pipe"]:
            self.addPipeSprite(x, y, z)
        for x, y in data["level"]["objects"]["sky"]:
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("sky"), None)
        for x, y in data["level"]["objects"]["ground"]:
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("ground"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )

    def updateEntities(self, cam):
        for entity in self.entityList:
            entity.update(cam)
            if entity.alive is None:
                self.entityList.remove(entity)

    def drawLevel(self, camera):
        try:
            for y in range(0, 15):
                for x in range(0 - int(camera.pos.x + 1), 20 - int(camera.pos.x - 1)):
                    if self.level[y][x].sprite is not None:
                        if self.level[y][x].sprite.redrawBackground:
                            self.screen.blit(
                                self.sprites.spriteCollection.get("sky").image,
                                ((x + camera.pos.x) * 32, y * 32),
                            )
                        self.level[y][x].sprite.drawSprite(
                            x + camera.pos.x, y, self.screen
                        )
            self.updateEntities(camera)
        except IndexError:
            return

    def addCloudSprite(self, x, y):
        try:
            for yOff in range(0, 2):
                for xOff in range(0, 3):
                    self.level[y + yOff][x + xOff] = Tile(
                        self.sprites.spriteCollection.get("cloud{}_{}".format(yOff + 1, xOff + 1)), None, )
        except IndexError:
            return

    def addPipeSprite(self, x, y, length=2):
        try:
            # add pipe head
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("pipeL"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("pipeR"),
                pygame.Rect((x + 1) * 32, y * 32, 32, 32),
            )
            # add pipe body
            for i in range(1, length + 20):
                self.level[y + i][x] = Tile(
                    self.sprites.spriteCollection.get("pipe2L"),
                    pygame.Rect(x * 32, (y + i) * 32, 32, 32),
                )
                self.level[y + i][x + 1] = Tile(
                    self.sprites.spriteCollection.get("pipe2R"),
                    pygame.Rect((x + 1) * 32, (y + i) * 32, 32, 32),
                )
        except IndexError:
            return

    def addBushSprite(self, x, y):
        try:
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("bush_1"), None)
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("bush_2"), None
            )
            self.level[y][x + 2] = Tile(
                self.sprites.spriteCollection.get("bush_3"), None
            )
        except IndexError:
            return

    def addCoinBox(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            CoinBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.sound,
                self.dashboard,
            )
        )

    def addRandomBox(self, x, y, item):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            RandomBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                item,
                self.sound,
                self.dashboard,
                self
            )
        )

    def addCoin(self, x, y):
        self.entityList.append(Coin(self.screen, self.sprites.spriteCollection, x, y))

    def addCoinBrick(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            CoinBrick(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.sound,
                self.dashboard
            )
        )

    def addGoomba(self, x, y):
        self.entityList.append(
            Goomba(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

    def addKoopa(self, x, y):
        self.entityList.append(
            Koopa(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

    def addRedMushroom(self, x, y):
        self.entityList.append(
            RedMushroom(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

class Vec2D:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y



