from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta

from ..entities.posture_data import PostureData
from ..entities.posture_calibration import PostureCalibration
from ..entities.statistics import PostureStatistics


class PostureRepository(ABC):
    
    @abstractmethod
    def save_posture_data(self, posture_data: PostureData) -> None:
        pass
    
    @abstractmethod
    def get_posture_data_by_date_range(self, start_date: datetime, end_date: datetime) -> List[PostureData]:
        pass
    
    @abstractmethod
    def get_statistics(self) -> PostureStatistics:
        pass
    
    @abstractmethod
    def save_calibration(self, calibration: PostureCalibration) -> None:
        pass
    
    @abstractmethod
    def get_calibration(self, camera_type: str) -> Optional[PostureCalibration]:
        pass
    
    @abstractmethod
    def save_setting(self, key: str, value: str) -> None:
        pass
    
    @abstractmethod
    def get_setting(self, key: str, default: str = "") -> str:
        pass 