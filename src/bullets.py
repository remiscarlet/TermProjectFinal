import math
import pygame
import sprites
import copy
import threading
from multiprocessing.pool import ThreadPool

####################################################
## For creating bullet PATTERNS. NOT FOR SHOOTING ##
## SHOOTING IS HANDLED UNDER PATHS DUE TO TIMING  ##
####################################################


#Self is the object we're adding bullets to, ringCount is how many rings to shoot
#group is the sprite group to add the bullets to
#dVel is the variance in velocity per ring. Eg, first ring moves at v=5, second ring moves at v=10, etc
#startVel is the velocity(by pixel/tick) of the "slowest" ring
#numBulletsInRing fits that many bullets into each ring
def multiCircle(self, ringCount=1, dVel=5, startVel=5, numBulletsInRing=10, bulletType="GenericBulletWhite", startAngle=0):
	def f(this, xrangeNum, vel, dAngle, startAngle):
		spriteList = list()
		for i in xrange(xrangeNum):
			spriteList.append(eval("sprites."+bulletType+"(startAngle+dAngle*i, this.rect.center, vel)"))
		#bulletGroup.add(spriteList)
		return spriteList
	dAngle = 360.0/numBulletsInRing
	listOfBullets = list()
	for ring in xrange(ringCount):
		vel = startVel+ring*dVel
		bulletPool = ThreadPool(processes=1)
		result = bulletPool.apply_async(f, (self, numBulletsInRing, vel, dAngle, startAngle))
		listOfBullets.extend(result.get())
		bulletPool.close()
	return listOfBullets

def fanSpread(self, angleWidth=160, numBulletsInSpread=20, vel=5, bulletType="GenericBulletWhite"):
	halfAngle = angleWidth/2
	centerAngle = 270
	startAngle = centerAngle-halfAngle
	dAngle = angleWidth/float(numBulletsInSpread)
	listOfBullets = list()
	for i in xrange(numBulletsInSpread):
		listOfBullets.append(eval("sprites."+bulletType+"(startAngle+dAngle*i, self.rect.center, vel)"))
	return listOfBullets
