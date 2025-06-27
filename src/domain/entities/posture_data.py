from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PostureData:
    shoulder_angle: float
    neck_angle: float
    camera_type: str
    timestamp: datetime
    is_poor_posture: bool = False
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now() 