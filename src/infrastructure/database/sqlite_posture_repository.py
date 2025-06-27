import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

from ...domain.entities.posture_data import PostureData
from ...domain.entities.posture_calibration import PostureCalibration
from ...domain.entities.statistics import PostureStatistics
from ...domain.repositories.posture_repository import PostureRepository

class SQLitePostureRepository(PostureRepository):
    def __init__(self, db_path: str = 'posture_data.db'):
        self.db_path = db_path
        self._init_db()
        self._migrate_database()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS posture_records
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT NOT NULL,
                      shoulder_angle REAL,
                      neck_angle REAL NOT NULL,
                      camera_type TEXT NOT NULL,
                      is_poor_posture INTEGER DEFAULT 0)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS app_settings
                     (key TEXT PRIMARY KEY,
                      value TEXT NOT NULL)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS calibration
                     (camera_type TEXT PRIMARY KEY,
                      shoulder_angle_min REAL,
                      shoulder_angle_max REAL,
                      neck_angle_min REAL,
                      neck_angle_max REAL,
                      margin REAL)''')
        
        conn.commit()
        conn.close()

    def _migrate_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("PRAGMA table_info(posture_records)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'camera' in columns and 'camera_type' not in columns:
                print("Migrando esquema do banco de dados...")
                
                c.execute("ALTER TABLE posture_records ADD COLUMN camera_type TEXT")
                c.execute("ALTER TABLE posture_records ADD COLUMN shoulder_angle REAL")
                c.execute("ALTER TABLE posture_records ADD COLUMN neck_angle REAL")
                c.execute("ALTER TABLE posture_records ADD COLUMN is_poor_posture INTEGER DEFAULT 0")
                
                c.execute("UPDATE posture_records SET camera_type = camera")
                c.execute("UPDATE posture_records SET shoulder_angle = angulo_ombro")
                c.execute("UPDATE posture_records SET neck_angle = angulo_pescoco")
                c.execute("UPDATE posture_records SET is_poor_posture = 1 WHERE angulo_ombro IS NOT NULL OR angulo_pescoco IS NOT NULL")
                
                c.execute("CREATE TABLE posture_records_new AS SELECT id, timestamp, shoulder_angle, neck_angle, camera_type, is_poor_posture FROM posture_records")
                c.execute("DROP TABLE posture_records")
                c.execute("ALTER TABLE posture_records_new RENAME TO posture_records")
                
                print("Migração do banco de dados concluída com sucesso")
                
        except Exception as e:
            print(f"Erro na migração (isso é normal para bancos novos): {e}")
        
        conn.commit()
        conn.close()

    def save_posture_data(self, posture_data: PostureData) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO posture_records (timestamp, shoulder_angle, neck_angle, camera_type, is_poor_posture) VALUES (?, ?, ?, ?, ?)",
                  (posture_data.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   posture_data.shoulder_angle,
                   posture_data.neck_angle,
                   posture_data.camera_type,
                   int(posture_data.is_poor_posture)))
        conn.commit()
        conn.close()

    def get_posture_data_by_date_range(self, start_date: datetime, end_date: datetime) -> List[PostureData]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, timestamp, shoulder_angle, neck_angle, camera_type, is_poor_posture FROM posture_records WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp",
                  (start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")))
        rows = c.fetchall()
        conn.close()
        return [PostureData(
            id=row[0],
            timestamp=datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"),
            shoulder_angle=row[2],
            neck_angle=row[3],
            camera_type=row[4],
            is_poor_posture=bool(row[5])
        ) for row in rows]

    def get_statistics(self) -> PostureStatistics:
        conn = sqlite3.connect(self.db_path)
        
        try:
            c = conn.cursor()
            c.execute("PRAGMA table_info(posture_records)")
            columns = [column[1] for column in c.fetchall()]
            
            if 'camera_type' not in columns:
                df = pd.read_sql_query("SELECT * FROM posture_records ORDER BY timestamp", conn)
                if not df.empty and 'camera' in df.columns:
                    df = df.rename(columns={
                        'camera': 'camera_type',
                        'angulo_ombro': 'shoulder_angle',
                        'angulo_pescoco': 'neck_angle'
                    })
                    if 'is_poor_posture' not in df.columns:
                        df['is_poor_posture'] = True
                else:
                    df = pd.DataFrame()
            else:
                df = pd.read_sql_query("SELECT * FROM posture_records ORDER BY timestamp", conn)
        except Exception as e:
            print(f"Erro ao ler estatísticas: {e}")
            df = pd.DataFrame()
        
        conn.close()
        
        if df.empty:
            return PostureStatistics.create_empty()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        today = datetime.now().date()
        week_ago = today - timedelta(days=6)
        
        df_week = df[df['date'] >= week_ago]
        daily_counts = df_week.groupby('date').size().to_dict()
        
        daily_occurrences = {date.isoformat(): count for date, count in daily_counts.items()}
        
        camera_distribution = df['camera_type'].value_counts().to_dict()
        
        df['week'] = df['timestamp'].dt.isocalendar().week
        df['year'] = df['timestamp'].dt.year
        df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
        weekly_counts = df.groupby('year_week').size().to_dict()
        
        total_occurrences = len(df)
        today_occurrences = len(df[df['date'] == today])
        frontal_camera_count = len(df[df['camera_type'] == 'frontal'])
        lateral_camera_count = len(df[df['camera_type'] == 'lateral'])
        last_occurrence = df['timestamp'].max().to_pydatetime()
        
        return PostureStatistics(
            total_occurrences=total_occurrences,
            today_occurrences=today_occurrences,
            frontal_camera_count=frontal_camera_count,
            lateral_camera_count=lateral_camera_count,
            last_occurrence=last_occurrence,
            daily_occurrences=daily_occurrences,
            camera_distribution=camera_distribution,
            weekly_trend=weekly_counts
        )

    def save_calibration(self, calibration: PostureCalibration) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO calibration (camera_type, shoulder_angle_min, shoulder_angle_max, neck_angle_min, neck_angle_max, margin) VALUES (?, ?, ?, ?, ?, ?)",
                  (calibration.camera_type, calibration.shoulder_angle_min, calibration.shoulder_angle_max, calibration.neck_angle_min, calibration.neck_angle_max, calibration.margin))
        conn.commit()
        conn.close()

    def get_calibration(self, camera_type: str) -> Optional[PostureCalibration]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT camera_type, shoulder_angle_min, shoulder_angle_max, neck_angle_min, neck_angle_max, margin FROM calibration WHERE camera_type = ?", (camera_type,))
        row = c.fetchone()
        conn.close()
        if row:
            return PostureCalibration(
                camera_type=row[0],
                shoulder_angle_min=row[1],
                shoulder_angle_max=row[2],
                neck_angle_min=row[3],
                neck_angle_max=row[4],
                margin=row[5]
            )
        return None

    def save_setting(self, key: str, value: str) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

    def get_setting(self, key: str, default: str = "") -> str:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default 