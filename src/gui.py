import pygame
import math
import os

class Button(pygame.sprite.Sprite):
	def __init__(self, subdir, image, pos, spriteSheet = False):
		pygame.sprite.Sprite.__init__(self)
		curdir = os.path.curdir
		if not spriteSheet:
			self.imageUnhighlighted = pygame.image.load(os.path.join(curdir, "img", subdir,image+".png")).convert_alpha()
			self.imageHighlighted = pygame.image.load(os.path.join(curdir, "img", subdir,image+"Highlighted.png")).convert_alpha()
		self.image = self.imageUnhighlighted
		self.rect = self.image.get_rect()
		self.position = pos
		self.rect.center = self.position
		self.highlighted = False

	def update(self):
		if self.highlighted == True:
			self.image = self.imageHighlighted
		else:
			self.image = self.imageUnhighlighted


class PauseMenu(object):
	def __init__(self, Touhou):
		def breakdownSheet(subsurface, surface):
			subsurface["returnToGame"] = surface.subsurface(48,32,160,32)
			subsurface["returnToTitle"] = surface.subsurface(48,64,112,32)
			subsurface["giveUpAndRetry"] = surface.subsurface(48,96,128,32)
			subsurface["yes"] = surface.subsurface(160,64,64,32)
			subsurface["no"] = surface.subsurface(176,96,64,32)
			subsurface["saveReplayAndReturnToTitle"] = surface.subsurface(48,128,176,32)
			subsurface["areYouSure"] = surface.subsurface(48,160,144,32)
			subsurface["saveReplay"] = surface.subsurface(48,192,144,32)
			subsurface["playAgain"] = surface.subsurface(0,224,128,32)
			subsurface["continue"] = surface.subsurface(128,224,128,32)

		def assignRects(rects, surfaces):
			center = Touhou.width/2,Touhou.height/2
			offset = 0
			if len(surfaces)%2 == 0:
				offset = 16
			for key in surfaces:
				rects[key] = surfaces[key].get_rect()
				if key == "returnToGame":
					rects[key].center = center[0],center[1]-32
				if key == "giveUpAndRetry":
					rects[key].center = center
				if key == "returnToTitle":
					rects[key].center = center[0],center[1]+32
		self.gradient = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pauseOverlay.png"))
		self.gradientRect = self.gradient.get_rect()
		self.initial = True #Initial pause menu (as opposed to confirmation or stuff)
		self.initOrder = ["returnToGame","giveUpAndRetry","returnToTitle"]
		self.whichHighlighted = {"returnToGame":True,"returnToTitle":False,"giveUpAndRetry":False}
		#self.whichHighlighted = ["returnToGame","returnToTitle","giveUpAndRetry"]
		master = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pause.png")).convert_alpha()
		masterHighlighted = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pauseHighlighted.png")).convert_alpha()
		self.highlighted = dict()
		self.highlightedRects = dict()
		self.unhighlighted = dict()
		self.unhighlightedRects = dict()
		breakdownSheet(self.unhighlighted, master)
		breakdownSheet(self.highlighted, masterHighlighted)
		assignRects(self.highlightedRects, self.highlighted)
		assignRects(self.unhighlightedRects, self.unhighlighted)

class GameOverMenu(PauseMenu):
	def __init__(self, Touhou):
		def breakdownSheet(subsurface, surface):
			subsurface["returnToGame"] = surface.subsurface(48,32,160,32)
			subsurface["returnToTitle"] = surface.subsurface(48,64,112,32)
			subsurface["giveUpAndRetry"] = surface.subsurface(48,96,128,32)
			subsurface["yes"] = surface.subsurface(160,64,64,32)
			subsurface["no"] = surface.subsurface(176,96,64,32)
			subsurface["saveReplayAndReturnToTitle"] = surface.subsurface(48,128,176,32)
			subsurface["areYouSure"] = surface.subsurface(48,160,144,32)
			subsurface["saveReplay"] = surface.subsurface(48,192,144,32)
			subsurface["playAgain"] = surface.subsurface(0,224,128,32)
			subsurface["continue"] = surface.subsurface(128,224,128,32)

		def assignRects(rects, surfaces):
			center = Touhou.width/2,Touhou.height/2
			offset = 0
			for key in surfaces:
				rects[key] = surfaces[key].get_rect()
				if key == "continue":
					rects[key].center = center[0],center[1]-32
				if key == "giveUpAndRetry":
					rects[key].center = center
				if key == "returnToTitle":
					rects[key].center = center[0],center[1]+32
		self.gradient = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pauseOverlay.png"))
		self.gradientRect = self.gradient.get_rect()
		self.initial = True #Initial pause menu (as opposed to confirmation or stuff)
		self.initOrder = ["continue","giveUpAndRetry", "returnToTitle"]
		self.whichHighlighted = {"continue":True,"returnToTitle":False,"giveUpAndRetry":False}
		#self.whichHighlighted = ["returnToGame","returnToTitle","giveUpAndRetry"]
		master = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pause.png")).convert_alpha()
		masterHighlighted = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pauseHighlighted.png")).convert_alpha()
		self.highlighted = dict()
		self.highlightedRects = dict()
		self.unhighlighted = dict()
		self.unhighlightedRects = dict()
		breakdownSheet(self.unhighlighted, master)
		breakdownSheet(self.highlighted, masterHighlighted)
		assignRects(self.highlightedRects, self.highlighted)
		assignRects(self.unhighlightedRects, self.unhighlighted)


class GameWinMenu(PauseMenu):
	def __init__(self, Touhou):
		def breakdownSheet(subsurface, surface):
			subsurface["returnToGame"] = surface.subsurface(48,32,160,32)
			subsurface["returnToTitle"] = surface.subsurface(48,64,112,32)
			subsurface["giveUpAndRetry"] = surface.subsurface(48,96,128,32)
			subsurface["yes"] = surface.subsurface(160,64,64,32)
			subsurface["no"] = surface.subsurface(176,96,64,32)
			subsurface["saveReplayAndReturnToTitle"] = surface.subsurface(48,128,176,32)
			subsurface["areYouSure"] = surface.subsurface(48,160,144,32)
			subsurface["saveReplay"] = surface.subsurface(48,192,144,32)
			subsurface["playAgain"] = surface.subsurface(0,224,128,32)
			subsurface["continue"] = surface.subsurface(128,224,128,32)

		def assignRects(rects, surfaces):
			center = Touhou.width/2,Touhou.height/2
			offset = 0
			for key in surfaces:
				rects[key] = surfaces[key].get_rect()
				if key == "playAgain":
					rects[key].center = center[0],center[1]-16
				if key == "returnToTitle":
					rects[key].center = center[0],center[1]+16
		self.gradient = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pauseOverlay.png"))
		self.gradientRect = self.gradient.get_rect()
		self.initial = True #Initial pause menu (as opposed to confirmation or stuff)
		self.initOrder = ["playAgain", "returnToTitle"]
		self.whichHighlighted = {"playAgain":True,"returnToTitle":False}
		#self.whichHighlighted = ["returnToGame","returnToTitle","giveUpAndRetry"]
		master = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pause.png")).convert_alpha()
		masterHighlighted = pygame.image.load(os.path.join(os.path.curdir,"img","gui","pauseHighlighted.png")).convert_alpha()
		self.winMessage = pygame.image.load(os.path.join(os.path.curdir,"img","gui","GameWin.png")).convert_alpha()
		self.winMessageRect = self.winMessage.get_rect(center=(320,120))
		self.highlighted = dict()
		self.highlightedRects = dict()
		self.unhighlighted = dict()
		self.unhighlightedRects = dict()
		breakdownSheet(self.unhighlighted, master)
		breakdownSheet(self.highlighted, masterHighlighted)
		assignRects(self.highlightedRects, self.highlighted)
		assignRects(self.unhighlightedRects, self.unhighlighted)



class Window(object):
	def __init__(self, config):
		self.winWidth = int(config["Screen Size"].split("x")[0])
		self.winHeight = int(config["Screen Size"].split("x")[1])
		master = pygame.image.load(os.path.join(os.path.curdir,"img","gui","front00.png")).convert_alpha()
		self.left = pygame.transform.scale(master.subsurface(64,40,64,440), (128,480))
		self.leftRect = (-64,0,64,480)
		self.right = pygame.transform.scale(master.subsurface(128,0,128,440), (192,480))
		self.rightRect = (448,0,192,400)
		self.top = master.subsurface(0,480,384,16)
		self.topRect = (64,0,384,16)
		self.bot = master.subsurface(0,496,384,16)
		self.botRect = (64,464,384,16)
		self.topBorder = 12
		self.botBorder = 468
		self.leftBorder = 60
		self.rightBorder = 452
		self.center= (self.rightBorder-self.leftBorder)/2+self.leftBorder,(self.botBorder-self.topBorder)/2
		self.gameScreenRect = (self.leftBorder, self.topBorder,
							   self.rightBorder, self.botBorder)
		master = pygame.image.load(os.path.join(os.path.curdir,"img","gui","front01.png")).convert_alpha()
		self.scoreText = master.subsurface((277,17,56,18)) #rect where the score is
		self.playerText = master.subsurface((270,34,64,22))
		self.powerText = master.subsurface((269,57,64,18))
		#the rects to update when using pygame.display.update
		self.updateRects = [self.gameScreenRect,
							(524, 64, 112, 16)]
		self.lifeIcon = master.subsurface((464,2,16,16))
		master = pygame.image.load(os.path.join(os.path.curdir,"img","gui","ascii.png")).convert_alpha()
		self.numbers = list()
		for i in xrange(12):
			self.numbers.append(master.subsurface((i*16,8*27,16,16)))


	def drawScreen(self, Touhou):
		win = Touhou.win
		#draw the borders
		win.blit(self.left, self.leftRect)
		win.blit(self.right, self.rightRect)
		win.blit(self.top, self.topRect)
		win.blit(self.bot, self.botRect)
		#draw the constant text
		win.blit(self.scoreText, (460, 64, 64, 32))
		win.blit(self.powerText, (456, 96, 64, 18))
		win.blit(self.playerText, (456, 128, 64, 18))
		#draw the variable text
		score = str(Touhou.score)
		scoreImages = list()
		level = "%.2f" % (Touhou.reimu.power/100.0)
		levelImages = list()
		#convert the score int into a list of images of numbers
		for c in score:
			scoreImages.append(self.numbers[int(c)])
		numZeroes = 7-len(scoreImages)
		# same but for level
		for c in level:
			if c == ".":
				levelImages.append(self.numbers[11])
				continue
			levelImages.append(self.numbers[int(c)])
		# draw the actual score
		for i in xrange(numZeroes):
			x = 524+i*16
			win.blit(self.numbers[0],(x,64,12,12))
		for i in xrange(len(scoreImages)):
			x = 524+(numZeroes+i)*16
			win.blit(scoreImages[i],(x,64,12,12))
		# draw power level
		for i in xrange(len(levelImages)):
			x = 524+i*16
			win.blit(levelImages[i],(x,96,16,16))
		# draw lives
		for i in xrange(Touhou.reimu.lives):
			x = 524+i*16
			win.blit(self.lifeIcon,(x,128,16,16))
