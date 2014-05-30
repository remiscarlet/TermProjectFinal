##################################
###### Main file for Touhou ######
##################################
import os
import pygame
import random
import gui
import sprites
import bullets
import defaultVals
import string
import sounds
import popup
import levels
import paths
try: 
	import thread
except ImportError:
	import dummy_thread as thread

#############################
###### Primary Class ######
#############################
class Touhou(object):
	############################
	###### Initialisation ######
	############################
	def __init__(self, config, win):
		self.varInit(config, win)
		self.loadingDone = False
		self.load()
		self.init(config)

	def init(self, config):
		self.GameWin = gui.Window(config)
		self.guiInit()
		self.soundInit()
		self.keyInit(config)
		self.spriteInit()
		self.fontInit()
		self.stageInit()
		self.win.unlock()
		self.loadingDone = True
		pygame.event.clear()

	class loadingAnimation(pygame.sprite.Sprite):
		def __init__(self):
			class Flake(object):
				def __init__(self, size=(16,16),pos=(10,0), vel=3):
					master = pygame.image.load(os.path.join(os.path.curdir, "img", "loading", "loading.png")).subsurface(0,64,32,32)
					self.original = pygame.transform.scale(master,size)
					self.image = self.original
					self.rect = self.image.get_rect(center=pos)
					self.r = size[0]/2
					self.vel = vel
					self.pos = pos
					self.angle = 0
				def update(self):
					self.image = sprites.rot_center(self.original,self.angle)
					self.pos = (self.pos[0],self.pos[1]+self.vel) if self.pos[1]+self.vel-self.r<64 else (self.pos[0],-self.r)
					self.rect.center = self.pos
					self.angle += 6

			self.clear = pygame.Surface((128,64), pygame.SRCALPHA, 32).convert_alpha()
			self.image = self.clear
			self.rect = self.image.get_rect(center=(550,420))
			self.flake1 = Flake((16,16),(10,0), 3)
			self.flake2 = Flake((8,8),(15,5), 2)
			self.flake3 = Flake((24,24),(80,20), 4)
			self.flake4 = Flake((16,16),(40,0), 2)
			self.flake5 = Flake((8,8),(105,30), 3)
			self.flake6 = Flake((24,24),(20,10), 1)
			self.image.blit(self.flake1.image, self.flake1.rect)
			self.image.blit(self.flake2.image, self.flake2.rect)
			self.image.blit(self.flake3.image, self.flake3.rect)
			self.image.blit(self.flake1.image, self.flake4.rect)
			self.image.blit(self.flake2.image, self.flake5.rect)
			self.image.blit(self.flake3.image, self.flake6.rect)

		def update(self):
			self.flake1.update()
			self.flake2.update()
			self.flake3.update()
			self.flake4.update()
			self.flake5.update()
			self.flake6.update()
			self.image.fill((0,0,0,0))
			self.image.blit(self.flake1.image, self.flake1.rect)
			self.image.blit(self.flake2.image, self.flake2.rect)
			self.image.blit(self.flake3.image, self.flake3.rect)
			self.image.blit(self.flake4.image, self.flake4.rect)
			self.image.blit(self.flake5.image, self.flake5.rect)
			self.image.blit(self.flake6.image, self.flake6.rect)


	def load(self, isTitle=True):
		def f(this, isTitle):
			ticks = 0
			while not this.loadingDone:
				ticks += 1
				pygame.time.Clock().tick(60)
				if ticks%2 == 0:
					this.loadingAnimation.update()
					if isTitle: this.win.blit(this.loadingScreen,this.loadingScreen.get_rect())
					else: this.win.fill((0,0,0))
					this.win.blit(this.loadingAnimation.image, this.loadingAnimation.rect)
					this.win.blit(this.loadingMessage,this.loadingMessageRect)
				pygame.transform.scale(this.win, (this.trueWidth, this.trueHeight), this.trueWin)
				pygame.display.update()
		thread.start_new_thread(f, (self,isTitle))

	def varInit(self, config, win):
		self.configInit(config)
		screenSize = config["Screen Size"].split("x")
		self.trueWidth = int(screenSize[0])
		self.trueHeight = int(screenSize[1])
		self.width,self.height = 640,480
		self.isRunning = True
		self.score = 0
		self.clock = pygame.time.Clock()
		self.ticks = 0 #Used for general events
		self.level = 1 
		self.win = pygame.Surface((640,480))
		self.trueWin = win
		self.loadingScreen = pygame.image.load(os.path.join(os.path.curdir,"img","loading","stg.png"))
		master = pygame.image.load(os.path.join(os.path.curdir,"img","loading","loading.png"))
		self.loadingMessage = master.subsurface((0,0,128,64))
		self.loadingMessageRect = self.loadingMessage.get_rect(center=(550,420))
		self.loadingAnimation = self.loadingAnimation()
		self.musicPlaying = False

	def fontInit(self):
		self.isTalking = False
		#the index of the line we're on
		self.dialogueStep = 0
		self.dialogueFont = pygame.font.Font(os.path.join(os.path.curdir,'fonts','LTYPE.TTF'), 16)
		self.nameFont = pygame.font.Font(os.path.join(os.path.curdir,'fonts','LTYPE.TTF'), 8)
		self.dialogueBox = pygame.Surface((392,100))
		self.dialogueBoxRect = self.dialogueBox.get_rect(center=(self.GameWin.center[0],418))

	def configInit(self, config):
		self.config = config
		#Set the vols of sfx and bgm to float from 0 to 1
		self.config["SFX"] = int(self.config["SFX"])/100.0
		self.config["BGM"] = int(self.config["BGM"])/100.0

	def guiInit(self):
		self.titleBG = pygame.image.load(
					   os.path.join(os.path.curdir,"img","gui","select00.png")).convert_alpha()
		self.titleBGRect = self.titleBG.get_rect()
		self.status = {"menu":True, "options":False, "paused":False, "instructions":False,
					   "editor":False, "playing":False, "gameOver":False, "gameWin":False}
		#####
		buttonImages = ["Start", "Instructions", "Options", "Options", "Quit"]
		pos = [(self.width/2, self.height*0.25+y*self.height/10) 
				for y in xrange(5)]
		self.menuButtons = [gui.Button("menu",buttonImages[i],pos[i])
				for i in xrange(5)]
		self.menuButtons[0].highlighted = True
		self.menuGroup = pygame.sprite.Group(self.menuButtons)
		#####
		pos[0] = pos[0][0]-50, pos[0][1]
		pos[1] = pos[1][0]-50, pos[1][1]
		optionImages = ["BGM", "SFX", "Window", "KeyConfig", "Back"]
		self.optionButtons = [gui.Button("options",optionImages[i],pos[i])
				for i in xrange(5)]
		self.optionButtons[0].highlighted = True
		self.optionGroup = pygame.sprite.Group(self.optionButtons)
		self.volumeBarBG = pygame.image.load(os.path.join(os.path.curdir,"img","options","VolumeBarBG.png"))
		self.volumeBarBGRect = self.volumeBarBG.get_rect(center=(pos[0][0]+105,pos[0][1]))
		self.volumeBarFG = pygame.image.load(os.path.join(os.path.curdir,"img","options","VolumeBarFG.png"))
		self.volumeBarFGRect = self.volumeBarFG.get_rect(center=(pos[0][0]+105,pos[0][1]))

		######
		self.PauseMenu = gui.PauseMenu(self)
		self.GameOverMenu = gui.GameOverMenu(self)
		self.GameWinMenu = gui.GameWinMenu(self)
		self.instructions = [pygame.image.load(os.path.join(os.path.curdir,"img","gui","instructions.png")),
							 pygame.image.load(os.path.join(os.path.curdir,"img","gui","instructions2.png"))]
		self.whichInstruction = 0
		self.instructionsRect = self.instructions[0].get_rect()

	def soundInit(self):
		self.bgm = sounds.BGM()
		self.sfx = sounds.SFX()
		self.sfx.setVolume(self.config["SFX"])

	def stageInit(self):
		self.stage1 = levels.Stage1(self)

	def keyInit(self, config):
		try:
			self.leftKey = int(eval("pygame."+config["Left"]))
			self.rightKey = int(eval("pygame."+config["Right"]))
			self.upKey = int(eval("pygame."+config["Up"]))
			self.downKey = int(eval("pygame."+config["Down"]))
			self.shootKey = int(eval("pygame."+config["Shoot"]))
			self.bombKey = int(eval("pygame."+config["Bomb"]))
			self.focusKey = int(eval("pygame."+config["Focus"]))
		except:
			config = remakeConfig()
			self.leftKey = int(eval("pygame."+config["Left"]))
			self.rightKey = int(eval("pygame."+config["Right"]))
			self.upKey = int(eval("pygame."+config["Up"]))
			self.downKey = int(eval("pygame."+config["Down"]))
			self.shootKey = int(eval("pygame."+config["Shoot"]))
			self.bombKey = int(eval("pygame."+config["Bomb"]))
			self.focusKey = int(eval("pygame."+config["Focus"]))
		pygame.key.set_repeat(250, 50)

	def spriteInit(self):
		####### Sprite Groups #######
		self.enemyGroup = pygame.sprite.Group()
		self.playerBulletsGroup = pygame.sprite.Group()
		self.enemyBulletsGroup = pygame.sprite.Group()
		self.playerHomingAmuletGroup = pygame.sprite.Group()
		self.itemsGroup = pygame.sprite.Group()
		self.bossGroup = pygame.sprite.Group()
		####### Sprites #######
		self.reimu = sprites.Reimu(self.config, self.GameWin.center[0], self.height-50)
		self.reimu.rect.center = (self.GameWin.center[0],self.height-50)
		self.reimu.hitbox.rect.center = self.reimu.rect.center
		self.player = pygame.sprite.LayeredUpdates()
		self.player.add(self.reimu)
		self.player.add(self.reimu.hitbox)

	#############################
	###### Events Handling ######
	#############################

	def events(self):
		keys = pygame.key.get_pressed()
		#Because the gameplay requires constant stream of keypress
		#information, continuously send anyway.
		if self.status["playing"]: self.playingUpdate(keys)
		#for all other events
		for event in pygame.event.get():
			#quit when x button is pressed
			if event.type == pygame.QUIT: self.isRunning = False
			#check that the event has attr of key to prevent crashes
			if hasattr(event, 'key'):
				if event.key == pygame.K_q: self.status["gameWin"] = True
				if event.type == pygame.KEYDOWN:
					if event.key == self.upKey:
						if self.status["menu"]: self.menuUpdate("UP")
						elif self.status["options"]: self.optionsUpdate("UP")
						elif self.status["paused"]: self.pausedUpdate("UP")
						elif self.status["gameOver"]: self.gameOverUpdate("UP")
						elif self.status["gameWin"]: self.gameWinUpdate("UP")
					if event.key == self.downKey:
						if self.status["menu"]: self.menuUpdate("DOWN")
						elif self.status["options"]: self.optionsUpdate("DOWN")
						elif self.status["paused"]: self.pausedUpdate("DOWN")
						elif self.status["gameOver"]: self.gameOverUpdate("DOWN")
						elif self.status["gameWin"]: self.gameWinUpdate("DOWN")
					if event.key == self.leftKey:
						if self.status["options"]: self.optionsUpdate("LEFT")
					if event.key == self.rightKey:
						if self.status["options"]: self.optionsUpdate("RIGHT")
					if event.key == self.shootKey:
						if self.status["menu"]: self.menuUpdate("ENTER")
						elif self.status["options"]:self.optionsUpdate("ENTER")
						elif self.status["paused"]: self.pausedUpdate("ENTER")
						elif self.status["gameOver"]: self.gameOverUpdate("ENTER")
						elif self.status["gameWin"]: self.gameWinUpdate("ENTER")
						elif self.status["instructions"]: self.instructionsUpdate("ENTER")
						if self.isTalking: self.dialogueStep += 1
					if event.key == pygame.K_ESCAPE:
						if self.status["playing"] or self.status["paused"]:
							self.sfx.pause.play()
							self.status["playing"] = not self.status["playing"]
							self.status["paused"] = not self.status["paused"]
						if self.status["instructions"]:
							self.instructionsUpdate("ESCAPE")

					if event.key == pygame.K_f:
						if self.status["playing"]:
							randX = random.randint(self.GameWin.leftBorder, 
												   self.GameWin.rightBorder)
							randY = random.randint(self.GameWin.topBorder,
												   self.GameWin.botBorder-150)
							vel = random.randint(1,3)
							direction = random.choice(["right","left"])
							eq = random.randint(0,300)/100.0
							self.enemyGroup.add(sprites.EnemyFairy1(self, (randX,randY), "Straight", 
																    **{"vel":vel, "direction":direction, "eq":eq}))
	def menuUpdate(self, key):
		if self.status["menu"] == True:
			if key == "UP":
				for i in xrange(len(self.menuButtons)):
					if self.menuButtons[i].highlighted == True:
						#we do know that the current 
						#index is highlighted, so set to false
						self.menuButtons[i].highlighted = False
						#and because we want to go up, 
						#set the previous index to highlighted
						self.menuButtons[i-1].highlighted = True
						self.sfx.ok.play()
						break

			if key == "DOWN":
				for i in xrange(len(self.menuButtons)):
					if self.menuButtons[i].highlighted == True:
						self.menuButtons[i].highlighted = False
						#mod cuz we don't want to go out of index.
						(self.menuButtons[(i+1)%len(self.menuButtons)].highlighted) = True
						self.sfx.ok.play()
						break

			if key == "ENTER":
				for i in xrange(len(self.menuButtons)):
					if self.menuButtons[i].highlighted == True:
						self.status["menu"] = False
						if i == 0:
							self.status["playing"] = True
							self.resetMenuButtons()
							self.musicPlaying = False
							self.level = 1
							self.sfx.ok.play()
						if i == 1:
							self.status["instructions"] = True
							self.resetMenuButtons()
							self.sfx.ok.play()
						if i == 2:
							self.status["options"] = True
							self.resetMenuButtons()
							self.sfx.ok.play()
						if i == 3:
							self.status["options"] = True
							self.resetMenuButtons()
							self.sfx.ok.play()
						if i == 4:
							self.isRunning = False
							self.sfx.ok.play()
						break

	def resetMenuButtons(self):
		#set it to default position
		for button in self.menuButtons:
			button.highlighted = False
		self.menuButtons[0].highlighted = True

	def instructionsUpdate(self, key):
		if self.status["instructions"] == True:
			if key == "ESCAPE":
				self.sfx.ok.play()
				self.status["instructions"] = False
				self.status["menu"] = True
			if key == "ENTER":
				self.whichInstruction = (self.whichInstruction+1)%2
				self.sfx.ok.play()

	def optionsUpdate(self, key):
		if self.status["options"] == True:
			if key == "UP":
				for i in xrange(len(self.optionButtons)):
					if self.optionButtons[i].highlighted == True:
						#we do know that the current 
						#index is highlighted, so set to false
						self.optionButtons[i].highlighted = False
						#and because we want to go up, 
						#set the previous index to highlighted
						self.optionButtons[i-1].highlighted = True
						self.sfx.ok.play()
						break
			if key == "LEFT":
				for i in xrange(len(self.optionButtons)):
					if self.optionButtons[i].highlighted == True:
						if i == 0:
							self.config["BGM"] = self.config["BGM"]-0.05 if self.config["BGM"]>0 else 0.0
							pygame.mixer.music.set_volume(self.config["BGM"])
							break
						if i == 1:
							self.config["SFX"] = self.config["SFX"]-0.05 if self.config["SFX"]>0 else 0.0
							self.sfx.setVolume(self.config["SFX"])
							break
			if key == "RIGHT":
				for i in xrange(len(self.optionButtons)):
					if self.optionButtons[i].highlighted == True:
						if i == 0:
							self.config["BGM"] = self.config["BGM"]+0.05 if self.config["BGM"]<1 else 1.0
							pygame.mixer.music.set_volume(self.config["BGM"])
							break
						if i == 1:
							self.config["SFX"] = self.config["SFX"]+0.05 if self.config["SFX"]<1 else 1.0
							self.sfx.setVolume(self.config["SFX"])
							break
			if key == "DOWN":
				for i in xrange(len(self.optionButtons)):
					if self.optionButtons[i].highlighted == True:
						self.optionButtons[i].highlighted = False
						#mod cuz we don't want to go out of index.
						self.optionButtons[(i+1)%len(self.optionButtons)].highlighted = True
						self.sfx.ok.play()
						break

			if key == "ENTER":
				for i in xrange(len(self.optionButtons)):
					if self.optionButtons[i].highlighted == True:
						if i == 0:
							self.status["options"] = True
						if i == 1:
							self.status["options"] = True
						if i == 2:
							self.status["options"] = True
						if i == 3:
							self.status["options"] = True
						if i == 4:
							self.status["options"] = False
							self.status["menu"] = True
							modifyConfigVals("BGM",int(self.config["BGM"]*100))
							modifyConfigVals("SFX",int(self.config["SFX"]*100))
							self.resetOptionButtons()
							self.sfx.ok.play()
						break

	def resetOptionButtons(self):
		#Set it to default positions
		for button in self.optionButtons:
			button.highlighted = False
		self.optionButtons[0].highlighted = True

	def pausedUpdate(self, key):
		if self.status["paused"] == True:
			if key == "UP":
				for i in xrange(len(self.PauseMenu.initOrder)):
					key = self.PauseMenu.initOrder[i]
					keyPrev = self.PauseMenu.initOrder[i-1]
					if self.PauseMenu.whichHighlighted[key] == True:
						#we do know that the current 
						#index is highlighted, so set to false
						self.PauseMenu.whichHighlighted[key] = False
						#and because we want to go up, 
						#set the previous index to highlighted
						self.PauseMenu.whichHighlighted[keyPrev] = True
						self.sfx.ok.play()
						break

			if key == "DOWN":
				for i in xrange(len(self.PauseMenu.initOrder)):
					key = self.PauseMenu.initOrder[i]
					#mod cuz we don't want to go out of index.
					keyNext = self.PauseMenu.initOrder[(i+1)%len(self.PauseMenu.whichHighlighted)]
					if self.PauseMenu.whichHighlighted[key] == True:
						self.PauseMenu.whichHighlighted[key] = False
						self.PauseMenu.whichHighlighted[keyNext] = True
						self.sfx.ok.play()
						break

			if key == "ENTER":
				for i in xrange(len(self.PauseMenu.initOrder)):
					key = self.PauseMenu.initOrder[i]
					if self.PauseMenu.whichHighlighted[key] == True:
						if i == 0:
							self.status["paused"] = False
							self.status["playing"] = True
							self.sfx.ok.play()
						if i == 1:
							self.loadingDone = False
							self.load(False)
							self.init(self.config)
							self.loadingDone = True
							pygame.event.clear()
							self.status["gameOver"] = False
							self.status["menu"] = False
							self.status["playing"] = True
						if i == 2:
							self.status["paused"] = False
							self.status["menu"] = True
							self.sfx.ok.play()
							self.score = 0
							self.reimu.lives = 3
							self.win.fill((0,0,0))
							self.win.blit(self.loadingMessage, self.loadingMessageRect)
							pygame.display.update()
							self.loadingDone = False
							self.load(False)
							self.init(self.config)
							self.loadingDone = True
							pygame.event.clear()
							pygame.mixer.music.stop()
							self.musicPlaying = False
						break
	def gameOverUpdate(self, key):
		if self.status["gameOver"] == True:
			if key == "UP":
				for i in xrange(len(self.GameOverMenu.initOrder)):
					key = self.GameOverMenu.initOrder[i]
					keyPrev = self.GameOverMenu.initOrder[i-1]
					if self.GameOverMenu.whichHighlighted[key] == True:
						#we do know that the current 
						#index is highlighted, so set to false
						self.GameOverMenu.whichHighlighted[key] = False
						#and because we want to go up, 
						#set the previous index to highlighted
						self.GameOverMenu.whichHighlighted[keyPrev] = True
						self.sfx.ok.play()
						break

			if key == "DOWN":
				for i in xrange(len(self.GameOverMenu.initOrder)):
					key = self.GameOverMenu.initOrder[i]
					#mod cuz we don't want to go out of index.
					keyNext = self.GameOverMenu.initOrder[(i+1)%len(self.GameOverMenu.whichHighlighted)]
					if self.GameOverMenu.whichHighlighted[key] == True:
						self.GameOverMenu.whichHighlighted[key] = False
						self.GameOverMenu.whichHighlighted[keyNext] = True
						self.sfx.ok.play()
						break

			if key == "ENTER":
				for i in xrange(len(self.GameOverMenu.initOrder)):
					key = self.GameOverMenu.initOrder[i]
					if self.GameOverMenu.whichHighlighted[key] == True:
						if i == 0:
							self.status["gameOver"] = False
							self.status["playing"] = True
							self.score = 0
							self.reimu.lives = 3
							self.playMusic(self.bgm.stage1theme)
							self.sfx.ok.play()
						if i == 1:
							self.loadingDone = False
							self.load(False)
							self.init(self.config)
							self.loadingDone = True
							pygame.event.clear()
							self.status["gameOver"] = False
							self.status["menu"] = False
							self.status["playing"] = True
						if i == 2:
							self.status["gameOver"] = False
							self.status["menu"] = True
							self.sfx.ok.play()
							self.score = 0
							self.reimu.lives = 3
							self.win.fill((0,0,0))
							self.win.blit(self.loadingMessage, self.loadingMessageRect)
							pygame.display.update()
							self.loadingDone = False
							self.load(False)
							self.init(self.config)
							self.loadingDone = True
							pygame.event.clear()
							pygame.mixer.music.stop()
							self.musicPlaying = False
						break
	def gameWinUpdate(self, key):
		if self.status["gameWin"] == True:
			if key == "UP":
				for i in xrange(len(self.GameWinMenu.initOrder)):
					key = self.GameWinMenu.initOrder[i]
					keyPrev = self.GameWinMenu.initOrder[i-1]
					if self.GameWinMenu.whichHighlighted[key] == True:
						#we do know that the current 
						#index is highlighted, so set to false
						self.GameWinMenu.whichHighlighted[key] = False
						#and because we want to go up, 
						#set the previous index to highlighted
						self.GameWinMenu.whichHighlighted[keyPrev] = True
						self.sfx.ok.play()
						break

			if key == "DOWN":
				for i in xrange(len(self.GameWinMenu.initOrder)):
					key = self.GameWinMenu.initOrder[i]
					#mod cuz we don't want to go out of index.
					keyNext = self.GameWinMenu.initOrder[(i+1)%len(self.GameWinMenu.whichHighlighted)]
					if self.GameWinMenu.whichHighlighted[key] == True:
						self.GameWinMenu.whichHighlighted[key] = False
						self.GameWinMenu.whichHighlighted[keyNext] = True
						self.sfx.ok.play()
						break

			if key == "ENTER":
				for i in xrange(len(self.GameWinMenu.initOrder)):
					key = self.GameWinMenu.initOrder[i]
					if self.GameWinMenu.whichHighlighted[key] == True:
						if i == 0:
							self.loadingDone = False
							self.load(False)
							self.init(self.config)
							self.loadingDone = True
							pygame.event.clear()
							self.status["gameOver"] = False
							self.status["menu"] = False
							self.status["playing"] = True
						if i == 1:
							self.status["gameOver"] = False
							self.status["menu"] = True
							self.sfx.ok.play()
							self.score = 0
							self.reimu.lives = 3
							self.win.fill((0,0,0))
							self.win.blit(self.loadingMessage, self.loadingMessageRect)
							pygame.display.update()
							self.loadingDone = False
							self.load(False)
							self.init(self.config)
							self.loadingDone = True
							pygame.event.clear()
							pygame.mixer.music.stop()
							self.musicPlaying = False
						break

	def playingUpdate(self, keys):
		(x,y) = (self.reimu.rect.center[0], self.reimu.rect.center[1])
		up = keys[self.upKey]
		down = keys[self.downKey]
		left = keys[self.leftKey]
		right = keys[self.rightKey]
		shoot = keys[self.shootKey]
		focus = keys[self.focusKey]
		if focus: self.reimu.isFocused = True
		else:  self.reimu.isFocused = False
		if (self.status["playing"] == True and self.reimu.lives >= 0 and 
			self.status["paused"] == False and self.status["gameWin"] == False):
			if not self.isTalking: self.score += 5
			moveVel = 6 if not focus else 3
			if down and left:
				#Have to check if on screen on every call 
				#because we still want the sprite
				#animation to be going even when running into the wall
				self.changeSpriteDir(self.reimu, "left")
				newLoc = (x-moveVel,y+moveVel)
				newLocDownLeft = (x-moveVel,y+moveVel)
				newLocDown = (x,y+moveVel)
				newLocLeft = (x-moveVel,y)
				#incase we're on the edge, but we want to along the border
				#eg, at left border but pressing downleft, we should still
				#slide leftwards.
				if self.reimu.isOnScreen(newLocDownLeft, self.GameWin):
					self.reimu.rect.center = newLocDownLeft
				elif self.reimu.isOnScreen(newLocLeft, self.GameWin):
					self.reimu.rect.center = newLocLeft
				elif self.reimu.isOnScreen(newLocDown, self.GameWin):
					self.reimu.rect.center = newLocDown	
			elif down and right:
				self.changeSpriteDir(self.reimu, "right")
				newLocDownRight = (x+moveVel,y+moveVel)
				newLocDown = (x,y+moveVel)
				newLocRight = (x+moveVel,y)
				if self.reimu.isOnScreen(newLocDownRight, self.GameWin):
					self.reimu.rect.center = newLocDownRight
				elif self.reimu.isOnScreen(newLocRight, self.GameWin):
					self.reimu.rect.center = newLocRight
				elif self.reimu.isOnScreen(newLocDown, self.GameWin):
					self.reimu.rect.center = newLocDown	
			elif up and left:
				self.changeSpriteDir(self.reimu, "left")
				newLocUpLeft = (x-moveVel,y-moveVel)
				newLocUp = (x,y-moveVel)
				newLocLeft = (x-moveVel,y)
				if self.reimu.isOnScreen(newLocUpLeft, self.GameWin):
					self.reimu.rect.center = newLocUpLeft
				elif self.reimu.isOnScreen(newLocLeft, self.GameWin):
					self.reimu.rect.center = newLocLeft
				elif self.reimu.isOnScreen(newLocUp, self.GameWin):
					self.reimu.rect.center = newLocUp
			elif up and right:
				self.changeSpriteDir(self.reimu, "right")
				newLocUpRight = (x+moveVel,y-moveVel)
				newLocUp = (x,y-moveVel)
				newLocRight = (x+moveVel,y)
				if self.reimu.isOnScreen(newLocUpRight, self.GameWin):
					self.reimu.rect.center = newLocUpRight
				elif self.reimu.isOnScreen(newLocRight, self.GameWin):
					self.reimu.rect.center = newLocRight
				elif self.reimu.isOnScreen(newLocUp, self.GameWin):
					self.reimu.rect.center = newLocUp

			elif left:
				self.changeSpriteDir(self.reimu, "left")
				newLoc = (x-moveVel,y)
				if self.reimu.isOnScreen(newLoc, self.GameWin):
					self.reimu.rect.center = newLoc
			elif right:
				self.changeSpriteDir(self.reimu, "right")
				newLoc = (x+moveVel,y)
				if self.reimu.isOnScreen(newLoc, self.GameWin):
					self.reimu.rect.center = newLoc
			elif up:
				self.changeSpriteDir(self.reimu, "idle")
				newLoc = (x,y-moveVel)
				if self.reimu.isOnScreen(newLoc, self.GameWin):
					self.reimu.rect.center = newLoc
			elif down:
				self.changeSpriteDir(self.reimu, "idle")
				newLoc = (x,y+moveVel)
				if self.reimu.isOnScreen(newLoc, self.GameWin):
					self.reimu.rect.center = newLoc
			else: self.changeSpriteDir(self.reimu, "idle")
			if shoot and not self.isTalking:
				(x,y) = self.reimu.rect.center
				if self.ticks%8 == 0:
					self.sfx.shoot.play()
					self.reimu.shoot(self.playerBulletsGroup,
									 self.playerHomingAmuletGroup, self.ticks)
			########### Collision checking
			# Regular player bullets
			for bullet in self.playerBulletsGroup:
				collided = pygame.sprite.spritecollide(bullet, 
													   self.enemyGroup, False, collisionCheck) 
				if collided != []:
					self.collisionCalc(bullet, collided)
				collided = pygame.sprite.spritecollide(bullet, 
													   self.bossGroup, False, collisionCheck) 
				if collided != []:
					self.collisionCalc(bullet, collided)

			# Player homing amulets
			for bullet in self.playerHomingAmuletGroup:
				collided = pygame.sprite.spritecollide(bullet,
													   self.enemyGroup, False, collisionCheck) 
				if collided != []:
					self.collisionCalc(bullet, collided)
				collided = pygame.sprite.spritecollide(bullet,
													   self.bossGroup, False, collisionCheck) 
				if collided != []:
					self.collisionCalc(bullet, collided)

			# Item drops
			for item in self.itemsGroup:
				collided = pygame.sprite.spritecollide(item, 
													   self.player, False, collisionCheck) 
				if collided != []:
					self.collisionCalc(item, collided)

			# Player hitbox
			collided = pygame.sprite.spritecollide(self.reimu.hitbox, 
												  self.enemyBulletsGroup, False, collisionCheck) 
			if collided != []:
				self.collisionCalc(self.reimu.hitbox, collided)
			########### Calling update method on everything ##########
			self.enemyGroup.update((self.reimu.rect.center[0],
									self.reimu.rect.center[1]),
									self.enemyBulletsGroup)
			self.playerBulletsGroup.update()
			self.playerHomingAmuletGroup.update(self.enemyGroup,
												self.reimu.rect.center)
			self.playerHomingAmuletGroup.update(self.bossGroup,
												self.reimu.rect.center)
			self.player.update()
			self.enemyBulletsGroup.update()
			self.itemsGroup.update(self.reimu.hitbox.rect.center)
			self.bossGroup.update(self)
			########### Removing bullets #########
			sprites.clearBullets(self.playerBulletsGroup, self.GameWin)
			sprites.clearBullets(self.playerHomingAmuletGroup, self.GameWin)
			sprites.clearBullets(self.enemyBulletsGroup, self.GameWin)
			#I should probably rename clearBullets to clearSprites
			#Since we're using it for items and enemies too now...
			sprites.clearBullets(self.itemsGroup, self.GameWin)
			sprites.clearBullets(self.enemyGroup, self.GameWin, True)
			############ Check if player above auto-collect line ##########
			x,y = self.reimu.hitbox.rect.center
			if y <= 100 and y > self.GameWin.topBorder:
				self.allItemsCollect()

			###### Stage running ######
			if self.level == 1: 
				self.stage1.update()
				self.stage1.run(self)
				pass
			if self.level == 2: pass
			if self.level == 3: pass
			if self.level == 4: pass
			if self.level == 5: pass

	def allItemsCollect(self): 
		for item in self.itemsGroup:
			item.autocollect = True

	def collisionCalc(self, sprite, listOfCollided):
		def kill(enemy, isBoss):
			if hasattr(enemy, "death"):
				if not isBoss: enemy.death(self.itemsGroup, self.reimu.power)
				if isBoss: enemy.death(self)
				self.enemyGroup.remove(enemy)
				self.score+=250 if not isBoss else 50000
				self.sfx.kill.play()

		def selfDeath():
			self.reimu.power = 0
			self.sfx.death.play()
			self.reimu.death(self.itemsGroup, self.reimu.power)

		for enemy in listOfCollided:
			isBoss = isinstance(enemy, levels.Stage1Boss)
			if isinstance(sprite, sprites.PlayerHomingAmulet):
				self.playerHomingAmuletGroup.remove(sprite)
				enemy.health -= 2
				if enemy.health <= 0:
					kill(enemy, isBoss)
				else:
					if not isBoss: self.sfx.damage.play()
			if isinstance(sprite, sprites.PlayerBullet):
				self.playerBulletsGroup.remove(sprite)
				enemy.health -= 10
				if enemy.health <= 0:
					kill(enemy, isBoss)
				else:
					if random.randint(0,5) == 0: self.sfx.damage.play()
			if isinstance(sprite, sprites.PowerBlock):
				self.itemsGroup.remove(sprite)
				power = self.reimu.power
				self.reimu.power = power+2 if power+2<400 else 400
				self.score += 100
			if isinstance(sprite, sprites.PointBlock):
				self.itemsGroup.remove(sprite)
				self.sfx.itemGet.play()
				self.score += 300
			if isinstance(sprite, sprites.Hitbox):
				if self.reimu.isDead == False:
					self.enemyBulletsGroup.remove(enemy)
					selfDeath()
					if self.reimu.lives < 0:
						self.status["gameOver"] = True
						self.musicPlaying = False
						self.sfx.gameOver.play()



	def changeSpriteDir(self, sprite, direc):
		if direc == "left":
			sprite.imageList = sprite.left
			sprite.isIdle = False
		if direc == "right": 
			sprite.imageList = sprite.right
			sprite.isIdle = False
		if direc == "idle": 
			sprite.imageList = sprite.idle
			sprite.isIdle = True

	#########################
	###### GUI Drawing ######
	#########################

	def drawMenu(self):
		if self.status["menu"] == True:
			self.win.unlock()
			self.win.blit(self.titleBG, self.titleBGRect)
			if not self.musicPlaying:
				self.playMusic(self.bgm.title)
				self.musicPlaying = True
			self.win.unlock()
			self.menuGroup.update()
			self.menuGroup.draw(self.win)

	def playMusic(self, track):
		if pygame.mixer.music.get_busy():
			pygame.mixer.music.fadeout(1000)
		pygame.mixer.music.load(track)
		pygame.mixer.music.set_volume(self.config["BGM"])
		pygame.mixer.music.play(-1)

	def drawPlaying(self):
		if self.status["playing"] or self.status["paused"] or self.status["gameOver"]:
			if not self.musicPlaying and not self.status["paused"] and not self.status["gameOver"]:
				self.playMusic(self.bgm.stage1theme)
				self.musicPlaying = True
			if self.status["paused"]: pygame.mixer.music.pause()
			if self.status["playing"]: pygame.mixer.music.unpause()
			###### Stage drawing ######
			left,top = self.GameWin.leftBorder,self.GameWin.topBorder
			if self.level == 1: self.stage1.draw(self.win,left,top)
			if self.level == 2: pass
			if self.level == 3: pass
			if self.level == 4: pass
			if self.level == 5: pass
			########### drawing ############
			self.enemyGroup.draw(self.win)
			self.bossGroup.draw(self.win)
			self.playerBulletsGroup.draw(self.win)
			self.playerHomingAmuletGroup.draw(self.win)
			#self.player.draw(self.win)
			for sprite in self.player:
				if isinstance(sprite, levels.StageTitle):
					blit_alpha(self.win, sprite.image, sprite.rect, sprite.alpha)
				else:
					self.win.blit(sprite.image, sprite.rect)
			self.enemyBulletsGroup.draw(self.win)
			self.itemsGroup.draw(self.win)
			for enemy in self.enemyGroup:
				enemy.bulletGroup.draw(self.win)
			self.GameWin.drawScreen(self)
		if self.status["paused"]:
			self.win.blit(self.PauseMenu.gradient,self.PauseMenu.gradientRect)
			if self.PauseMenu.initial:
				for key in self.PauseMenu.initOrder:
					if self.PauseMenu.whichHighlighted[key]:
						self.win.blit(self.PauseMenu.highlighted[key],
									  self.PauseMenu.highlightedRects[key])
					else:
						self.win.blit(self.PauseMenu.unhighlighted[key],
									  self.PauseMenu.unhighlightedRects[key])
		if self.status["gameOver"]:
			if not self.musicPlaying:
				self.playMusic(self.bgm.gameOver)
				self.musicPlaying = True
			self.win.blit(self.GameOverMenu.gradient,self.GameOverMenu.gradientRect)
			if self.GameOverMenu.initial:
				for key in self.GameOverMenu.initOrder:
					if self.GameOverMenu.whichHighlighted[key]:
						self.win.blit(self.GameOverMenu.highlighted[key],
									  self.GameOverMenu.highlightedRects[key])
					else:
						self.win.blit(self.GameOverMenu.unhighlighted[key],
									  self.GameOverMenu.unhighlightedRects[key])
		if self.status["gameWin"]:
			if self.musicPlaying:
				pygame.mixer.music.fadeout(1000)
				self.musicPlaying = False
			self.win.blit(self.GameWinMenu.gradient,self.GameWinMenu.gradientRect)
			self.win.blit(self.GameWinMenu.winMessage,self.GameWinMenu.winMessageRect)
			for key in self.GameWinMenu.initOrder:
					if self.GameWinMenu.whichHighlighted[key]:
						self.win.blit(self.GameWinMenu.highlighted[key],
									  self.GameWinMenu.highlightedRects[key])
					else:
						self.win.blit(self.GameWinMenu.unhighlighted[key],
									  self.GameWinMenu.unhighlightedRects[key])
		if self.isTalking:
			#dialogueFont nameFont
			if self.dialogueStep/self.stage1.remilia.dialogueLen == 0:
				index = self.dialogueStep%self.stage1.remilia.dialogueLen
				dList = self.stage1.remilia.dialogueList
				white = (255,255,255)
				black = (0,0,0)
				size = self.dialogueFont.size(dList[index])
				dialogueBox = self.dialogueBox.copy()
				if size[0]>350:
					dialogue = dList[index]
					split = dialogue.split()
					half = len(split)/2
					firstHalf = string.join(split[:half])
					secondHalf = string.join(split[half:])
					dText1 = self.dialogueFont.render(firstHalf, True, white)
					dText2 = self.dialogueFont.render(secondHalf, True, white)
					dialogueBox.blit(dText1, (40,37))
					dialogueBox.blit(dText2, (40,53))
				if size[0]<=350:
					dialogueText = self.dialogueFont.render(dList[index], True, white)
					dialogueBox.blit(dialogueText, (50,50))
				blit_alpha(self.win,dialogueBox, self.dialogueBoxRect.topleft, 200)


					

	def drawEditor(self):
		if self.status["editor"] == True:
			pass

	def drawOptions(self):
		if self.status["options"] == True:
			self.win.blit(self.titleBG, self.titleBGRect)
			rect = self.volumeBarBGRect
			SFXRect = (0,0,rect[2]*self.config["SFX"],rect[3])
			BGMRect = (0,0,rect[2]*self.config["BGM"],rect[3])
			self.win.blit(self.volumeBarBG, self.volumeBarBGRect)
			self.win.blit(self.volumeBarFG, self.volumeBarFGRect, BGMRect)
			shiftedRect = (rect[0],rect[1]+48,rect[2],rect[3])
			self.win.blit(self.volumeBarBG, shiftedRect)
			self.win.blit(self.volumeBarFG, shiftedRect, SFXRect)
			self.optionGroup.update()
			self.optionGroup.draw(self.win)

	def drawInstructions(self):
		if self.status["instructions"] == True:
			self.win.unlock()
			self.win.blit(self.titleBG, self.titleBGRect)
			self.win.blit(self.instructions[self.whichInstruction], self.instructionsRect)

	def redrawAll(self):
		self.win.fill((0,0,0))
		self.drawMenu()
		self.drawPlaying()
		self.drawEditor()
		self.drawOptions()
		self.drawInstructions()
		pygame.transform.scale(self.win, (self.trueWidth, self.trueHeight), self.trueWin)
		if self.status["playing"]:
			if self.stage1.gameTick == 1:
				pygame.display.update()
			else:
				pygame.display.update()#(self.GameWin.updateRects)
		else:
			pygame.display.update()

	def run(self):
		while self.isRunning == True:
			self.clock.tick(60)
			self.ticks += 1
			self.events()
			self.redrawAll()
		pygame.quit()

###############################
###### Main Run Function ######
###############################

def run():
	#Grab some vals from the config
	config = dict()
	fin = fout = None
	#Load and parse the config file.
	try:
		fin = open("config.txt", "rt")
		contents = fin.readlines()
		assert(defaultVals.verify(contents, "config"))
		config = parseConfigVals(contents)
	except:
		config = remakeConfig()
	finally:
		if fin != None: fin.close()
		if fout != None: fout.close()
	pygame.mixer.pre_init(44100, -16, 2, 2048)
	pygame.mixer.init()
	pygame.mixer.set_num_channels(32)
	pygame.init()
	pygame.display.set_caption("15-112: Touhou")
	pygame.display.set_icon(pygame.image.load(os.path.join(os.path.curdir,"img","gui","icon.png")))
	pygame.mouse.set_visible(1)
	pygame.event.set_allowed([pygame.QUIT,pygame.KEYDOWN,pygame.KEYUP])
	screenSize = config["Screen Size"].split("x")
	trueWidth = int(screenSize[0])
	trueHeight = int(screenSize[1])
	win = pygame.display.set_mode((trueWidth,trueHeight))
	game = Touhou(config, win)
	try:
		game.run()
	except:
		popup.error("Fatal Error", "Yikes! A fatal error just occurred!\nFear not though, I'll just restart the program.\nBasically, pygame sucks.")
		run()
#########################
##### Helper Funcs ######
#########################


def collisionCheck(sprite1, sprite2):
	rect1 = None
	rect2 = None
	if hasattr(sprite1, "hitbox"):
		rect1 = sprite1.hitbox.rect
	else: rect1 = sprite1.rect
	if hasattr(sprite2, "hitbox"):
		rect2 = sprite2.hitbox.rect
	else: rect2 = sprite2.rect
	return rect1.colliderect(rect2)

def remakeConfig():
	config = dict()
	popup.error("Incorrect Config", "No config file exists or is broken! Creating new one!")
	fout = open("config.txt", "wt")
	fout.write(defaultVals.config())
	fout.close()
	return parseConfigVals(defaultVals.config().split("\n"))

def parseConfigVals(config):
	#Incase for whatever reason the provided config data
	#hasn't yet been split into lines yet.
	if type(config) != list:
		config = config.split("\n")
	listOfVals = dict()
	#add the vals to a dict with the keys 
	for line in config:
		index = line.find(":")
		if index != -1:
			val = line[index+1:].strip(string.whitespace)
			key = line[0:index].strip(string.whitespace)
			listOfVals[key] = val
	return listOfVals

def modifyConfigVals(key, val):
	fin = fout = None
	try:
		fin = open("config.txt", "rt")
		fout = open("temp.txt","wt")
		content = fin.read()
		start = string.find(content, key)+len(key)+1
		end = string.find(content, "\n", start)
		part1 = content[:start]
		part2 = " "+str(val)
		part3 = content[end:]
		fout.write(part1+part2+part3)

	except:
		config = remakeConfig()
	finally:
		if fin != None: fin.close()
		if fout != None: fout.close()
		os.remove("config.txt")
		os.rename("temp.txt","config.txt")

# http://www.nerdparadise.com/tech/python/pygame/blitopacity/
# Alpha blitting for per-pixel alpha surfaces	
def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)        
    target.blit(temp, location)










####################
# THE ALL HOLY RUN #
####################
####################
run() ##############
####################
####################

#  .----.-----.-----.-----.
# /      \     \     \     \
#|  \/    |     |   __L_____L__
#|   |    |     |  (           \
#|    \___/    /    \______/    |
#|        \___/\___/\___/       |
# \      \     /               /
#  |                        __/
#   \_                   __/
#    |        |         |
#    |                  |
#    |                  |


























