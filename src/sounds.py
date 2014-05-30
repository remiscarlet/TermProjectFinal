#########################################
######  Sound Initialisation File  ######
#########################################
import os
import pygame

class SFX(object):
	def __init__(self):
		self.damage00 = pygame.mixer.Sound(os.path.join('sound', 'sfx', 'se_damage00.wav')) 
		self.damage01 = pygame.mixer.Sound(os.path.join('sound', 'sfx', 'se_damage01.wav')) 
		self.ok = pygame.mixer.Sound(os.path.join('sound', 'sfx', 'se_ok00.wav'))
		self.shoot = pygame.mixer.Sound(os.path.join('sound','sfx','se_plst00.wav'))
		self.kill = pygame.mixer.Sound(os.path.join('sound','sfx','se_tan00.wav'))
		self.death = pygame.mixer.Sound(os.path.join('sound','sfx','se_pldead00.wav'))
		self.pause = pygame.mixer.Sound(os.path.join('sound', 'sfx', 'se_pause.wav'))
		self.gameOver = pygame.mixer.Sound(os.path.join('sound','sfx','se_playerdead.wav'))
		self.damage = pygame.mixer.Sound(os.path.join('sound','sfx','se_damage00.wav'))
		self.enemyShoot = pygame.mixer.Sound(os.path.join('sound','sfx','se_tan01.wav'))
		self.spellClear = pygame.mixer.Sound(os.path.join('sound','sfx','se_enep02.wav'))
		self.gameWin = pygame.mixer.Sound(os.path.join('sound','sfx','se_enep01.wav'))
		self.itemGet = pygame.mixer.Sound(os.path.join('sound','sfx','se_item00.wav'))
		self.laser = pygame.mixer.Sound(os.path.join('sound','sfx','se_lazer00.wav'))
	def setVolume(self, vol):
		self.damage00.set_volume(vol)
		self.damage01.set_volume(vol)
		self.ok.set_volume(vol)
		self.shoot.set_volume(vol)
		self.kill.set_volume(vol)
		self.death.set_volume(vol)
		self.pause.set_volume(vol)
		self.gameOver.set_volume(vol)
		self.damage.set_volume(vol)
		self.enemyShoot.set_volume(vol)
		self.spellClear.set_volume(vol)
		self.gameWin.set_volume(vol)
		self.itemGet.set_volume(vol)
		self.laser.set_volume(vol)

class BGM(object):
	def __init__(self):
		self.title = os.path.join('sound', 'bgm', 'Eiyashou ~ Eastern Night.ogg')
		self.stage1theme = os.path.join('sound', 'bgm', 'Genshi no Yoru ~ Ghostly Eyes.ogg')
		self.gameOver = os.path.join('sound','bgm','PlayerScore.ogg')
		self.septette = os.path.join('sound', 'bgm', 'Naki Oujo no Tame no Septette.ogg')
