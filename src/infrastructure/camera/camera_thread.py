import cv2
import queue
from threading import Thread, Event
import time

class CameraThread(Thread):
    def __init__(self, source):
        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=2)
        self.source = source
        self.running = True
        self.cap = None
        self.connected = False

    def run(self):
        try:
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                print(f"Erro: Não foi possível abrir a câmera {self.source}")
                return
            
            self.connected = True
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            while self.running:
                ret, frame = self.cap.read()
                
                if ret:
                    if self.queue.full():
                        try:
                            self.queue.get_nowait()
                        except queue.Empty:
                            pass
                    
                    try:
                        self.queue.put_nowait(frame)
                    except queue.Full:
                        pass
                else:
                    time.sleep(0.01)
                    
        except Exception as e:
            print(f"Erro na thread da câmera {self.source}: {e}")
            self.connected = False
        finally:
            self.cleanup()

    def is_connected(self):
        return self.connected and self.cap is not None and self.cap.isOpened()

    def get_frame(self):
        try:
            return self.queue.get_nowait() if not self.queue.empty() else None
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
        if self.is_alive():
            self.join(timeout=1.0)
        self.cleanup()

    def cleanup(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.connected = False

    def __del__(self):
        self.cleanup() 