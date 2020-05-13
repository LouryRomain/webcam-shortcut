from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.camera import Camera
import moving
from pynput.mouse import Button, Controller
import cv2
import kivy.core.text
import cv2
from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
import gc


#capture=cv2.VideoCapture(0)

class ConfigButton(ToggleButton):

	def load_config(self,id):
		file=open('config/config_'+id+'.txt','r').read()
		return eval(file)

class SaveButton(Button):

	def save_config(self,id,value):
		file=open('config/config_'+id+'.txt','w')
		file.write(str(value))
		file.close()

class KivyCamera(Image):
	def __init__(self, capture, fps,seuil, test, **kwargs):
		super(KivyCamera, self).__init__(**kwargs)
		self.capture = capture
		self.clock=Clock
		shape=(15,20)
		self.video=moving.Image_processing(self.capture)
		(height, width) = self.video.frame.shape[:2]
		self.grid=moving.Grid(height,width,shape)
		self.event=self.clock.schedule_interval(self.update, 1.0 / fps)
		self.test=test
		self.seuil_mean=seuil


	def update(self,dt):
		try:
			ret, frame = self.capture.read()
			if ret:
				# convert it to texture
				buf1 = cv2.flip(frame, -1)
				buf = buf1.tostring()
				image_texture = Texture.create(
					size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
				image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
				# display image from the texture
				self.texture = image_texture
				# keep looping, until interrupted
				self.video.update()
				#cv2.imshow("Video Feed", video.thresh[0:int(height),0:int(width)])
				self.grid.evaluate(self.video.thresh,self.seuil_mean,self.test)
				if self.grid.val_test==False:
					self.color = [1, 1, 1, 1]
				else:
					self.color = [0, 1, 0, 0.5]
				
		except:
			pass

	def stop(self): 
		self.event.cancel()
		print('Destructor called, Camera deleted.') 



		
class Screen1(Screen):
	pass


class Screen2(Screen):
	def limit_spinner(self, *args):
		max = 5  # max number of Buttons to display in the Spinner DropDown
		for i in self.spinners:
			i.dropdown_cls.max_height =  max * dp(48)# dp(48) is the size of each Button in the DropDown (from style.kv)

	def launch(self,dico_action,state):
		print(state)
		if state=='down':
			##minimum (3,3)
			shape=(15,20)
			self.capture=cv2.VideoCapture(0)
			self.video=moving.Image_processing(self.capture)
			self.dico_action=dico_action
			(height, width) = self.video.frame.shape[:2]
			self.grid=moving.Grid(height,width,shape)
			# keep looping, until interrupted
			self.clock=Clock
			self.event=self.clock.schedule_interval(self.update, 1.0 / 30)
		else:
			self.event.cancel()
			self.capture.release()
			cv2.destroyAllWindows()
			del self.grid
			del self.video
	
	def update(self,dt):
		self.video.update()
		self.grid.evaluate(self.video.thresh,self.video.seuil_mean,self.dico_action)






class Screen3(Screen):
	def __init__(self, **kwargs):
		super(Screen3, self).__init__(**kwargs)
		self.status=None

	def on_enter(self,test='no'):
		if self.status!='in':
			self.status='in'
			self.capture=cv2.VideoCapture(0)
			self.kivycam=KivyCamera(capture=self.capture, fps=30,seuil=30,test=test)
			self.add_widget(self.kivycam)

	def on_leave(self):
		if self.status!='out':
			self.status='out'
			self.remove_widget(self.kivycam)
			self.capture.release()
			cv2.destroyAllWindows()


class BetaApp(App):
	pass

if __name__ == "__main__":
	BetaApp().run()