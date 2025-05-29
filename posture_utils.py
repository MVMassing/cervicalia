import cv2
import mediapipe as mp
import numpy as np
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class PostureProcessor:
    
    def __init__(self, camera_type="frontal"):
        self.camera_type = camera_type 
        
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.calibrado = False
        self.quadros_calibracao = 0
        self.calibracao_angulo_ombro = []
        self.calibracao_angulo_pescoco = []
        
        self.limite_ombro_min = 0
        self.limite_ombro_max = 0
        self.limite_pescoco_min = 0
        self.limite_pescoco_max = 0
        
        self.margem = 5 
        self.tempo_minimo_postura_ruim = 3
        self.tempo_postura_ruim_iniciado = None
    
    def calcular_angulo(self, ponto1, ponto2, ponto3):
        angulo = np.arctan2(ponto3[1] - ponto2[1], ponto3[0] - ponto2[0]) - np.arctan2(ponto1[1] - ponto2[1], ponto1[0] - ponto2[0])
        return np.abs(angulo * 180.0 / np.pi)
    
    def desenhar_angulo(self, frame, ponto1, ponto2, ponto3, angulo, cor):
        cv2.line(frame, ponto1, ponto2, cor, 3)
        cv2.line(frame, ponto2, ponto3, cor, 3)
        cv2.putText(frame, str(int(angulo)), (ponto2[0] - 50, ponto2[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2, cv2.LINE_AA)
    
    def process_frame(self, frame):
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = self.pose.process(frame_rgb)
            frame_anotado = frame.copy()
            
            if resultados.pose_landmarks:
                pontos = resultados.pose_landmarks.landmark
                
                ombro_esquerdo = (int(pontos[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1]),
                                int(pontos[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]))
                ombro_direito = (int(pontos[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1]),
                               int(pontos[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]))
                orelha_esquerda = (int(pontos[mp_pose.PoseLandmark.LEFT_EAR.value].x * frame.shape[1]),
                                 int(pontos[mp_pose.PoseLandmark.LEFT_EAR.value].y * frame.shape[0]))
                orelha_direita = (int(pontos[mp_pose.PoseLandmark.RIGHT_EAR.value].x * frame.shape[1]),
                                int(pontos[mp_pose.PoseLandmark.RIGHT_EAR.value].y * frame.shape[0]))
                
                angulo_ombro = self.calcular_angulo(ombro_esquerdo, ombro_direito, (ombro_direito[0], 0))
                angulo_pescoco = self.calcular_angulo(orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0))
                
                mp_drawing.draw_landmarks(frame_anotado, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                if not self.calibrado and self.quadros_calibracao < 30:
                    self.calibracao_angulo_ombro.append(angulo_ombro)
                    self.calibracao_angulo_pescoco.append(angulo_pescoco)
                    self.quadros_calibracao += 1
                    
                    cv2.putText(frame_anotado, f"Calibrando... {self.quadros_calibracao}/30", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
                    
                    return frame_anotado, {
                        'calibrando': True,
                        'quadros_calibracao': self.quadros_calibracao,
                        'angulo_ombro': angulo_ombro,
                        'angulo_pescoco': angulo_pescoco,
                        'postura_ruim': False
                    }
                    
                elif not self.calibrado:
                    self.limite_ombro_min = np.mean(self.calibracao_angulo_ombro) - self.margem
                    self.limite_ombro_max = np.mean(self.calibracao_angulo_ombro) + self.margem
                    self.limite_pescoco_min = np.mean(self.calibracao_angulo_pescoco) - self.margem
                    self.limite_pescoco_max = np.mean(self.calibracao_angulo_pescoco) + self.margem
                    self.calibrado = True
                    
                    print(f"Calibração {self.camera_type} concluída.")
                    print(f"Limite Ombro: {self.limite_ombro_min:.1f}-{self.limite_ombro_max:.1f}")
                    print(f"Limite Pescoço: {self.limite_pescoco_min:.1f}-{self.limite_pescoco_max:.1f}")
                
                meio = ((ombro_esquerdo[0] + ombro_direito[0]) // 2, 
                       (ombro_esquerdo[1] + ombro_direito[1]) // 2)
                
                if self.camera_type == "frontal":
                    self.desenhar_angulo(frame_anotado, ombro_esquerdo, meio, (meio[0], 0), angulo_ombro, (255, 0, 0))
                    self.desenhar_angulo(frame_anotado, orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0), angulo_pescoco, (0, 255, 0))
                else:
                    self.desenhar_angulo(frame_anotado, orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0), angulo_pescoco, (0, 255, 0))
                
                postura_ruim = False
                if self.calibrado:
                    if self.camera_type == "frontal":
                        postura_ruim = (angulo_ombro < self.limite_ombro_min or angulo_ombro > self.limite_ombro_max or
                                      angulo_pescoco < self.limite_pescoco_min or angulo_pescoco > self.limite_pescoco_max)
                    else:
                        postura_ruim = (angulo_pescoco < self.limite_pescoco_min or angulo_pescoco > self.limite_pescoco_max)
                    
                    self.desenhar_feedback(frame_anotado, angulo_ombro, angulo_pescoco, postura_ruim)
                
                return frame_anotado, {
                    'calibrando': False,
                    'angulo_ombro': angulo_ombro,
                    'angulo_pescoco': angulo_pescoco,
                    'postura_ruim': postura_ruim,
                    'limite_ombro_min': self.limite_ombro_min,
                    'limite_ombro_max': self.limite_ombro_max,
                    'limite_pescoco_min': self.limite_pescoco_min,
                    'limite_pescoco_max': self.limite_pescoco_max
                }
            
            return frame, None
            
        except Exception as e:
            print(f"Erro no processamento do frame {self.camera_type}: {e}")
            return frame, None
    
    def desenhar_feedback(self, frame, angulo_ombro, angulo_pescoco, postura_ruim):
        try:
            if postura_ruim:
                status = "Postura Ruim"
                cor = (0, 0, 255) 
            else:
                status = "Postura Boa"
                cor = (0, 255, 0) 
            
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2, cv2.LINE_AA)
            
            if self.camera_type == "frontal":
                cv2.putText(frame, f"Ombro: {angulo_ombro:.1f}/{self.limite_ombro_min:.1f}-{self.limite_ombro_max:.1f}", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, f"Pescoco: {angulo_pescoco:.1f}/{self.limite_pescoco_min:.1f}-{self.limite_pescoco_max:.1f}", 
                          (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.putText(frame, f"Cervical: {angulo_pescoco:.1f}/{self.limite_pescoco_min:.1f}-{self.limite_pescoco_max:.1f}", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
                
        except Exception as e:
            print(f"Erro ao desenhar feedback: {e}")
    
    def reset_calibration(self):
        self.calibrado = False
        self.quadros_calibracao = 0
        self.calibracao_angulo_ombro = []
        self.calibracao_angulo_pescoco = []
        self.tempo_postura_ruim_iniciado = None
        print(f"Calibração {self.camera_type} resetada")
    
    def __del__(self):
        if hasattr(self, 'pose'):
            self.pose.close()

def process_frame(frame):
    processor = PostureProcessor()
    result = processor.process_frame(frame)
    processor.__del__()
    return result