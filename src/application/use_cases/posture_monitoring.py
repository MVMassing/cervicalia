from datetime import datetime
from typing import Optional

from ...domain.entities.posture_data import PostureData
from ...domain.entities.posture_calibration import PostureCalibration
from ...domain.entities.statistics import PostureStatistics
from ...domain.repositories.posture_repository import PostureRepository

class PostureMonitoringUseCase:
    
    def __init__(self, repository: PostureRepository):
        self.repository = repository
    
    def process_posture_frame(self, shoulder_angle: float, neck_angle: float, 
                            camera_type: str, calibration_data: Optional[PostureCalibration] = None) -> None:
        if calibration_data:
            is_poor_posture = not calibration_data.is_good_posture(shoulder_angle, neck_angle)
        else:
            is_poor_posture = True
        
        posture_data = PostureData(
            shoulder_angle=shoulder_angle,
            neck_angle=neck_angle,
            camera_type=camera_type,
            timestamp=datetime.now(),
            is_poor_posture=is_poor_posture
        )
        
        self.repository.save_posture_data(posture_data)
    
    def get_statistics(self) -> PostureStatistics:
        return self.repository.get_statistics()
    
    def save_calibration(self, calibration: PostureCalibration) -> None:
        self.repository.save_calibration(calibration)
    
    def get_calibration(self, camera_type: str) -> Optional[PostureCalibration]:
        return self.repository.get_calibration(camera_type) 