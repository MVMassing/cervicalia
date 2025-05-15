import cv2
import queue
from threading import Thread

class CameraThread(Thread):
    def __init__(self, source):
        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=2)
        self.source = source
        self.running = True

    def run(self):
        # Configuração otimizada para streams HTTP
        cap = cv2.VideoCapture(self.source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                if self.queue.full():
                    self.queue.get_nowait()
                self.queue.put(frame)

    def get_frame(self):
        return self.queue.get() if not self.queue.empty() else None