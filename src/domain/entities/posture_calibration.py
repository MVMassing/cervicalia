from dataclasses import dataclass
from typing import List


@dataclass
class PostureCalibration:
    camera_type: str
    shoulder_angle_min: float
    shoulder_angle_max: float
    neck_angle_min: float
    neck_angle_max: float
    margin: float = 5.0
    
    def is_within_shoulder_range(self, angle: float) -> bool:
        return self.shoulder_angle_min <= angle <= self.shoulder_angle_max
    
    def is_within_neck_range(self, angle: float) -> bool:
        return self.neck_angle_min <= angle <= self.neck_angle_max
    
    def is_good_posture(self, shoulder_angle: float, neck_angle: float) -> bool:
        return (self.is_within_shoulder_range(shoulder_angle) and 
                self.is_within_neck_range(neck_angle)) 