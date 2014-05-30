import pygame
import math
import random



###################
# SPRITE MOVEMENT #
###################
class Still(object):
	def __init__(self, **kwargs):
		pass
	def update(self, sprite, **kwargs):
		pass

class Straight(object):
		#Add code to format slope, or equation, input into proper terms
	def __init__(self, **kwargs):
		parseAttributes(self, **kwargs)
		self.tick = 0
	def update(self, sprite, **kwargs):
		self.tick += 1
		keys = kwargs
		vel = self.vel
		bulletGroup = kwargs["bulletGroup"] if "bulletGroup" in kwargs else None
		shots = kwargs["shots"] if "shots" in kwargs else None
		if self.dir == "left":
			vel = -self.vel
		#This next line will adjust the offset so the hypotenuse of the
		#dx and dy will equal velocity and not something crazy
		dx,dy = vel*math.cos(self.angle), vel*math.sin(self.angle)
		sprite.pos = sprite.pos[0]+dx,sprite.pos[1]+dy
		sprite.pos = sprite.pos[0]+dx,sprite.pos[1]+dy
		if self.shotType == "interval":
			if (self.tick >= self.shotTimer and 
				self.tick < self.shotTimer+self.shotDuration):
				if self.tick%self.shotInterval == 0:
					sprite.shoot(kwargs["playerpos"],kwargs["bulletGroup"])
		if self.shotType == "fanSpread":
			if self.tick == self.shotTimer:
				for bullet in shots:
					bullet.pos = sprite.rect.center
				bulletGroup.add(shots)
		if self.tick > 300: sprite.kill

class Accel(object):
	def __init__(self, initVel=0.1, dVel=0.1, finalVel=3, angle=0):
		self.initVel = initVel
		self.vel = initVel
		self.dVel = dVel

		self.finalVel = finalVel
		self.angle = angle
		self.tick = 0
	def update(self, sprite):
		self.tick+=1
		self.vel = self.vel+self.dVel*self.tick if self.vel+self.dVel*self.tick<=self.finalVel else self.finalVel
		x,y = sprite.pos
		sprite.pos = x,y+self.vel
		sprite.rect.center = sprite.pos
		sprite.hitbox.rect.center = sprite.pos


class MovePauseMove(object):
	def __init__(self, **kwargs):
		parseAttributes(self, **kwargs)
		self.tick = 0
	def update(self, sprite, **kwargs):
		self.tick += 1
		bulletGroup = kwargs["bulletGroup"]
		shots = kwargs["shots"]
		## MOVEMENT HANDLING ##
		vel = self.vel
		if self.dir == "left":
			vel = -self.vel
		#This next line will adjust the offset so the hypotenuse of the
		#dx and dy will equal velocity and not something crazy
		dx,dy = vel*math.cos(self.angle), vel*math.sin(self.angle)
		#Move forwards
		if self.tick <= self.moveTimer:
			sprite.pos = sprite.pos[0]+dx,sprite.pos[1]+dy
		#Move backwards
		if self.tick > self.moveTimer+self.pauseTimer:
			sprite.pos = sprite.pos[0]-dx,sprite.pos[1]-dy
			#And just incase something crazy happens and the sprite doesn't get deleted
			#This will autokill the sprite
		## SHOT HANDLING ##
		if self.shotType == "ring":
			if self.tick == self.shotTimer: 
				for bullet in shots:
					bullet.pos = sprite.rect.center
				bulletGroup.add(shots)
		if self.shotType == "interval":
			if (self.tick >= self.shotTimer and 
				self.tick < self.shotTimer+self.shotDuration):
				if self.tick%self.shotInterval == 0:
					sprite.shoot(kwargs["playerpos"],kwargs["bulletGroup"])


def parseAttributes(self, **kwargs):
	#how long it pauses
	self.pauseTimer = kwargs["pauseTimer"] if "pauseTimer" in kwargs else 300
	#when it shoots
	self.shotTimer = kwargs["shotTimer"] if "shotTimer" in kwargs else 450
	#how long it moves
	self.moveTimer = kwargs["moveTimer"] if "moveTimer" in kwargs else 300
	#equation of movement
	self.slope = kwargs["eq"] if "eq" in kwargs else 0
	self.angle = math.atan2(self.slope,1)
	#velocity
	self.vel = kwargs["vel"] if "vel" in kwargs else 1
	#The shottype
	self.shotType = kwargs["shotType"] if "shotType" in kwargs else "random"
	#direction
	self.dir = kwargs["direction"] if "direction" in kwargs else "right"
	#interval at which it shoots if using interval shottype
	self.shotInterval = kwargs["shotInterval"] if "shotInterval" in kwargs else 20
	#How long to shoot if using interval
	self.shotDuration = kwargs["shotDuration"] if "shotDuration" in kwargs else 120


###################
### BULLET PATH ###
###################

