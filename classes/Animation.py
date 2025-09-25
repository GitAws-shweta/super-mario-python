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
