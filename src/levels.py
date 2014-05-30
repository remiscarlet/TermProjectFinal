import pygame
import random
import bullets
import paths
import math
import gui
import os
import sprites
import threading
import multiprocessing
from multiprocessing.pool import ThreadPool

class Stage1BGSprite(object):
	def __init__(self, surface, botBorder, top, pos=(0,0), vel=(0,0)):
		self.image = surface
		#position for "resetting" tree group sprites to.
		self.startPos = (pos[0],top)
		#account for offset at beginning with +top as top is negative
		self.pos = pos[0],pos[1]+top
		self.vel = vel
		self.botBorder = botBorder
		self.top = top
		self.rect = self.image.get_rect()
		self.rect.center = pos
	def resetPos(self):
		self.pos = self.startPos
	def update(self):
		self.pos = self.pos[0]+self.vel[0],self.pos[1]+self.vel[1]
		self.rect.center = self.pos

def makeTrees(self, x, y):
	surfaceList = [self.tree1Large, self.tree1Medium, self.tree1Small]
	##The y position we want all three sprites to 
	#overlap to give the visual effect of us being overhead
	targetOverlapPos = self.botBorder-50
	topPos = [0,-45,-90] #y position for bot, med, top portion of tree to start at (in order)
	velList = list()
	for pos in topPos:
		rate = (targetOverlapPos-pos)/120.0#pixels/120 ticks, px/tick
		velList.append(rate)
	return [Stage1BGSprite(surfaceList[i], 
						   self.botBorder,
						   topPos[i],
						   (x,y),
						   (0,velList[i])) for i in xrange(3)]


class Stage1Background(object):
	def __init__(self, Touhou):
		self.botBorder = Touhou.GameWin.botBorder
		master = pygame.image.load(os.path.join(os.path.curdir,"img","stagebg","stg1bg.png")).convert_alpha()
		self.bgHalf = pygame.transform.scale(pygame.transform.rotate(master.subsurface(0,0,256,256),90),(392,256))
		self.bgPrimary = self.bgHalf
		self.tree1Large = master.subsurface(257,0,128,128)
		self.tree1Medium = pygame.transform.scale(self.tree1Large, (96, 96))
		self.tree1Small = pygame.transform.scale(self.tree1Large, (64, 64))
		self.gradient = pygame.image.load(os.path.join(os.path.curdir,"img","stagebg","stg1bggradient.png")).convert_alpha()
		treePosList = [(30,-5),(160,-35),(290,-10),
						(80,140),(320,125),
						(35,285),(165,235),(285,260),
						(110,405),(320,390)]
		self.treeGroups = list()
		for pos in treePosList:
			self.treeGroups.append(makeTrees(self, pos[0]+Touhou.GameWin.leftBorder,
											   pos[1]+Touhou.GameWin.topBorder))
		bgCenter = 196+Touhou.GameWin.leftBorder #px from the left border
		topPos = -170 #px above the top border for center of third bg stack layer <- words not working.
		bgR = 126 #the "radius" of the rect that the image is in
		bgVel = (0,3.5) #Velocity at which the base background slides down



		########################################################
		###### TEMPORARILY DISABLING SLIDING BACKGROUND ########
		########################################################
		#jk


		self.bgGroup = [Stage1BGSprite(self.bgPrimary,self.botBorder, 
										  topPos, 
										  (bgCenter,bgR+256*i),
										  bgVel) for i in xrange(3)]

	def update(self):
		for group in self.treeGroups:
			for sprite in group:
				sprite.update()
			for sprite in group:
				if sprite.pos[1]>sprite.botBorder+100:
					for sprite in group:
						sprite.resetPos()
		for sprite in self.bgGroup:
			sprite.update()
			if sprite.pos[1]>sprite.botBorder+128:
				sprite.resetPos()

class StageTitle(pygame.sprite.Sprite):
	def __init__(self, Touhou):
		pygame.sprite.Sprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","stagebg","stg1txt.png")).convert_alpha()
		stageTitle = master.subsurface((0,4,256,32)).convert_alpha()
		stageNum = master.subsurface((0,48,150,32)).convert_alpha()
		stageDesc = master.subsurface((256,8,256,32)).convert_alpha()
		self.image = pygame.Surface((256,128), pygame.SRCALPHA, 32).convert_alpha()
		self.image.blit(stageNum, stageNum.get_rect(center=(75,16)))
		self.image.blit(stageTitle, stageTitle.get_rect(center=(128,48)))
		self.image.blit(stageDesc, stageDesc.get_rect(center=(128,96)))
		self.image.convert_alpha()
		self.alpha = 0
		self.image.set_alpha(self.alpha)
		self.rect = self.image.get_rect(center=(Touhou.GameWin.center[0], 150))
		self.tick = 0
	def update(self):
		self.tick+=1
		if self.tick < 127:
			self.alpha = self.alpha+2 if self.alpha+2<256 else 255
			self.image.set_alpha(self.alpha)
		if self.tick > 300:
			self.alpha = self.alpha-2 if self.alpha-2>0 else 0
			self.image.set_alpha(self.alpha)
			if self.alpha <= 0:
				self.kill()

class Stage1(object):
	def __init__(self, Touhou):
		self.gameTick = 0 #Used for level-specific timing events
		self.BG = Stage1Background(Touhou)
		self.initLevelSprites(Touhou)

	def initLevelSprites(self, Touhou):
		self.remilia = Stage1Boss(Touhou)
		self.stageTitle = StageTitle(Touhou)
		self.enemyStream1 = [(sprites.EnemyFairy1(Touhou, (460,50), "Straight", 
							**{"vel":2,"direction":"left", "eq":-0.8, "shotFreq":1}), 20) for i in xrange(10)]

		self.enemyStream2 = [(sprites.EnemyFairy1(Touhou, (50,50), "Straight", 
							**{"vel":2,"direction":"right", "eq":0.8, "shotFreq":1}), 20) for i in xrange(10)]

		self.enemyStream3 = [(sprites.EnemyFairy1(Touhou, (460,480), "Straight", 
							**{"vel":2,"direction":"left", "eq":1, "shotDuration":80,
							   "shotType":"interval", "shotInterval":8,"shotTimer":100}), 20) for i in xrange(10)]

		self.enemyStream4 = [(sprites.EnemyFairy1(Touhou, (100,480), "Straight", 
							**{"vel":2,"direction":"right", "eq":-1, "shotDuration":80,
							   "shotType":"interval", "shotInterval":8,"shotTimer":100}), 20) for i in xrange(10)]

		self.enemyStream5 = [(sprites.EnemyFairy1(Touhou, (50,50), "Straight", 
							**{"vel":1,"direction":"right", "eq":0.5, "shotTimer":100,
							   "shotType":"fanSpread", "shotAngle":120, "numShots":10,
							   "shotVel":3,"bulletType":"ArrowBulletBlue"}), 20) for i in xrange(8)]

		self.enemyStream6 = [(sprites.EnemyFairy1(Touhou, (460,50), "Straight", 
							**{"vel":1,"direction":"left", "eq":-0.5, "shotTimer":100,
							   "shotType":"fanSpread", "shotAngle":120,  "numShots":15,
							   "shotVel":3,"bulletType":"ArrowBulletBlue"}), 20) for i in xrange(8)]

		self.enemyStream7 = [(sprites.EnemyFairy1(Touhou, (460,50), "Straight", 
							**{"vel":1.5,"direction":"left", "eq":-0.5, "shotTimer":50,
							   "shotType":"fanSpread", "shotAngle":120,  "numShots":20,
							   "shotVel":2,"bulletType":"ArrowBulletBlue"}), 15) for i in xrange(8)]

		self.enemyStream8 = [(sprites.EnemyFairy1(Touhou, (50,50), "Straight", 
							**{"vel":1.5,"direction":"right", "eq":0.5, "shotTimer":50,
							   "shotType":"fanSpread", "shotAngle":120,  "numShots":20,
							   "shotVel":2,"bulletType":"ArrowBulletBlue"}), 15) for i in xrange(8)]

		self.enemyStream9 = [(sprites.EnemyFairy1(Touhou, (460,50), "Straight", 
							**{"vel":2,"direction":"left", "eq":-0.8, "shotDuration":80,
							   "shotType":"fanSpread", "shotAngle":120,"shotTimer":40,
							   "bulletType":"TriangleBulletRed", "numShots":15, "shotVel":1.6}), 20) for i in xrange(10)]

		self.enemyStream10 = [(sprites.EnemyFairy1(Touhou, (50,50), "Straight", 
							**{"vel":2,"direction":"right", "eq":0.8, "shotDuration":80,
							   "shotType":"fanSpread", "shotAngle":120,"shotTimer":40,
							   "bulletType":"TriangleBulletRed", "numShots":15, "shotVel":1.6}), 20) for i in xrange(10)]

		self.movePauseMove1 = sprites.EnemyMasterFairy1(Touhou, (10,50), "MovePauseMove",
							**{"vel":4,"direction":"right", "eq":0, "shotType":"ring",
							   "pauseTimer":120,"moveTimer":30,"shotTimer":60,
							   "ringCount":4, "shotDVel":1,"bulletType":"ArrowBulletBlue"})

		self.movePauseMove2 = sprites.EnemyMasterFairy1(Touhou, (502,50), "MovePauseMove",
							**{"vel":4,"direction":"left", "eq":0, "shotType":"ring",
							   "pauseTimer":120,"moveTimer":30,"shotTimer":60,
							   "ringCount":4, "shotDVel":1,"bulletType":"ArrowBulletBlue"})

		self.movePauseMove3 = sprites.EnemyMasterFairy1(Touhou, (402,0), "MovePauseMove",
							**{"vel":2,"direction":"left","eq":-100,"shotType":"interval",
							   "shotInterval":8,"shotTimer":50,"shotDuration":100,
							   "pauseTimer":150,"moveTimer":30})

		self.movePauseMove4 = sprites.EnemyMasterFairy1(Touhou, (110,0), "MovePauseMove",
							**{"vel":2,"direction":"right","eq":100,"shotType":"interval",
							   "shotInterval":8,"shotTimer":50,"shotDuration":100,
							   "pauseTimer":150,"moveTimer":30})

		self.MasterFairy1 = sprites.EnemyMasterFairy1(Touhou, (502,50), "MovePauseMove",
							**{"vel":2,"direction":"left","eq":0,"shotType":"interval",
							   "shotInterval":8,"shotTimer":100,"shotDuration":100,
							   "pauseTimer":150,"moveTimer":50})

		self.MasterFairy2 = sprites.EnemyMasterFairy1(Touhou, (10,50), "MovePauseMove",
							**{"vel":2,"direction":"right","eq":0,"shotType":"interval",
							   "shotInterval":8,"shotTimer":100,"shotDuration":100,
							   "pauseTimer":150,"moveTimer":50})

		self.MasterFairy3 = sprites.EnemyMasterFairy1(Touhou, (502,50), "MovePauseMove",
							**{"vel":2,"direction":"left","eq":0,"shotType":"interval",
							   "shotInterval":10,"shotTimer":100,"shotDuration":300,
							   "pauseTimer":350,"moveTimer":50, "bulletType":"TriangleBulletRed"})

		self.MasterFairy4 = sprites.EnemyMasterFairy1(Touhou, (10,50), "MovePauseMove",
							**{"vel":2,"direction":"right","eq":0,"shotType":"interval",
							   "shotInterval":10,"shotTimer":100,"shotDuration":300,
							   "pauseTimer":350,"moveTimer":50, "bulletType":"TriangleBulletRed"})

	def update(self):
		self.gameTick += 1
		self.BG.update()

	def draw(self, window,left,top):
		for sprite in self.BG.bgGroup:
			window.blit(sprite.image, sprite.rect)
		for group in self.BG.treeGroups:
			for surface in group:
				window.blit(surface.image, surface.rect)
		window.blit(self.BG.gradient,(left,top,392,456))

	def run(self, Touhou):
		if self.gameTick == 150:
			addSprites(Touhou, self.enemyStream1)
			addSprites(Touhou, self.enemyStream2)
		if self.gameTick == 200:
			addSprites(Touhou, self.movePauseMove1)
			addSprites(Touhou, self.movePauseMove2)
		if self.gameTick == 600:
			Touhou.player.add(self.stageTitle)
		if self.gameTick == 1050:
			addSprites(Touhou, self.MasterFairy1)
			addSprites(Touhou, self.MasterFairy2)
		if self.gameTick == 1100:
			addSprites(Touhou, self.enemyStream3)
			addSprites(Touhou, self.enemyStream4)
		if self.gameTick == 1250:
			addSprites(Touhou, self.enemyStream5)
			addSprites(Touhou, self.enemyStream6)
		if self.gameTick == 1400:
			addSprites(Touhou, self.movePauseMove3)
			addSprites(Touhou, self.movePauseMove4)
		if self.gameTick == 1450:
			addSprites(Touhou, self.enemyStream7)
			addSprites(Touhou, self.enemyStream8)
		if self.gameTick == 1600:
			addSprites(Touhou, self.MasterFairy3)
			addSprites(Touhou, self.MasterFairy4)
		if self.gameTick == 1650:
			addSprites(Touhou, self.enemyStream9)
			addSprites(Touhou, self.enemyStream10)
		if self.gameTick == 2300:
			Touhou.bossGroup.add(self.remilia)
			Touhou.bossGroup.add(self.remilia.healthbar)
		#if self.gameTick == 1000:
		#	self.initLevelSprites(Touhou)
		#	self.gameTick = 0

class Stage1Boss(pygame.sprite.Sprite):
	def __init__(self, Touhou):
		pygame.sprite.Sprite.__init__(self)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","remi.png")).convert_alpha()
		self.idle = master.subsurface((0,0,64,80))
		self.left = master.subsurface((64,0,64,80))
		self.right = pygame.transform.flip(self.left, False, True)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","kosbie.png")).convert_alpha()
		self.kosbie = master.subsurface((0,0,64,80))
		self.image = self.kosbie
		self.rect = self.image.get_rect()
		self.pos = (Touhou.GameWin.center[0],-10)
		self.rect.center = self.pos
		self.tick = 0
		self.initSpellCards(Touhou)
		self.bulletGroup = pygame.sprite.Group()
		self.moveDur = 0
		self.isTalking = True
		self.initDialogue()
		self.health = 3000
		self.healthbar = self.InitHealth(Touhou)
		self.switch = False

	class InitHealth(pygame.sprite.Sprite):
		def __init__(self, Touhou):
			pygame.sprite.Sprite.__init__(self)
			self.health = 3000
			self.blank = pygame.Surface((380,7), pygame.SRCALPHA, 32).convert_alpha()
			self.image = self.blank.copy()
			self.rect = self.image.get_rect(center=(Touhou.GameWin.center[0],20))
			self.bg = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","remiHealthBG.png"))
			self.bgRect = (0,0,380,7)
			self.fg = pygame.image.load(os.path.join(os.path.curdir,"img","enemy","remiHealthFG.png"))
		def update(self, Touhou):
			self.image = self.blank.copy()
			self.health = Touhou.stage1.remilia.health
			frac = self.health/3000.0
			shiftRect = (0,0,int(380*frac), 7)
			self.image.blit(self.bg,self.bgRect)
			self.image.blit(self.fg,self.bgRect, shiftRect)

	def initDialogue(self):
		kosbie1a = "Wow! I'm surprised you made it this far in 15-112!"
		kosbie1b = "...but first, put that phone away."
		reimu1a = "Damn, you're good."
		reimu1b = "Anyway, this's been too easy! Give me more!"
		kosbie2a = "Carpe Diem! That's the spirit!"
		reimu2a = "Are you going to make me dodge Carpe Diems now??"
		kosbie3a = "Oh no, no, no. You won't be fighting me at all!"
		reimu3a = "?"
		kosbie4a = "I have a guest who'll be able to"
		kosbie4b = "keep you occupied for much longer!"
		reimu4a = "!"
		kosbie5a = "You two enjoy yourselves!"
		remi1a = "WHAT AM I EVEN DOING HERE"
		dList = [kosbie1a, kosbie1b, reimu1a, reimu1b,
				 kosbie2a, reimu2a, kosbie3a, reimu3a,
				 kosbie4a, kosbie4b, reimu4a, kosbie5a,
				 remi1a]
		self.dialogueList = list()
		for dialogue in dList:
			self.dialogueList.append(dialogue)
		self.dialogueLen = len(self.dialogueList)
		self.dialogueOrder = [1,1,2,2,1,2,1,2,1,1,2,1,3]
	def initSpellCards(self, Touhou):
		class Spellcard1(object):
			def __init__(self, remilia, Touhou):
				#self, ringCount=1, dVel=5, startVel=5, numBulletsInRing=10, bulletType="GenericBulletWhite", startAngle=0
				self.LargeCircles = [bullets.multiCircle(remilia,1,1,2,12,"SphereBulletRed",6*i) for i in xrange(20)]
				self.WhiteCircles = [bullets.multiCircle(remilia,1,1,3.5,24,"LargeBulletWhite",-4*i) for i in xrange(32)]
				pass

			def update(self, this, Touhou):
				tick = this.tick
				#if tick == 1:
				#	addBullets(Touhou, self.LargeCircles)
				#	addBullets(Touhou, self.WhiteCircles)
				if tick == 900 or this.health == 2250:
					Touhou.sfx.spellClear.play()
					for bullet in Touhou.enemyBulletsGroup:
						if Touhou.reimu.power/100 < 3:
							rand = random.choice([0,1])
							point = None
							if rand == 0:
								point = sprites.PointBlock(bullet)
							else: point = sprites.PowerBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
						else:
							point = sprites.PointBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
					Touhou.enemyBulletsGroup.empty()
				if tick > 100 and this.health > 2250:
					if tick%40 == 0 and len(self.LargeCircles)>0:
						spriteList = self.LargeCircles.pop()
						for sprite in spriteList:
							sprite.pos = this.rect.center
							sprite.rect.center = sprite.pos
						Touhou.enemyBulletsGroup.add(spriteList)
					if tick%25 == 0 and len(self.WhiteCircles)>0:
						spriteList = self.WhiteCircles.pop()
						for sprite in spriteList:
							sprite.pos = this.rect.center
							sprite.rect.center = sprite.pos
						Touhou.enemyBulletsGroup.add(spriteList)
					if  tick%20 == 0 and tick < 900:
						Touhou.sfx.enemyShoot.play()
		class Spellcard2(object):
			def __init__(self, remilia, Touhou):
				self.RedBullets = [bullets.multiCircle(remilia,1,1,2,4,"TriangleBulletRed",-7*i) for i in xrange(100)]
				self.BlueBullets = [bullets.multiCircle(remilia,1,1,2,4,"TriangleBulletBlue",+5*i) for i in xrange(100)]
				self.GenericCircles = [bullets.multiCircle(remilia,1,1,1.5,20,"GenericBulletWhite",30*i) for i in xrange(40)]
			def update(self, this, Touhou):
				tick = this.tick
				if tick == 1800 or this.health == 1500:
					Touhou.sfx.spellClear.play()
					for bullet in Touhou.enemyBulletsGroup:
						if Touhou.reimu.power/100 < 3:
							rand = random.choice([0,1])
							point = None
							if rand == 0:
								point = sprites.PointBlock(bullet)
							else: point = sprites.PowerBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
						else:
							point = sprites.PointBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
					Touhou.enemyBulletsGroup.empty()
				if tick > 900:
					if tick%8==0:
						if len(self.BlueBullets)>0:
							spriteList = self.BlueBullets.pop()
							for sprite in spriteList:
								sprite.pos = this.rect.center
								sprite.rect.center = sprite.pos
							Touhou.enemyBulletsGroup.add(spriteList)
						if len(self.RedBullets)>0:
							spriteList = self.RedBullets.pop()
							for sprite in spriteList:
								sprite.pos = this.rect.center
								sprite.rect.center = sprite.pos
							Touhou.enemyBulletsGroup.add(spriteList)
					if tick%20 == 0:
						if len(self.GenericCircles)>0:
							spriteList = self.GenericCircles.pop()
							for sprite in spriteList:
								sprite.pos = this.rect.center
								sprite.rect.center = sprite.pos
							Touhou.enemyBulletsGroup.add(spriteList)
					if tick%16==0 and tick < 1700:
						Touhou.sfx.enemyShoot.play()
		class Spellcard3(object):
			def __init__(self, remilia, Touhou):
				self.LargeCircles = [bullets.multiCircle(remilia,1,1,1.5,10,"SphereBulletRed",-7*i) for i in xrange(20)]
				self.WhiteCircles = [bullets.multiCircle(remilia,1,1,3.5,16,"LargeBulletWhite",+5*i) for i in xrange(32)]
				self.RedBullets = [bullets.multiCircle(remilia,1,1,2,4,"TriangleBulletRed",-9*i) for i in xrange(100)]
				self.BlueBullets = [bullets.multiCircle(remilia,1,1,2,4,"TriangleBulletBlue",+7*i) for i in xrange(100)]
			def update(self, this, Touhou):
				tick = this.tick
				if tick == 2800 or this.health == 750:
					Touhou.sfx.spellClear.play()
					for bullet in Touhou.enemyBulletsGroup:
						if Touhou.reimu.power/100 < 3:
							rand = random.choice([0,1])
							point = None
							if rand == 0:
								point = sprites.PointBlock(bullet)
							else: point = sprites.PowerBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
						else:
							point = sprites.PointBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
					Touhou.enemyBulletsGroup.empty()
				if tick > 1800:
					if tick%8==0:
						if len(self.BlueBullets)>0:
							spriteList = self.BlueBullets.pop()
							for sprite in spriteList:
								sprite.pos = this.rect.center
								sprite.rect.center = sprite.pos
							Touhou.enemyBulletsGroup.add(spriteList)
						if len(self.RedBullets)>0:
							spriteList = self.RedBullets.pop()
							for sprite in spriteList:
								sprite.pos = this.rect.center
								sprite.rect.center = sprite.pos
							Touhou.enemyBulletsGroup.add(spriteList)
					if tick%40 == 0 and len(self.LargeCircles)>0:
						spriteList = self.LargeCircles.pop()
						for sprite in spriteList:
							sprite.pos = this.rect.center
							sprite.rect.center = sprite.pos
						Touhou.enemyBulletsGroup.add(spriteList)
					if tick%25 == 0 and len(self.WhiteCircles)>0:
						spriteList = self.WhiteCircles.pop()
						for sprite in spriteList:
							sprite.pos = this.rect.center
							sprite.rect.center = sprite.pos
						Touhou.enemyBulletsGroup.add(spriteList)
					if  tick%16 == 0 and tick < 2800:
						Touhou.sfx.enemyShoot.play()
					if tick%40==0 and tick < 2800:
						Touhou.sfx.laser.play()

		class Spellcard4(object):
			def __init__(self, remilia, Touhou):
				listOfX = [random.randint(100,400) for i in xrange(50)]
				self.CarpeBullets = [sprites.CarpeBullet(0, (listOfX[i]-70,100), 0.1, paths.Accel(0.1,0.1,3,0)) for i in xrange(50)]
				self.DiemBullets = [sprites.DiemBullet(0, (listOfX[i]+5,90), 0.1, paths.Accel(0.2,0.15,3.5,0)) for i in xrange(50)]
			def update(self, this, Touhou):
				tick = this.tick
				if tick == 3800 or this.health <= 0:
					Touhou.sfx.spellClear.play()
					for bullet in Touhou.enemyBulletsGroup:
						if Touhou.reimu.power/100 < 3:
							rand = random.choice([0,1])
							point = None
							if rand == 0:
								point = sprites.PointBlock(bullet)
							else: point = sprites.PowerBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
						else:
							point = sprites.PointBlock(bullet)
							point.autocollect = True
							Touhou.itemsGroup.add(point)
					Touhou.enemyBulletsGroup.empty()
				if tick > 2800:
					if tick%20==0:
						if len(self.CarpeBullets)>0:
							sprite = self.CarpeBullets.pop()
							Touhou.enemyBulletsGroup.add(sprite)
						if len(self.DiemBullets)>0:
							sprite = self.DiemBullets.pop()
							Touhou.enemyBulletsGroup.add(sprite)
					if tick%40==0 and tick < 3800:
						Touhou.sfx.laser.play()
				if tick >= 3800:
					Touhou.stage1.remilia.health = 0
					Touhou.stage1.remilia.healthbar.health = 0
					Touhou.collisionCalc.kill(Touhou.stage1.remilia,True)


		self.card1 = Spellcard1(self, Touhou)
		self.card2 = Spellcard2(self, Touhou)
		self.card3 = Spellcard3(self, Touhou)
		self.card4 = Spellcard4(self, Touhou)
	def update(self, Touhou):
		x,y = self.rect.center
		if not self.isTalking:
			self.tick += 1
			#Updating spellcards 
			self.card1.update(self, Touhou)
			self.card2.update(self, Touhou)
			self.card3.update(self, Touhou)
			self.card4.update(self, Touhou)
			# movement 0
			if self.tick > 100:
				if y > 100:
					y = y+1 if y+1 < 101 else 100
				if y < 100:
					y = y-1 if y-1 > 99 else 100
					self.pos = x,y
				self.rect.center = self.pos
			# movement 0.5
			if self.tick < 100:
				self.pos = x,y+1
				self.rect.center = self.pos
			# movement 1
			if self.tick > 350 and self.tick < 400:
				self.image = self.left
				self.pos = x-2,y+0.1
				self.rect.center = self.pos
			if self.tick == 300:
				self.image = self.idle
			# movement 2
			if self.tick > 850 and self.tick < 880:
				self.image = self.right
				self.pos = x+2.6,y+0.2
				self.rect.center = self.pos
			if self.tick == 580:
				self.image = self.idle
			# movement 3
			if self.tick > 1150 and self.tick < 1190:
				self.image = self.left
				self.pos = x-1.6, y+0.1
				self.rect.center = self.pos
			if self.tick == 690:
				self.image = self.idle
			# movement 4
			if self.tick > 1450 and self.tick < 1490:
				self.image = self.right
				self.pos = x+1.8, y-0.5
				self.rect.center = self.pos
			if self.tick == 890:
				self.image = self.idle
			# movement 5
			if self.tick > 1720 and self.tick < 1770:
				self.image = self.left
				self.pos = x-1.3, y+0.7
				self.rect.center = self.pos
			if self.tick == 1170:
				self.image = self.idle
			# movement 6
			if self.tick > 2050 and self.tick < 2130:
				self.image = self.right
				self.pos = x+1.4, y+0.2
				self.rect.center = self.pos
			if self.tick == 2130:
				self.image = self.idle
			# movement 7
			if self.tick > 2550 and self.tick < 2590:
				self.image = self.left
				self.pos = x-0.2, y-0.3
				self.rect.center = self.pos
			if self.tick == 2590:
				self.image = self.idle
			# movement 8
			if self.tick > 2700 and self.tick < 2870:
				self.image = self.right
				self.pos = x+0.8, y+0.1
				self.rect.center = self.pos
			if self.tick == 2870:
				self.image = self.idle
			# movement 9
			if self.tick > 3000 and self.tick < 3060:
				self.image = self.left
				self.pos = x-1.3, y+0.2
				self.rect.center = self.pos
			if self.tick == 3060:
				self.image = self.idle
			# movement 10
			if self.tick > 3300 and self.tick < 3370:
				self.image = self.right
				self.pos = x+1.3, y-0.3
				self.rect.center = self.pos
			if self.tick == 3370:
				self.image = self.idle
		if self.isTalking:
			Touhou.isTalking = True
			#If we're before the 8th dialogue box
			if Touhou.dialogueStep <8:
				#have kosbie scroll up
				y = y+2 if y+2 < 100 else 100
				self.pos = x,y
				self.rect.center = self.pos
			#If we hit the 8th or beyond
			if Touhou.dialogueStep >=8:
				#and if scrolling UP won't put us too far up
				if y-2 > -10 and not self.switch:
					#go up
					y -= 2
				#if it does go too far, 
				elif not self.switch:
					#set it at -10
					y = -10
					self.switch = True
					self.image = self.idle
				self.pos = x,y
				self.rect.center = self.pos
			if Touhou.dialogueStep >= self.dialogueLen:
				Touhou.isTalking = False
				self.isTalking = False
				self.image = self.idle
				self.pos = x,-10
				self.rect.center = self.pos
				Touhou.playMusic(Touhou.bgm.septette)





	def death(self, Touhou):
		Touhou.sfx.gameWin.play()
		Touhou.status["gameWin"] = True
		self.kill()






def addSprites(Touhou, sprites):
	def spriteAdd(Touhou, sprites):
		ticks = 0
		#sprite will be a tuple of the sprite object and the tick delay
		for sprite in sprites:
			while 1:
				Touhou.clock.tick(60)
				ticks +=1
				if sprite[1] == ticks:
					Touhou.enemyGroup.add(sprite[0])
					ticks = 0
					break
	def singleSpriteAdd(Touhou, sprite):
		Touhou.enemyGroup.add(sprite)
	#if it's not in a list, it's a single sprite. Just add it
	if type(sprites) != list:
		spriteThread = threading.Thread(target=singleSpriteAdd, args=(Touhou, sprites))
		spriteThread.start()
	#otherwise, it will be a list of tuples
	else:
		spriteThread = threading.Thread(target=spriteAdd, args=(Touhou,sprites))
		spriteThread.start()


def addBullets(Touhou, sprites):
	def spriteAdd(Touhou, sprites):
		ticks = 0
		#sprite will be a tuple of the sprite object and the tick delay
		for sprite in sprites:
			while 1:
				Touhou.clock.tick(60)
				ticks +=1
				if sprite[1] == ticks:
					Touhou.enemyBulletsGroup.add(sprite[0])
					ticks = 0
					break
	def singleSpriteAdd(Touhou, sprite):
		Touhou.enemyBulletsGroup.add(sprite)
	#if it's not in a list, it's a single sprite. Just add it
	if type(sprites) != list:
		spriteThread = threading.Thread(target=singleSpriteAdd, args=(Touhou, sprites))
		spriteThread.start()
	#otherwise, it will be a list of tuples
	else:
		spriteThread = threading.Thread(target=spriteAdd, args=(Touhou,sprites))
		spriteThread.start()


















