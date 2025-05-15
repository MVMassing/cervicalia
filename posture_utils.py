import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def process_frame(frame):
    """Processa o frame com MediaPipe e retorna o frame anotado + dados posturais"""
    with mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        
        # Converte e processa o frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = pose.process(frame_rgb)
        frame_anotado = frame.copy()
        
        if resultados.pose_landmarks:
            # Desenha landmarks e conexões
            mp_drawing.draw_landmarks(
                frame_anotado,
                resultados.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            # Calcula ângulos posturais
            dados = calcular_angulos(resultados.pose_landmarks, frame.shape)
            
            # Desenha ângulos
            desenhar_angulos(frame_anotado, dados)
            
            return frame_anotado, dados
        
        return frame, None

def calcular_angulos(landmarks, frame_shape):
    """Calcula os ângulos posturais"""
    h, w = frame_shape[:2]
    
    # Pontos-chave
    ombro_esq = (int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w),
                 int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h))
    ombro_dir = (int(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w),
                 int(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h))
    orelha_esq = (int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR].x * w),
                  int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR].y * h))
    
    # Cálculos
    angulo_ombro = calcular_angulo(ombro_esq, ombro_dir, (ombro_dir[0], 0))
    angulo_pescoco = calcular_angulo(orelha_esq, ombro_esq, (ombro_esq[0], 0))
    
    return {
        'angulo_ombro': abs(angulo_ombro),
        'angulo_pescoco': abs(angulo_pescoco),
        'pontos': {'ombro_esq': ombro_esq, 'ombro_dir': ombro_dir, 'orelha_esq': orelha_esq},
        'postura_ruim': False  # Implemente sua lógica aqui
    }

def calcular_angulo(a, b, c):
    """Calcula ângulo entre 3 pontos"""
    angulo = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    return np.abs(np.degrees(angulo))

def desenhar_angulos(frame, dados):
    """Desenha ângulos e linhas no frame"""
    pts = dados['pontos']
    meio = ((pts['ombro_esq'][0] + pts['ombro_dir'][0]) // 2,
            (pts['ombro_esq'][1] + pts['ombro_dir'][1]) // 2)
    
    # Ângulo dos ombros
    cv2.line(frame, pts['ombro_esq'], meio, (255, 0, 0), 2)
    cv2.line(frame, meio, (meio[0], 0), (255, 0, 0), 2)
    cv2.putText(frame, f"{int(dados['angulo_ombro'])}°", 
                (meio[0]-50, meio[1]-20), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (255, 0, 0), 2)
    
    # Ângulo do pescoço
    cv2.line(frame, pts['orelha_esq'], pts['ombro_esq'], (0, 255, 0), 2)
    cv2.line(frame, pts['ombro_esq'], (pts['ombro_esq'][0], 0), (0, 255, 0), 2)
    cv2.putText(frame, f"{int(dados['angulo_pescoco'])}°", 
                (pts['ombro_esq'][0]-50, pts['ombro_esq'][1]-40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)