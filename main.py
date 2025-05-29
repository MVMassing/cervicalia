from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from camera_thread import CameraThread
from posture_utils import PostureProcessor
from playsound import playsound
import cv2
import time
import numpy as np
import os

Builder.load_file('assets/styles.kv')

class PostureCorrector(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.frontal_processor = PostureProcessor("frontal")
        self.lateral_processor = PostureProcessor("lateral")
        
        self.frontal_cam = cv2.VideoCapture(0)
        self.frontal_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.frontal_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.frontal_cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.lateral_thread = CameraThread("http://192.168.1.101:4747/video")
        self.lateral_thread.start()
        
        self.calibrado = False
        self.ultimo_alerta = 0
        self.tempo_alerta = 10
        
        self.alerta = "assets/alert.wav"
        
        Clock.schedule_interval(self.update, 1.0/30)

    def update(self, dt):
        ret, frontal_frame = self.frontal_cam.read()
        if ret:
            frame_anotado, dados = self.frontal_processor.process_frame(frontal_frame)
            self.mostrar_frame(frame_anotado, 'frontal')
            if dados:
                self.atualizar_interface(dados, 'frontal')
        
        lateral_frame = self.lateral_thread.get_frame()
        if lateral_frame is not None:
            frame_anotado, dados = self.lateral_processor.process_frame(lateral_frame)
            self.mostrar_frame(frame_anotado, 'lateral')
            if dados:
                self.atualizar_interface(dados, 'lateral')

    def mostrar_frame(self, frame, tipo):
        try:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.ids[f'{tipo}_cam'].texture = texture
        except Exception as e:
            print(f"Erro ao mostrar frame {tipo}: {e}")

    def atualizar_interface(self, dados, tipo):
        try:
            if dados['calibrando']:
                self.ids[f'{tipo}_angle'].text = f"{tipo.upper()}: Calibrando... {dados['quadros_calibracao']}/30"
                self.ids[f'{tipo}_status'].text = "CALIBRANDO"
                self.ids[f'{tipo}_status'].text_color = (1, 1, 0, 1)  # Amarelo
            else:
                if tipo == 'frontal':
                    angle_text = f"FRONTAL: Ombro={dados['angulo_ombro']:.1f}° Pescoço={dados['angulo_pescoco']:.1f}°"
                else:
                    angle_text = f"LATERAL: Cervical={dados['angulo_pescoco']:.1f}°"
                
                self.ids[f'{tipo}_angle'].text = angle_text
                
                if dados['postura_ruim']:
                    self.ids[f'{tipo}_status'].text = "POSTURA RUIM"
                    self.ids[f'{tipo}_status'].text_color = (1, 0, 0, 1) 
                    self.verificar_alerta()
                else:
                    self.ids[f'{tipo}_status'].text = "POSTURA BOA"
                    self.ids[f'{tipo}_status'].text_color = (0, 1, 0, 1) 
                    
        except Exception as e:
            print(f"Erro ao atualizar interface {tipo}: {e}")

    def verificar_alerta(self):
        tempo_atual = time.time()
        if tempo_atual - self.ultimo_alerta > self.tempo_alerta:
            try:
                if os.path.exists(self.alerta):
                    playsound(self.alerta, block=False)
                    print("Alerta sonoro disparado!")
                    self.ultimo_alerta = tempo_atual
            except Exception as e:
                print(f"Erro ao tocar alerta: {e}")

    def calibrar(self):
        self.frontal_processor.reset_calibration()
        self.lateral_processor.reset_calibration()
        self.calibrado = False
        self.ids.status.text = "RECALIBRANDO..."
        self.ids.status.theme_text_color = "Custom"
        self.ids.status.text_color = (1, 1, 0, 1)

    def on_stop(self):
        if hasattr(self, 'lateral_thread'):
            self.lateral_thread.running = False
        if hasattr(self, 'frontal_cam'):
            self.frontal_cam.release()
        if hasattr(self, 'frontal_processor'):
            del self.frontal_processor
        if hasattr(self, 'lateral_processor'):
            del self.lateral_processor

class PostureApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        return PostureCorrector()

    def on_stop(self):
        self.root.on_stop()
        return True

if __name__ == '__main__':
    PostureApp().run()