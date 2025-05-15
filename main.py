from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from camera_thread import CameraThread
from posture_utils import process_frame
from playsound import playsound
import cv2
import time

Builder.load_file('assets/styles.kv')

class PostureCorrector(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Configuração das câmeras
        self.frontal_cam = cv2.VideoCapture(0)
        self.frontal_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.frontal_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Thread para DroidCam
        self.lateral_thread = CameraThread("http://192.168.1.17:4747/video")
        self.lateral_thread.start()
        
        # Variáveis de estado
        self.calibrado = False
        self.ultimo_alerta = 0
        self.frame_counter = 0
        
        Clock.schedule_interval(self.update, 1.0/30)

    def update(self, dt):
        # Webcam frontal
        ret, frontal_frame = self.frontal_cam.read()
        if ret:
            frame_anotado, dados = process_frame(frontal_frame)
            self.mostrar_frame(frame_anotado, 'frontal')
            if dados:
                self.atualizar_interface(dados, 'frontal')
        
        # DroidCam (a cada 2 frames)
        if self.frame_counter % 2 == 0:
            lateral_frame = self.lateral_thread.get_frame()
            if lateral_frame is not None:
                lateral_frame = cv2.rotate(lateral_frame, cv2.ROTATE_90_CLOCKWISE)
                frame_anotado, dados = process_frame(lateral_frame)
                self.mostrar_frame(frame_anotado, 'lateral')
                if dados:
                    self.atualizar_interface(dados, 'lateral')
        
        self.frame_counter += 1

    def mostrar_frame(self, frame, tipo):
        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.ids[f'{tipo}_cam'].texture = texture

    def atualizar_interface(self, dados, tipo):
        self.ids[f'{tipo}_angle'].text = f"{tipo.upper()}: Ombro={dados['angulo_ombro']:.1f}° Pescoço={dados['angulo_pescoco']:.1f}°"
        
        if dados['postura_ruim']:
            self.ids[f'{tipo}_status'].text = "POSTURA RUIM"
            self.ids[f'{tipo}_status'].text_color = (1, 0, 0, 1)
            self.verificar_alerta()
        else:
            self.ids[f'{tipo}_status'].text = "POSTURA OK"
            self.ids[f'{tipo}_status'].text_color = (0, 1, 0, 1)

    def verificar_alerta(self):
        if time.time() - self.ultimo_alerta > 10:
            try:
                playsound('assets/alert.wav')
                self.ultimo_alerta = time.time()
            except:
                import winsound
                winsound.PlaySound('assets/alert.wav', winsound.SND_FILENAME)

    def calibrar(self):
        self.calibrado = True
        self.ids.status.text = "CALIBRADO"
        self.ids.status.theme_text_color = "Custom"
        self.ids.status.text_color = (0, 1, 0, 1)

class PostureApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        return PostureCorrector()

if __name__ == '__main__':
    PostureApp().run()