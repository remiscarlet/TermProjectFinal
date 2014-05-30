#####################################
###### Sprites Management File ######
#####################################
import sprites
import os
import pygame
import math
import random
import bullets
import paths

class Hitbox(pygame.sprite.DirtySprite):
	def __init__(self, size=(8,8)):
		pygame.sprite.DirtySprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama.png")).convert_alpha()
		self.image = master.subsurface((0,240,8,8)) if size == (8,8) else pygame.Surface(size)
		self.rect = self.image.get_rect()


class Reimu(pygame.sprite.DirtySprite):
	def __init__(self, config, centerX, startY):
		pygame.sprite.DirtySprite.__init__(self)
		self.winWidth = 640
		self.winHeight = 480
		master = pygame.image.load(os.path.join(os.path.curdir,"img","sprites","pl00.png")).convert_alpha()
		master_width, master_height = master.get_size()
		self.index = 0
		self.tick = 0
		self.idle = list()
		self.isIdle = True
		self.bullets = list()
		self.power = 0
		for i in xrange(int(master_width/32)):
			self.idle.append(master.subsurface((i*32,0,32,48)))
		self.left = list()
		for i in xrange(int(master_width/32)):
			self.left.append(master.subsurface((i*32,48,32,48)))
		self.right = list()
		for i in xrange(int(master_width/32)):
			self.right.append(master.subsurface((i*32,96,32,48)))
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama2.png")).convert_alpha()
		#Focus ring images
		self.focusImage = master.subsurface((0,16,64,64))#master.subsurface((64,16,64,64))
		self.focusImage2 = master.subsurface((0,16,64,64))
		#They rotate.
		self.focusImageAngle = 0
		self.imageList = self.idle
		self.image = pygame.Surface((64,64), pygame.SRCALPHA, 32).convert_alpha()
		self.rect = self.image.get_rect()
		self.rect.center = (0,0)
		self.hitbox = Hitbox()
		self.lives = 3
		self.isDead = False
		self.deadTimer = 0
		self.isFocused = False
		self.focusLen = 0
		self.centerX = centerX
		self.startY = startY

	def isOnScreen(self, newLoc, GameWin):
		topBorder = GameWin.topBorder
		botBorder = GameWin.botBorder
		leftBorder = GameWin.leftBorder
		rightBorder = GameWin.rightBorder
		horizontalR = self.rect[2]/2
		verticalR = self.rect[3]/2
		left = newLoc[0]-horizontalR
		right = newLoc[0]+horizontalR
		up = newLoc[1]-verticalR
		down = newLoc[1]+verticalR
		if (left<leftBorder or right>rightBorder or
			up<topBorder or down>botBorder):
			return False
		return True

	def shoot(self, group, group2, ticks):
		(x,y) = self.rect.center
		level = self.power/100+1
		if level >= 1:
			group.add(PlayerBullet(0,(x,y+5)))
		if level >= 2 and ticks%16 == 0:
			group2.add(PlayerHomingAmulet((x+15,y-10)))
			group2.add(PlayerHomingAmulet((x-15,y-10)))
			group2.add(PlayerHomingAmulet((x+15,y+10)))
			group2.add(PlayerHomingAmulet((x-15,y+10)))
		if level >= 3:
			group.add(PlayerBullet(-15,(x+10,y+5)))
			group.add(PlayerBullet(+15,(x-10,y+5)))
		if level >= 4 and ticks%16 == 0:
			group2.add(PlayerHomingAmulet((x+30,y)))
			group2.add(PlayerHomingAmulet((x-30,y)))

	def death(self, itemsGroup, power):
		self.focusLen = 0
		self.isDead = True
		self.deadTimer = 0
		self.lives -= 1

	def drawFocusRings(self):
		#scaling the size of the "focus rings" so it "grows" and "shrinks" when you start and end focus
		scaleX = scaleY = int(64*self.focusLen/10.0)
		focusImage = pygame.transform.scale(self.focusImage, (scaleX,scaleY))
		focusImage2 = pygame.transform.scale(self.focusImage2, (scaleX,scaleY))
		self.focusImageAngle += 2
		#ROT_CENTER NOT MY CODE SEE FUNCTION AT BOT OF PAGE FOR CREDITS
		self.image.blit(focusImage, focusImage.get_rect(center=(32,32)))
		self.image.blit(rot_center(focusImage2,
								   -self.focusImageAngle),
						focusImage2.get_rect(center=(32,32)))

	def update(self):
		#Normal animation updates, eg not dead.
		#if self.isDead == False:
		self.tick += 1
		self.image.fill((0,0,0,0))
		lenImg = len(self.imageList)
		self.index = self.tick/24
		if self.index>=lenImg and self.isIdle:
			self.index = lenImg-1
			self.tick = 0
		elif self.index>=lenImg:
			self.index = lenImg-3
			self.tick = lenImg*16
		if self.isFocused == True:
			#Notice how this has to +1 first. Otherwise we'll divide by 0 in drawFocusRings
			self.focusLen = self.focusLen+1 if self.focusLen<10 else 10
			self.drawFocusRings()
		if self.isFocused == False and self.focusLen > 0:
			#Here, we -1 afterwards as to avoid the same issue.
			self.drawFocusRings()
			self.focusLen = self.focusLen-1
		self.image.blit(self.imageList[self.index], (16,8))
		#If dead, gotta do some special stuff.
		if self.isDead == False:
			self.hitbox.rect.center = self.rect.center
		if self.isDead == True and self.deadTimer < 180:
			self.deadTimer += 1
			#resets self image incase we died while focusing
			if self.deadTimer == 1:
				self.image.fill((0,0,0,0))
				self.image.blit(self.imageList[0], (16,8))
				self.hitbox.rect.center = (-10,-10)
				self.rect.center = (-10,-10)
			elif self.deadTimer < 20:
				self.rect.center = (self.centerX, self.winHeight+20)
			#Notice it's <90 and not < 180. This is to give the player a bit of a "grace period" 
			#after respawning to move around and reposition
			elif self.deadTimer >= 20 and self.deadTimer < 90:
				self.rect.center = (self.rect.center[0], self.rect.center[1]-1)
			elif self.deadTimer == 179:
				self.hitbox.rect.center = self.rect.center
		if self.isDead == True and self.deadTimer >= 180: 
			self.isDead = False

class PowerBlock(pygame.sprite.DirtySprite):
	def __init__(self, enemy):
		pygame.sprite.DirtySprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama2.png")).convert_alpha()
		self.image = master.subsurface(2,210,12,12)
		self.rect = self.image.get_rect()
		self.rect.center = enemy.rect.center
		self.vel = -3
		self.autocollect = False
	def update(self, playerPos):
		if not self.autocollect:
			self.vel += 0.2 if self.vel<=0 else 0.05
			self.rect.move_ip(0,self.vel)
			#get distance between item and player pos
			edx, edy = self.rect[0]-playerPos[0], self.rect[1]-playerPos[1]
			if (edx**2+edy**2)**0.5<=50:
				#get the angle between enemy and bullet
				dRadians = math.atan2(edx,edy)
				angle = math.degrees(dRadians)
				dx,dy = 10*math.sin(dRadians), 10*math.cos(dRadians)
				x,y = self.rect[0], self.rect[1]
				self.rect.move_ip(-dx,-dy)
		if self.autocollect:
			#get distance between item and player pos
			edx, edy = self.rect[0]-playerPos[0], self.rect[1]-playerPos[1]
			#get the angle between enemy and bullet
			dRadians = math.atan2(edx,edy)
			angle = math.degrees(dRadians)
			dx,dy = 13*math.sin(dRadians), 13*math.cos(dRadians)
			x,y = self.rect[0], self.rect[1]
			self.rect.move_ip(-dx,-dy)
class PointBlock(pygame.sprite.DirtySprite):
	def __init__(self, enemy):
		pygame.sprite.DirtySprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama2.png")).convert_alpha()
		self.image = master.subsurface(18,210,12,12)
		self.rect = self.image.get_rect()
		self.rect.center = enemy.rect.center
		self.vel = -3
		self.autocollect = False
	def update(self, playerPos):
		if not self.autocollect:
			self.vel += 0.2 if self.vel<=0 else 0.05
			self.rect.move_ip(0,self.vel)
			#get distance between item and player pos
			edx, edy = self.rect[0]-playerPos[0], self.rect[1]-playerPos[1]
			if (edx**2+edy**2)**0.5<=50:
				#get the angle between enemy and bullet
				dRadians = math.atan2(edx,edy)
				angle = math.degrees(dRadians)
				dx,dy = 10*math.sin(dRadians), 10*math.cos(dRadians)
				x,y = self.rect[0], self.rect[1]
				self.rect.move_ip(-dx,-dy)
		if self.autocollect:
			#get distance between item and player pos
			edx, edy = self.rect[0]-playerPos[0], self.rect[1]-playerPos[1]
			#get the angle between enemy and bullet
			dRadians = math.atan2(edx,edy)
			angle = math.degrees(dRadians)
			dx,dy = 13*math.sin(dRadians), 13*math.cos(dRadians)
			x,y = self.rect[0], self.rect[1]
			self.rect.move_ip(-dx,-dy)


class EnemyFairy1(pygame.sprite.DirtySprite):
	######### MODIFY CODE TO PARSE EQ PROPERLY #HAH JK I DON'T HAVE ENOUGH TIME
	#def __init__(self, Touhou, pos=(100,100), pathType="Still", vel=0, direction="right", eq=0):
	def __init__(self, Touhou, pos=(100,100), pathType="Still", **kwargs):
		pygame.sprite.DirtySprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","enemy.png")).convert_alpha()
		self.index = 0
		self.tick = 0
		self.screenRect = Touhou.GameWin.gameScreenRect
		numOfFrames = 12
		self.idle = list()
		self.left = list()
		self.right = list()
		self.isIdle = True
		self.bullets = list()
		self.bulletGroup = pygame.sprite.Group()
		self.health = 10
		self.onScreen = False
		for i in xrange(numOfFrames):
			self.left.append(master.subsurface((i*32,8*32,32,32)))
		for frame in self.left:
			self.right.append(pygame.transform.flip(frame, True, False))
		for i in xrange(4): #arbitrary number of frames for idle
			self.idle.append(master.subsurface((i*32,8*32,32,32)))
		self.imageList = self.idle
		self.image = self.imageList[0]
		self.rect = self.image.get_rect()
		self.pos = pos
		self.rect.center = self.pos
		self.initFairyAttributes(pathType, **kwargs)

	def initFairyAttributes(self, pathType, **kwargs):
		##### Path parsing #####
		# Exact attributes are parsed within the path inits themselves in the paths file
		self.path = eval("paths."+str(pathType)+"(**kwargs)")
		##### Shot type parsing #####
		self.shotType = kwargs["shotType"] if "shotType" in kwargs else "random"
		self.shotFreq = kwargs["shotFreq"] if "shotFreq" in kwargs else "1" #from 1 to 10
		self.shotVel = kwargs["shotVel"] if "shotVel" in kwargs else 1
		self.ringCount = kwargs["ringCount"] if "ringCount" in kwargs else 2
		self.numShots = kwargs["numShots"] if "numShots" in kwargs else 20
		self.shotDVel = kwargs["shotDVel"] if "shotDVel" in kwargs else 0.1
		self.shotAngle = kwargs["shotAngle"] if "shotAngle" in kwargs else 90
		self.bulletType = kwargs["bulletType"] if "bulletType" in kwargs else "GenericBulletWhite"
		self.shots = list()
		if self.shotType == "ring":
			self.shots = bullets.multiCircle(self, self.ringCount, self.shotDVel, self.shotVel, self.numShots, self.bulletType)
		if self.shotType == "fanSpread":
			self.shots = bullets.fanSpread(self, self.shotAngle, self.numShots, self.shotVel, self.bulletType)


	def isOnScreen(self):
		if (self.rect[0]+self.rect[2] < self.screenRect[2] and #self right border < GameWin right border
			self.rect[0] > self.screenRect[0] and #self left border > GameWin left border
			self.rect[1]+self.rect[3] < self.screenRect[3] and #self bot border < GameWin bot border
			self.rect[1] > self.screenRect[1]): #self top border > GameWin top border
			return True
		return False

	def update(self, playerpos, bulletGroup):
		#once it moves ONTO the screen (eg, if it starts off-screen)
		#then set it so that it's moved on once. Now we can delete it
		#if it goes outside the gameborders again.
		if self.isOnScreen():
			self.onScreen = True
		self.path.update(self, **{"playerpos":playerpos,"bulletGroup":bulletGroup, "shots":self.shots})
		self.rect.center = self.pos
		self.tick += 1
		lenImg = len(self.imageList)
		self.index = self.tick/6
		if self.index>=lenImg and self.isIdle:
			self.index = lenImg-1
			self.tick = 0
		elif self.index>=lenImg:
			self.index = lenImg-3
			self.tick = lenImg*4
		self.image = self.imageList[self.index]
		if self.shotType == "random":
			rand = random.randint(0,100)
			if rand <= self.shotFreq:
				self.shoot(playerpos, bulletGroup)

	def death(self, itemGroup, power):
		if power/100 < 3:
			itemGroup.add(PowerBlock(self))
		else:
			pass
			#itemGroup.add(ScoreBlock(self))
	def shoot(self, playerpos, bulletGroup):
		dx, dy = playerpos[0]-self.rect.center[0],-1*(playerpos[1]-self.rect.center[1])
		angle = math.degrees(math.atan2(dy,dx))
		angle = angle+360 if angle<0 else angle
		radians = math.radians(angle-90)
		dx,dy = 5*math.sin(radians), 5*math.cos(radians)
		bulletGroup.add((eval("sprites."+self.bulletType+"(angle, self.rect.center)")))
		#bulletGroup.add(GenericBulletWhite(angle, self.rect.center))

class EnemyMasterFairy1(EnemyFairy1):
	def __init__(self, Touhou, pos=(100,100), pathType="Still", **kwargs):
		pygame.sprite.DirtySprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","enemy.png")).convert_alpha()
		self.index = 0
		self.tick = 0
		self.screenRect = Touhou.GameWin.gameScreenRect
		self.idle = list()
		self.left = list()
		self.right = list()
		self.isIdle = True
		self.bullets = list()
		self.bulletGroup = pygame.sprite.Group()
		self.health = 100
		self.onScreen = False
		for i in xrange(5): #arbitrary number of frames for idle
			self.idle.append(master.subsurface((i*64,32*12,64,64)))
		self.left.append(master.subsurface(320,32*12,64,64))
		for i in xrange(2):
			for j in xrange(3):
				self.left.append(master.subsurface((384+i*64,384-64*i,64,64)))
		for frame in self.left:
			self.right.append(pygame.transform.flip(frame, True, False))
		self.imageList = self.idle
		self.image = self.imageList[0]
		self.rect = self.image.get_rect()
		self.pos = pos
		self.rect.center = self.pos
		self.initFairyAttributes(pathType, **kwargs)


class Bullet(pygame.sprite.DirtySprite):
	def __init__(self, angle=0, pos=(100,100), vel=3, path=None):
		pygame.sprite.DirtySprite.__init__(self)
		self.angle = angle
		self.angle = angle
		self.vel = vel
		self.pos = pos
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama.png")).convert_alpha()
		self.image = rot_center(master.subsurface((0,64,16,16)), self.angle-90)
		self.rect = self.image.get_rect(center=self.pos)
		radians = math.radians(self.angle-90)
		self.hitbox = Hitbox((4,4))
		self.dx = self.vel*math.sin(radians)
		self.dy = self.vel*math.cos(radians)
		self.path = path
	def update(self):
		if self.path != None:
			self.path.update(self)
		else:
			radians = math.radians(self.angle-90)
			x,y = self.pos[0],self.pos[1]
			self.pos = (x-self.dx,y-self.dy)
			self.rect.center = self.pos[0],self.pos[1]
			self.hitbox.rect.center = self.rect.center

class GenericBulletWhite(pygame.sprite.DirtySprite):
	def __init__(self, angle=0, pos=(100,100), vel=3, path=None):
		pygame.sprite.DirtySprite.__init__(self)
		self.angle = angle
		self.vel = vel
		self.pos = pos
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama.png")).convert_alpha()
		self.image = rot_center(master.subsurface((0,64,16,16)), self.angle-90)
		self.rect = self.image.get_rect(center=self.pos)
		radians = math.radians(self.angle-90)
		self.hitbox = Hitbox((4,4))
		self.dx = self.vel*math.sin(radians)
		self.dy = self.vel*math.cos(radians)
		self.path = path

	def update(self):
		if self.path != None:
			self.path.update(self)
		else:
			radians = math.radians(self.angle-90)
			x,y = self.pos[0],self.pos[1]
			self.pos = (x-self.dx,y-self.dy)
			self.rect.center = self.pos[0],self.pos[1]
			self.hitbox.rect.center = self.rect.center

class ArrowBulletBlue(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3):
		Bullet.__init__(self, angle, pos, vel)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama.png")).convert_alpha()
		self.image = rot_center(master.subsurface((80,80,16,16)), self.angle-90)
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((4,4))
		self.hitbox.rect.center = self.rect.center

class CarpeBullet(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3, path=None):
		Bullet.__init__(self, angle, pos, vel, path)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","CarpeDiem.png")).convert_alpha()
		self.image = master.subsurface((0,8,70,18))
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((58,12))
		self.hitbox.rect.center = self.rect.center

class DiemBullet(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3, path=None):
		Bullet.__init__(self, angle, pos, vel, path)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","CarpeDiem.png")).convert_alpha()
		self.image = master.subsurface((70,8,58,18))
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((48,12))
		self.hitbox.rect.center = self.rect.center


class TriangleBulletRed(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3):
		Bullet.__init__(self, angle, pos, vel)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama.png")).convert_alpha()
		self.image = rot_center(master.subsurface((16,16,16,16)), self.angle-90)
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((4,4))
		self.hitbox.rect.center = self.rect.center

class TriangleBulletBlue(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3):
		Bullet.__init__(self, angle, pos, vel)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama.png")).convert_alpha()
		self.image = rot_center(master.subsurface((80,16,16,16)), self.angle-90)
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((4,4))
		self.hitbox.rect.center = self.rect.center

class SphereBulletRed(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3):
		Bullet.__init__(self, angle, pos, vel)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama4.png")).convert_alpha()
		self.image = rot_center(master.subsurface((0,0,64,64)), self.angle-90)
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((32,32))
		self.hitbox.rect.center = self.rect.center

class LargeBulletWhite(Bullet):
	def __init__(self, angle, pos=(100,100), vel=3):
		Bullet.__init__(self, angle, pos, vel)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","etama4.png")).convert_alpha()
		self.image = rot_center(master.subsurface((128,208,32,32)), self.angle-90)
		self.pos = pos
		self.rect = self.image.get_rect(center=self.pos)
		self.hitbox = Hitbox((12,12))
		self.hitbox.rect.center = self.rect.center

class PlayerBullet(pygame.sprite.DirtySprite):
	def __init__(self, angle=0, pos=(0,0)):
		pygame.sprite.DirtySprite.__init__(self)
		self.angle = angle+90
		master = pygame.image.load(os.path.join(os.path.curdir,"img","sprites","pl00.png")).convert_alpha()
		self.image = pygame.transform.rotate(master.subsurface((0,176,64,16)), self.angle)
		self.rect = self.image.get_rect(center=pos)
	def update(self):
		radians = math.radians(self.angle-90)
		x,y = self.rect[0], self.rect[1]
		dx,dy = 30*math.sin(radians), 30*math.cos(radians)
		self.rect.move_ip(-dx,-dy)

class PlayerHomingAmulet(pygame.sprite.DirtySprite):
	def __init__(self, pos=(0,0)):
		pygame.sprite.DirtySprite.__init__(self)
		self.angle = 90
		master = pygame.image.load(os.path.join(os.path.curdir,"img","sprites","pl00.png")).convert_alpha()
		self.original = rot_center(master.subsurface((16,144,16,16)), self.angle)
		self.image = self.original
		self.rect = self.image.get_rect(center=pos)


	def update(self, enemyGroup, playerpos):
		distances = list()
		dRadians = 0
		if len(enemyGroup) != 0:
			target = None
			closest = 9999
			for enemy in enemyGroup:
				edx, edy = enemy.rect[0]-playerpos[0], enemy.rect[1]-playerpos[1]
				#find closest enemy from player
				if closest>((edx**2+edy**2)**0.5):
					#save who's closest
					target = enemy
					closest = (edx**2+edy**2)**0.5
			#distance from closest enemy to bullet
			edx, edy = self.rect[0]-target.rect[0], self.rect[1]-target.rect[1]
			#get the angle between enemy and bullet
			dRadians = math.atan2(edx,edy)
		angle = math.degrees(dRadians)
		self.image = pygame.transform.rotate(self.original, angle)
		dx,dy = 13*math.sin(dRadians), 13*math.cos(dRadians)
		x,y = self.rect[0], self.rect[1]
		self.rect.move_ip(-dx,-dy)

def clearBullets(group, GameWin, isEnemy=False):
	leftBorder = GameWin.leftBorder
	rightBorder = GameWin.rightBorder
	topBorder = GameWin.topBorder
	botBorder = GameWin.botBorder
	wasEnemy = True if isEnemy else False
	for bullet in group:
		#if it's an enemy
		if isEnemy:
			#and it's on the screen, eg has moved ONTO the screen
			#from it's pre-render off-screen
			if bullet.onScreen:
				#then set this var to false to clear if it goes BACK off-screen
				isEnemy = False
		if not isEnemy:
			if (bullet.rect[1]>480 or bullet.rect[1]+bullet.rect[3]<0 or
				bullet.rect[0]>640 or bullet.rect[0]+bullet.rect[2]<0):
				if group.has(bullet):
					group.remove(bullet)

### NOT MY CODE ###
# http://www.pygame.org/wiki/RotateCenter
# No name provided to credit.
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image



