from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import time
import os
import threading
import winsound

from ...infrastructure.camera.camera_thread import CameraThread
from ...application.services.posture_analysis_service import PostureAnalysisService
from ...application.use_cases.posture_monitoring import PostureMonitoringUseCase

class PostureMonitorScreen(Screen):
    def __init__(self, repository, **kwargs):
        super().__init__(**kwargs)
        self.repository = repository
        self.monitoring_use_case = PostureMonitoringUseCase(self.repository)
        self.frontal_only = True
        self.lateral_ip = ""
        self.last_bad_posture_time = {}
        self.lateral_processor = None
        self.lateral_thread = None
        self.frontal_processor = None
        self.last_save_time = 0
        self.save_interval = 5
    
    def setup_cameras(self, frontal_only=True, lateral_ip=""):
        self.frontal_only = frontal_only
        self.lateral_ip = lateral_ip
        
        self.frontal_processor = PostureAnalysisService("frontal")
        self.lateral_processor = PostureAnalysisService("lateral") if not frontal_only else None
        
        self.frontal_cam = cv2.VideoCapture(0)
        if not self.frontal_cam.isOpened():
            print("Erro: Não foi possível abrir a câmera frontal")
            return
            
        self.frontal_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.frontal_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.frontal_cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not frontal_only and lateral_ip:
            self.lateral_thread = CameraThread(lateral_ip)
            self.lateral_thread.start()
        else:
            self.lateral_thread = None
            self.lateral_processor = None
            self.ids.lateral_cam.opacity = 0
            self.ids.lateral_angle.opacity = 0
            self.ids.lateral_status.opacity = 0
        
        self.is_calibrated = False
        self.last_alert_time = 0
        self.alert_interval = 10
        self.alert_sound = "assets/alert.wav"
        
        Clock.schedule_interval(self.update_frame, 1.0/30)
        
        self.ids.status.text = "AGUARDANDO CALIBRAÇÃO"
        self.ids.status.theme_text_color = "Custom"
        self.ids.status.text_color = (1, 0, 0, 1)
    
    def update_frame(self, dt):
        if not hasattr(self, 'frontal_cam') or self.frontal_cam is None:
            return
        if not hasattr(self, 'frontal_processor') or self.frontal_processor is None:
            return
            
        ret, frontal_frame = self.frontal_cam.read()
        if ret:
            frame_annotated, analysis_result = self.frontal_processor.process_frame(frontal_frame)
            self.show_frame(frame_annotated, 'frontal')
            if analysis_result and self.is_calibrated:
                self.update_interface(analysis_result, 'frontal')
                self.save_posture_data(analysis_result, 'frontal')
        
        if not self.frontal_only and self.lateral_thread and self.lateral_processor:
            lateral_frame = self.lateral_thread.get_frame()
            if lateral_frame is not None:
                frame_annotated, analysis_result = self.lateral_processor.process_frame(lateral_frame)
                self.show_frame(frame_annotated, 'lateral')
                if analysis_result and self.is_calibrated:
                    self.update_interface(analysis_result, 'lateral')
                    self.save_posture_data(analysis_result, 'lateral')
    
    def show_frame(self, frame, camera_type):
        try:
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.ids[f'{camera_type}_cam'].texture = texture
        except Exception as e:
            print(f"Erro ao mostrar frame {camera_type}: {e}")
    
    def update_interface(self, analysis_result, camera_type):
        try:
            if analysis_result.is_calibrating:
                self.ids[f'{camera_type}_angle'].text = f"{camera_type.upper()}: Calibrando... {analysis_result.calibration_frames}/30"
                self.ids[f'{camera_type}_status'].text = "CALIBRANDO"
                self.ids[f'{camera_type}_status'].text_color = (1, 1, 0, 1)
            else:
                if camera_type == 'frontal':
                    angle_text = f"FRONTAL: Ombro={analysis_result.shoulder_angle:.1f}° Pescoço={analysis_result.neck_angle:.1f}°"
                else:
                    angle_text = f"LATERAL: Cervical={analysis_result.neck_angle:.1f}°"
                
                self.ids[f'{camera_type}_angle'].text = angle_text
                
                if analysis_result.is_poor_posture:
                    self.ids[f'{camera_type}_status'].text = "POSTURA RUIM"
                    self.ids[f'{camera_type}_status'].text_color = (1, 0, 0, 1)
                    self.check_alert()
                else:
                    self.ids[f'{camera_type}_status'].text = "POSTURA BOA"
                    self.ids[f'{camera_type}_status'].text_color = (0, 1, 0, 1)
        except Exception as e:
            print(f"Erro ao atualizar interface {camera_type}: {e}")
    
    def save_posture_data(self, analysis_result, camera_type):
        """Salva dados de postura periodicamente"""
        current_time = time.time()
        if current_time - self.last_save_time > self.save_interval:
            try:
                if analysis_result and analysis_result.calibration_data:
                    self.monitoring_use_case.process_posture_frame(
                        analysis_result.shoulder_angle,
                        analysis_result.neck_angle,
                        camera_type,
                        analysis_result.calibration_data
                    )
                    self.last_save_time = current_time
                    print(f"Dados {camera_type} salvos")
            except Exception as e:
                print(f"Erro ao salvar dados {camera_type}: {e}")
    
    def save_alert_data(self):
        try:
            if hasattr(self, 'frontal_processor') and self.frontal_processor:
                frontal_result = self.frontal_processor.get_last_result()
                if frontal_result and frontal_result.is_poor_posture and frontal_result.calibration_data:
                    self.monitoring_use_case.process_posture_frame(
                        frontal_result.shoulder_angle,
                        frontal_result.neck_angle,
                        'frontal',
                        frontal_result.calibration_data
                    )
                    print("Dados frontais salvos devido ao alerta")
            
            if hasattr(self, 'lateral_processor') and self.lateral_processor:
                lateral_result = self.lateral_processor.get_last_result()
                if lateral_result and lateral_result.is_poor_posture and lateral_result.calibration_data:
                    self.monitoring_use_case.process_posture_frame(
                        lateral_result.shoulder_angle,
                        lateral_result.neck_angle,
                        'lateral',
                        lateral_result.calibration_data
                    )
                    print("Dados laterais salvos devido ao alerta")
                    
        except Exception as e:
            print(f"Erro ao salvar dados do alerta: {e}")
    
    def play_alert_sound(self):
        """Reproduz alerta sonoro usando winsound (mais confiável em executáveis)"""
        def play_sound():
            try:
                print("Tocando alerta sonoro...")
                winsound.Beep(800, 200) 
                time.sleep(0.1)
                winsound.Beep(1000, 200)
                time.sleep(0.1)
                winsound.Beep(1200, 300)
                
                print("Alerta sonoro reproduzido com sucesso!")
                
            except Exception as e:
                print(f"Erro ao reproduzir alerta sonoro: {e}")
                try:
                    winsound.Beep(1000, 500)
                    print("Alerta sonoro simples reproduzido")
                except:
                    print("Não foi possível reproduzir nenhum alerta sonoro")
        threading.Thread(target=play_sound, daemon=True).start()
    
    def check_alert(self):
        current_time = time.time()
        if current_time - self.last_alert_time > self.alert_interval:
            self.play_alert_sound()
            self.last_alert_time = current_time
            self.save_alert_data()
    
    def calibrate(self):
        if hasattr(self, 'frontal_processor') and self.frontal_processor:
            self.frontal_processor.reset_calibration()
        if hasattr(self, 'lateral_processor') and self.lateral_processor:
            self.lateral_processor.reset_calibration()
        
        self.is_calibrated = False
        self.ids.status.text = "RECALIBRANDO..."
        self.ids.status.theme_text_color = "Custom"
        self.ids.status.text_color = (1, 1, 0, 1)
        
        Clock.schedule_once(self.check_calibration, 1)
    
    def check_calibration(self, dt):
        frontal_calibrated = self.frontal_processor.is_calibrated if hasattr(self, 'frontal_processor') and self.frontal_processor else False
        lateral_calibrated = self.lateral_processor.is_calibrated if self.lateral_processor else True
        
        if frontal_calibrated and lateral_calibrated:
            self.is_calibrated = True
            self.ids.status.text = "CALIBRADO - MONITORANDO"
            self.ids.status.text_color = (0, 1, 0, 1)
        else:
            Clock.schedule_once(self.check_calibration, 1)
    
    def go_back(self):
        self.on_stop()
        self.manager.current = 'welcome'
    
    def on_stop(self):
        Clock.unschedule(self.update_frame)
        
        if hasattr(self, 'lateral_thread') and self.lateral_thread:
            self.lateral_thread.running = False
        if hasattr(self, 'frontal_cam'):
            self.frontal_cam.release()
        if hasattr(self, 'frontal_processor'):
            del self.frontal_processor
        if hasattr(self, 'lateral_processor'):
            del self.lateral_processor 