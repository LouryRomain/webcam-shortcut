#Definition des imports
import cv2
import imutils
import numpy as np
import os
import keyboard
import time
import sys
from pynput.mouse import Button, Controller

###########Definition de la classe Grid qui constitue tous les tableaux de reponses et d'evaluation que l'on utilise

def test_1():
	print('ok')

class Grid():

	#Fonction d'initialisation, elle prend comme argument
	#La taille de l'image et la taille de map que l'on fait
	def __init__(self,height,width,shape):
		# L'increment qui permet de separer les gestes
		self.no_count=0
		# Le nombre de mouvement enregistrer pour le signe
		self.count=0
		#le nombre d'image qui faut pour considerer que l'on en fait pas de mouvement
		self.seuil_no_count=5
		#delay d'image entre deux action
		self.action_block=0
		self.action_block_seuil=10
		#Definition des differentes zones
		#initialisation de la map
		self.map=np.zeros((shape[0]-2,shape[1]-2,4))
		#signale qu'une action a ete detecte
		self.action_find=0
		#remplissage des extremite de la facon suivante : haut, bas , gauche , droite
		self.build_zone_map(height,width,shape)
		#Initialisation du tableau de re		ponse memoire 
		self.result_mem=np.zeros((shape[0]-2,shape[1]-2))
		#Initialisation du tableau de memoire des actions trouves 
		self.list_action=[]
		#liste des barycentres
		self.list_bary_x=[]
		self.list_bary_y=[]
		self.val_test=False
		
	#Fonction d'evaluation des zones d'une image en fonction de la map definit et du seuil donne
	def evaluate(self,image,seuil,test):
		if self.get_action_find()==1:
			self.increment_action_block()
			if self.get_action_block_seuil()==self.get_action_block():
				self.set_action_find(0)
				self.reset_action_block()
				self.set_val_test(False)
				print('release')
			return

		#On evalue chaque partie de l'image
		result_tmp=self.evalutation_zone_mean(image,seuil)

		#print(self.result_mem)
		#On compare en suite si il y a eu du changement positif depuis la derniere image
		if (np.maximum(self.get_result_mem(),result_tmp)!=self.get_result_mem()).any():
			# on signale qui il y a eu du changement
			#print(self.get_result_mem())
			if np.sum(result_tmp)>int(0.35*self.get_result_mem_shape()[0]*self.get_result_mem_shape()[1]):
				return
			self.reset_no_count()
			self.increment_count()
			self.barycentre(result_tmp)
			#print(self.get_list_bary_y())
			#On met a jour la memoire en mettant le max de chaque zone 
			self.set_result_mem(np.maximum(self.get_result_mem(),result_tmp))
			if self.get_action_find()==0:
				#On utilise les methode d'activation_horizontale
				self.activation_verticale()
				#On utilise les methode d'activation_horizontale
				self.activation_horizontale()
		else:
			self.increment_no_count()
			if self.get_no_count()==self.get_seuil_no_count():
				if len(self.get_list_action())!=0:
					self.action_detection(test)
				self.reset_result_mem()
				self.reset_no_count()
				self.reset_count()
				self.reset_list_bary_x()
				self.reset_list_bary_y()


	
	def activation_horizontale(self):
		if (np.sum(self.get_result_mem(),axis=(0))>=[int(self.get_result_mem_shape()[0]/5)]*self.get_result_mem_shape()[1]).all():
			list_tmp=soustration_liste(self.get_list_bary_x()[:-1],self.get_list_bary_x()[1:])[-5:]
			if len(list_tmp)==5:
				#self.add_list_action('horizontale')
				if sum(list_tmp)>0:
					self.add_list_action('gauche')
				elif sum(list_tmp)<0:
					self.add_list_action('droite')
			self.reset_result_mem()
			self.reset_list_bary_x()


	def activation_verticale(self):
		if (np.sum(self.get_result_mem()[:,3*int(self.get_result_mem_shape()[1]/5):5*int(self.get_result_mem_shape()[1]/5)],axis=(1))>=[int(self.get_result_mem_shape()[1]/5)]*self.get_result_mem_shape()[0]).all():
			list_tmp=soustration_liste(self.get_list_bary_y()[:-1],self.get_list_bary_y()[1:])[-5:]
			#print(soustration_liste(self.get_list_bary_y()[:-1],self.get_list_bary_y()[1:])[-5:])
			if len(list_tmp)==5:
				if sum(list_tmp)>0:
					self.add_list_action('haut')
				elif sum(list_tmp)<0:
					self.add_list_action('bas')
			self.reset_result_mem()
			self.reset_list_bary_y()
			
	def action(self,string):
		if string=='Onglet Gauche':
			keyboard.press_and_release('ctrl + maj + tab')
		elif string=='Onglet Droit':
			keyboard.press_and_release('ctrl + tab')
		elif string=='Scroll Haut':
			mouse.scroll(0, 10)
		elif string=='Scroll Bas':
			mouse.scroll(0, -10)
		elif string=='Lancer une lecture video':
			keyboard.press_and_release('space')
		elif string=='Ouvrir Explorateur de fichier':
			os.system('explorer')
		elif string=='Capture ecran':
			keyboard.press_and_release('win+maj+S')

	def action_detection(self,test):
		self.set_action_find(1)
		try:
			dict(test)
			if self.get_list_action()[-1] in test.keys():
				self.action(test[self.get_list_action()[-1]])
		except:
			if self.get_list_action()[-1]==test:
				self.set_val_test(True)

		self.reset_list_action()

	def reset_count(self):
		self.count=0

	def get_count(self):
		return self.count

	def increment_count(self):
		self.count=self.count+1
		
	def reset_no_count(self):
		self.no_count=0

	def get_no_count(self):
		return self.no_count

	def increment_no_count(self):
		self.no_count=self.no_count+1
		
	def get_seuil_no_count(self):
		return self.seuil_no_count

	def set_seuil_no_count(self,valeur):
		self.seuil_no_count=valeur
		
	def get_map(self):
		return self.map
	
	def set_map(self,valeur):
		self.map=valeur

	def get_image_map_zone(self,image,i,j):
		return image[int(self.get_map()[i][j][0]):int(self.get_map()[i][j][1]),int(self.get_map()[i][j][2]):int(self.get_map()[i][j][3])]
	
	def get_result_mem(self):
		return self.result_mem
		
	def set_result_mem(self,valeur):
		self.result_mem=valeur
		
	def reset_result_mem(self):
		self.set_result_mem(np.zeros(self.result_mem.shape))
	
	def get_result_mem_shape(self):
		return self.get_result_mem().shape
		
	
	def build_zone_map(self,height,width,shape):
		#remplissage des extremite de la facon suivante : haut, bas , gauche , droite
		for i in range(1,shape[0]-1):
			for j in range(1,shape[1]-1):
				self.get_map()[i-1,j-1,0:4]=[i*int(height/shape[0]),(i+1)*int(height/shape[0]),j*int(width/shape[1]),(j+1)*int(width/shape[1])]
		
	def get_action_find(self):
		return self.action_find
		
	def set_action_find(self,valeur):
		self.action_find=valeur
	
	def evalutation_zone_mean(self,image,seuil):
		#init du tableau temporaire de reponse
		result_tmp=np.zeros(self.get_result_mem_shape())
		#On evalue chaque partie de l'image
		for i in range(0,self.get_result_mem_shape()[0]):
			for j in range(0,self.get_result_mem_shape()[1]):
				result_tmp[i,j]=np.mean(self.get_image_map_zone(image,i,j),axis=(0, 1))>seuil
		return result_tmp

	def get_list_bary_x(self):
		return self.list_bary_x
		
	def set_list_bary_x(self):
		self.list_bary_x=valeur
		
	def reset_list_bary_x(self):
		self.list_bary_x=[]
		
	def add_list_bary_x(self,valeur):
		self.list_bary_x.append(valeur)
		
	def get_list_bary_y(self):
		return self.list_bary_y
		
	def set_list_bary_y(self):
		self.list_bary_y=valeur
		
	def reset_list_bary_y(self):
		self.list_bary_y=[]
		
	def add_list_bary_y(self,valeur):
		self.list_bary_y.append(valeur)
		
	def barycentre(self,image):
		patron_x= [range(1,self.get_result_mem_shape()[1]+1)]*self.get_result_mem_shape()[0]
		patron_y= np.transpose([range(1,self.get_result_mem_shape()[0]+1)]*self.get_result_mem_shape()[1])
		self.add_list_bary_x(np.sum(patron_x*image/np.sum(image)))
		self.add_list_bary_y(np.sum(patron_y*image/np.sum(image)))
		
	def get_action_block(self):
		return self.action_block
	
	def increment_action_block(self):
		self.action_block=self.action_block+1

	def reset_action_block(self):
		self.action_block=0
		
	
	def get_action_block_seuil(self):
		return self.action_block_seuil
	
	def set_action_block_seuil(self,valeur):
		self.action_block_seuil=valeur
		
	def get_list_action(self):
		return self.list_action
		
	def add_list_action(self,valeur):
		self.list_action.append(valeur)
		
	def reset_list_action(self):
		self.list_action=[]
		
	def get_val_test(self):
		return self.val_test
		
	def set_val_test(self,valeur):
		self.val_test=valeur




def soustration_liste(list1,list2):
	out=[]
	for i in range(len(list1)):
		if list1[i]-list2[i]>=0:
			out.append(1)
		else:
			out.append(-1)
	return out

class Image_processing():
	def __init__(self,camera):
		# get the reference to the webcam
		self.camera = camera
		# get the current frame
		(grabbed, frame) = self.camera.read()
		# get the reference to the webcam
		frame = cv2.flip(frame, 1)
		frame = cv2.GaussianBlur(frame, (7, 7), 0)
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		self.frame = cv2.dilate(frame, None, iterations=10)
		self.clone = frame.copy()
		# Creating a window for HSV track bars
		#cv2.namedWindow('Reglage')
		# Creating track bar
		self.seuil_diff=20#cv2.createTrackbar('seuil_diff', 'Reglage',30,255,nothing)
		self.seuil_mean=20#cv2.createTrackbar('seuil_mean', 'Reglage',20,255,nothing)
		self.thresh=[]


	def update(self):
		(grabbed, frame) = self.camera.read()
		# get the reference to the webcam
		frame = cv2.flip(frame, 1)
		frame = cv2.GaussianBlur(frame, (7, 7), 0)
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		self.frame = cv2.dilate(frame, None, iterations=10)
		# Ecart entre les frames
		delta = cv2.absdiff(frame, self.clone)
		# Seuil
		thresh = cv2.threshold(delta,self.seuil_diff, 255, cv2.THRESH_BINARY)[1]
		# Dilatation des zones
		self.thresh = cv2.dilate(thresh, None, iterations=10)
		self.clone = frame.copy()



def nothing(x):
	pass

	
	
	
	
#if __name__ == "__main__":
	##minimum (3,3)
#	shape=(15,20)
	
	#on capture la souris
#	mouse = Controller()
#	video=Image_processing()
#	(height, width) = video.frame.shape[:2]
#	grid=Grid(height,width,shape)
	# keep looping, until interrupted
#	while(True):
#		video.update()
#		
#		grid.evaluate(video.thresh,cv2.getTrackbarPos('seuil_mean', 'Reglage'))

		#Display

	#	cv2.imshow("Video Feed", video.thresh[0:int(height),0:int(width)])

#		# observe the keypress by the user
#		keypress = cv2.waitKey(1) & 0xFF
		# if the user pressed "q", then stop looping
	#	if keypress == ord("q"):
#			break
		
		
	
# free up memory
#video.camera.release()
#cv2.destroyAllWindows()



		#os.system('start .')
		#keyboard.press_and_release('ctrl + tab')
		#keyboard.press_and_release('space')

