import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from ...domain.entities.posture_calibration import PostureCalibration


@dataclass
class PostureAnalysisResult:
    shoulder_angle: float
    neck_angle: float
    is_calibrating: bool
    calibration_frames: int
    is_poor_posture: bool
    calibration_data: Optional[PostureCalibration] = None


class PostureAnalysisService:
    
    def __init__(self, camera_type: str = "frontal"):
        self.camera_type = camera_type
        
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.is_calibrated = False
        self.calibration_frames = 0
        self.calibration_shoulder_angles = []
        self.calibration_neck_angles = []
        
        self.shoulder_angle_min = 0
        self.shoulder_angle_max = 0
        self.neck_angle_min = 0
        self.neck_angle_max = 0
        
        self.margin = 5.0
        self.minimum_poor_posture_time = 3.0
        self.poor_posture_start_time = None
        self.last_analysis_result = None
    
    def calculate_angle(self, point1: Tuple[int, int], 
                       point2: Tuple[int, int], 
                       point3: Tuple[int, int]) -> float:
        angle = np.arctan2(point3[1] - point2[1], point3[0] - point2[0]) - \
                np.arctan2(point1[1] - point2[1], point1[0] - point2[0])
        return np.abs(angle * 180.0 / np.pi)
    
    def draw_angle(self, frame: np.ndarray, point1: Tuple[int, int], 
                  point2: Tuple[int, int], point3: Tuple[int, int], 
                  angle: float, color: Tuple[int, int, int]) -> None:
        cv2.line(frame, point1, point2, color, 3)
        cv2.line(frame, point2, point3, color, 3)
        cv2.putText(frame, str(int(angle)), (point2[0] - 50, point2[1] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[PostureAnalysisResult]]:
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)
            annotated_frame = frame.copy()
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                left_shoulder = (int(landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1]),
                               int(landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]))
                right_shoulder = (int(landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1]),
                                int(landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]))
                left_ear = (int(landmarks[mp.solutions.pose.PoseLandmark.LEFT_EAR.value].x * frame.shape[1]),
                           int(landmarks[mp.solutions.pose.PoseLandmark.LEFT_EAR.value].y * frame.shape[0]))
                right_ear = (int(landmarks[mp.solutions.pose.PoseLandmark.RIGHT_EAR.value].x * frame.shape[1]),
                            int(landmarks[mp.solutions.pose.PoseLandmark.RIGHT_EAR.value].y * frame.shape[0]))
                
                shoulder_angle = self.calculate_angle(left_shoulder, right_shoulder, (right_shoulder[0], 0))
                neck_angle = self.calculate_angle(left_ear, left_shoulder, (left_shoulder[0], 0))
                
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated_frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
                )
                
                if not self.is_calibrated and self.calibration_frames < 30:
                    self.calibration_shoulder_angles.append(shoulder_angle)
                    self.calibration_neck_angles.append(neck_angle)
                    self.calibration_frames += 1
                    
                    cv2.putText(annotated_frame, f"Calibrating... {self.calibration_frames}/30",
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
                    
                    result = PostureAnalysisResult(
                        shoulder_angle=shoulder_angle,
                        neck_angle=neck_angle,
                        is_calibrating=True,
                        calibration_frames=self.calibration_frames,
                        is_poor_posture=False
                    )
                    self.last_analysis_result = result
                    return annotated_frame, result
                
                elif not self.is_calibrated:
                    self.shoulder_angle_min = np.mean(self.calibration_shoulder_angles) - self.margin
                    self.shoulder_angle_max = np.mean(self.calibration_shoulder_angles) + self.margin
                    self.neck_angle_min = np.mean(self.calibration_neck_angles) - self.margin
                    self.neck_angle_max = np.mean(self.calibration_neck_angles) + self.margin
                    self.is_calibrated = True
                    
                    print(f"Calibração {self.camera_type} concluída.")
                    print(f"Limites do ombro: {self.shoulder_angle_min:.1f}-{self.shoulder_angle_max:.1f}")
                    print(f"Limites do pescoço: {self.neck_angle_min:.1f}-{self.neck_angle_max:.1f}")
                
                shoulder_center = ((left_shoulder[0] + right_shoulder[0]) // 2,
                                 (left_shoulder[1] + right_shoulder[1]) // 2)
                
                if self.camera_type == "frontal":
                    self.draw_angle(annotated_frame, left_shoulder, shoulder_center, 
                                  (shoulder_center[0], 0), shoulder_angle, (255, 0, 0))
                    self.draw_angle(annotated_frame, left_ear, left_shoulder,
                                  (left_shoulder[0], 0), neck_angle, (0, 255, 0))
                else:
                    self.draw_angle(annotated_frame, left_ear, left_shoulder,
                                  (left_shoulder[0], 0), neck_angle, (0, 255, 0))
                
                is_poor_posture = False
                if self.is_calibrated:
                    if self.camera_type == "frontal":
                        is_poor_posture = (shoulder_angle < self.shoulder_angle_min or 
                                         shoulder_angle > self.shoulder_angle_max or
                                         neck_angle < self.neck_angle_min or 
                                         neck_angle > self.neck_angle_max)
                    else:
                        is_poor_posture = (neck_angle < self.neck_angle_min or 
                                         neck_angle > self.neck_angle_max)
                    
                    self.draw_feedback(annotated_frame, shoulder_angle, neck_angle, is_poor_posture)
                
                calibration_data = None
                if self.is_calibrated:
                    calibration_data = PostureCalibration(
                        camera_type=self.camera_type,
                        shoulder_angle_min=self.shoulder_angle_min,
                        shoulder_angle_max=self.shoulder_angle_max,
                        neck_angle_min=self.neck_angle_min,
                        neck_angle_max=self.neck_angle_max,
                        margin=self.margin
                    )
                
                result = PostureAnalysisResult(
                    shoulder_angle=shoulder_angle,
                    neck_angle=neck_angle,
                    is_calibrating=False,
                    calibration_frames=self.calibration_frames,
                    is_poor_posture=is_poor_posture,
                    calibration_data=calibration_data
                )
                self.last_analysis_result = result
                return annotated_frame, result
            
            self.last_analysis_result = None
            return frame, None
            
        except Exception as e:
            print(f"Erro ao processar frame {self.camera_type}: {e}")
            self.last_analysis_result = None
            return frame, None
    
    def draw_feedback(self, frame: np.ndarray, shoulder_angle: float, 
                     neck_angle: float, is_poor_posture: bool) -> None:
        try:
            if is_poor_posture:
                status = "Postura Ruim"
                color = (0, 0, 255)
            else:
                status = "Postura Boa"
                color = (0, 255, 0)
            
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            
            if self.camera_type == "frontal":
                cv2.putText(frame, f"Ombro: {shoulder_angle:.1f}°", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(frame, f"Pescoço: {neck_angle:.1f}°", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(frame, f"Cervical: {neck_angle:.1f}°", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                
        except Exception as e:
            print(f"Erro ao desenhar feedback: {e}")
    
    def reset_calibration(self) -> None:
        self.is_calibrated = False
        self.calibration_frames = 0
        self.calibration_shoulder_angles = []
        self.calibration_neck_angles = []
        self.shoulder_angle_min = 0
        self.shoulder_angle_max = 0
        self.neck_angle_min = 0
        self.neck_angle_max = 0
        self.last_analysis_result = None
    
    def get_last_result(self) -> Optional[PostureAnalysisResult]:
        return self.last_analysis_result
    
    def __del__(self):
        if hasattr(self, 'pose'):
            self.pose.close() 