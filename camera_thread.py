import cv2
import queue
from threading import Thread, Event
import time

class CameraThread(Thread):
    def __init__(self, source):
        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=1) 
        self.source = source
        self.resolution = (320, 240) 
        self.fps = 15 
        self.running = True
        self.stop_event = Event()
        self.cap = None
        self.frame_time = 1.0 / self.fps
        self.last_frame_time = 0

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                print(f"Erro: Não foi possível abrir a câmera {self.source}")
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            if isinstance(self.source, str) and self.source.startswith('http'):
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            consecutive_failures = 0
            max_failures = 10
            
            while self.running and not self.stop_event.is_set():
                current_time = time.time()
                
                if current_time - self.last_frame_time < self.frame_time:
                    time.sleep(0.001) 
                    continue
                
                ret, frame = self.cap.read()
                
                if ret:
                    consecutive_failures = 0
                    
                    if frame.shape[:2] != self.resolution[::-1]:
                        frame = cv2.resize(frame, self.resolution)
                    
                    if self.queue.full():
                        try:
                            self.queue.get_nowait()
                        except queue.Empty:
                            pass
                    
                    try:
                        self.queue.put_nowait(frame)
                        self.last_frame_time = current_time
                    except queue.Full:
                        pass 
                        
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        print(f"Muitas falhas consecutivas na câmera {self.source}")
                        break
                    
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"Erro na thread da câmera {self.source}: {e}")
        finally:
            self.cleanup()

    def get_frame(self):
        try:
            return self.queue.get_nowait() if not self.queue.empty() else None
        except queue.Empty:
            return None

    def get_latest_frame(self):
        latest_frame = None
        try:
            while not self.queue.empty():
                latest_frame = self.queue.get_nowait()
        except queue.Empty:
            pass
        return latest_frame

    def stop(self):
        self.running = False
        self.stop_event.set()
        if self.is_alive():
            self.join(timeout=2.0) 
        self.cleanup()

    def cleanup(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def is_connected(self):
        return self.cap is not None and self.cap.isOpened()

    def get_fps(self):
        return self.fps

    def set_fps(self, fps):
        self.fps = max(1, min(fps, 30))
        self.frame_time = 1.0 / self.fps
        if self.cap:
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

    def __del__(self):
        self.cleanup()