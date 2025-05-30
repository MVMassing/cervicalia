import cv2
import mediapipe as mp
import numpy as np
import time
from playsound import playsound
import os

mp_pose = mp.solutions.pose
mp_desenho = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

alerta = "assets/alert.wav"

calibrado = False
quadros_calibracao = 0
calibracao_angulo_ombro = []
calibracao_angulo_pescoco = []
ultimo_alerta = 0
tempo_alerta = 10
tempo_minimo_postura_ruim = 3
tempo_postura_ruim_iniciado = None

def calcular_angulo(ponto1, ponto2, ponto3):
    angulo = np.arctan2(ponto3[1] - ponto2[1], ponto3[0] - ponto2[0]) - np.arctan2(ponto1[1] - ponto2[1], ponto1[0] - ponto2[0])
    return np.abs(angulo * 180.0 / np.pi)

def desenhar_angulo(frame, ponto1, ponto2, ponto3, angulo, cor):
    cv2.line(frame, ponto1, ponto2, cor, 3)
    cv2.line(frame, ponto2, ponto3, cor, 3)
    cv2.putText(frame, str(int(angulo)), (ponto2[0] - 50, ponto2[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2, cv2.LINE_AA)

def feedback_postura(angulo_ombro, limite_ombro_min, limite_ombro_max, angulo_pescoco, limite_pescoco_min, limite_pescoco_max):
    global tempo_postura_ruim_iniciado, ultimo_alerta
    tempo_atual = time.time()
    
    if angulo_ombro < limite_ombro_min or angulo_ombro > limite_ombro_max or angulo_pescoco < limite_pescoco_min or angulo_pescoco > limite_pescoco_max:
        status = "Postura Ruim"
        cor = (0, 0, 255)
        
        if tempo_postura_ruim_iniciado is None:
            tempo_postura_ruim_iniciado = tempo_atual
        elif tempo_atual - tempo_postura_ruim_iniciado >= tempo_minimo_postura_ruim:
            if tempo_atual - ultimo_alerta > tempo_alerta:
                print("Postura ruim detectada!")
                if os.path.exists(alerta):
                    playsound(alerta) 
                ultimo_alerta = tempo_atual
    else:
        status = "Postura Boa"
        cor = (0, 255, 0) 
        tempo_postura_ruim_iniciado = None

    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2, cv2.LINE_AA)
    cv2.putText(frame, f"Ombro: {angulo_ombro:.1f}/{limite_ombro_min:.1f}-{limite_ombro_max:.1f}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, f"Pescoco: {angulo_pescoco:.1f}/{limite_pescoco_min:.1f}-{limite_pescoco_max:.1f}", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    quadro_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = pose.process(quadro_rgb)

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

        angulo_ombro = calcular_angulo(ombro_esquerdo, ombro_direito, (ombro_direito[0], 0))
        angulo_pescoco = calcular_angulo(orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0))

        if not calibrado and quadros_calibracao < 30:
            calibracao_angulo_ombro.append(angulo_ombro)
            calibracao_angulo_pescoco.append(angulo_pescoco)
            quadros_calibracao += 1
            cv2.putText(frame, f"Calibrando... {quadros_calibracao}/30", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        elif not calibrado:
            margem = 5 
            limite_ombro_min = np.mean(calibracao_angulo_ombro) - margem
            limite_ombro_max = np.mean(calibracao_angulo_ombro) + margem
            limite_pescoco_min = np.mean(calibracao_angulo_pescoco) - margem
            limite_pescoco_max = np.mean(calibracao_angulo_pescoco) + margem
            calibrado = True
            print(f"Calibração concluída. Limite Ombro: {limite_ombro_min:.1f}-{limite_ombro_max:.1f}, Limite Pescoço: {limite_pescoco_min:.1f}-{limite_pescoco_max:.1f}")

        mp_desenho.draw_landmarks(frame, resultados.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        meio = ((ombro_esquerdo[0] + ombro_direito[0]) // 2, (ombro_esquerdo[1] + ombro_direito[1]) // 2)
        desenhar_angulo(frame, ombro_esquerdo, meio, (meio[0], 0), angulo_ombro, (255, 0, 0))
        desenhar_angulo(frame, orelha_esquerda, ombro_esquerdo, (ombro_esquerdo[0], 0), angulo_pescoco, (0, 255, 0))

        if calibrado:
            feedback_postura(angulo_ombro, limite_ombro_min, limite_ombro_max, angulo_pescoco, limite_pescoco_min, limite_pescoco_max)

    cv2.imshow("Cervicalia", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
