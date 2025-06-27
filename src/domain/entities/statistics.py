from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class PostureStatistics:
    total_occurrences: int
    today_occurrences: int
    frontal_camera_count: int
    lateral_camera_count: int
    last_occurrence: datetime
    daily_occurrences: Dict[str, int]
    camera_distribution: Dict[str, int]
    weekly_trend: Dict[str, int]
    
    @classmethod
    def create_empty(cls) -> 'PostureStatistics':
        return cls(
            total_occurrences=0,
            today_occurrences=0,
            frontal_camera_count=0,
            lateral_camera_count=0,
            last_occurrence=datetime.now(),
            daily_occurrences={},
            camera_distribution={},
            weekly_trend={}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_occurrences': self.total_occurrences,
            'today_occurrences': self.today_occurrences,
            'frontal_camera_count': self.frontal_camera_count,
            'lateral_camera_count': self.lateral_camera_count,
            'last_occurrence': self.last_occurrence.isoformat(),
            'daily_occurrences': self.daily_occurrences,
            'camera_distribution': self.camera_distribution,
            'weekly_trend': self.weekly_trend
        } 