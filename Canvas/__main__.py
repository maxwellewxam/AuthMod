import tkinter as tk
import queue
import threading
import time
from func_timeout import func_timeout, FunctionTimedOut
class MainGui:
    def __init__(self, master, worker, height, width):
        self.start = worker.start
        self.stop = worker.stop
        self.queue = worker.queue
        self.worker = worker
        self.master = master
        self.master.geometry(f'{width}x{height}')
        self.master.title('3D Render')
        self.canvas = tk.Canvas(self.master, width = width, height = height, bg = 'white')
        self.canvas.bind('<Map>', self.start)
        self.canvas.bind('<Destroy>', self.stop)
        self.canvas.grid(row = 0, column = 0)
        self.tagdict = {}
    def processIncoming(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get()
                if msg[0] not in self.tagdict.keys():
                    if msg[2] == 1:
                        id = self.canvas.create_line(msg[1][0], msg[1][1], fill = 'black')
                        self.tagdict[msg[0]] = id
                    if msg[2] == 2:
                        id = self.canvas.create_polygon(msg[1][0], msg[1][1], msg[1][2], fill = 'black')
                        self.tagdict[msg[0]] = id
                else:
                    self.canvas.coords(self.tagdict[msg[0]], *msg[1][0], *msg[1][1])
            except:
                pass
class ThreadedClient:
    def __init__(self, master, shape, height, width):
        self.master = master
        self.shape = shape
        self.started = False
        self.queue = queue.Queue(maxsize = 1)
        self.gui = MainGui(master, self, height, width)
    def workerThread1(self):
        try:
            self.queue.put([1,self.shape.lines])
            self.gui.processIncoming()
        except:
            pass
        try:
            self.queue.put([2,self.shape.triangle])
            self.gui.processIncoming()
        except:
            pass
        self.run = self.shape(self)
        prev_time = time.time()
        t = threading.current_thread()
        while getattr(t, "do_run", True):
            try:
                func_timeout(2,self.run.Main)
            except FunctionTimedOut as err:
                print(err)
            curr_time = time.time()
            diff = curr_time - prev_time
            delay = max(1.0/144 - diff, 0)
            time.sleep(delay)
            prev_time = curr_time
    def start(self, event = None):
        self.thread1 = threading.Thread(target = self.workerThread1, name = 'WorkerThread')
        self.thread1.start()
    def stop(self, event = None):
        self.thread1.do_run = False
    def line(self, pos, tag1):
        self.queue.put([tag1, pos, 1])
        self.gui.processIncoming()
    def triangle(self, pos, tag1):
        self.queue.put([tag1, pos, 2])
        self.gui.processIncoming()
class Canvas:
    def __init__(self, Handler, Height = 500, Width = 500):
        root = tk.Tk()
        client = ThreadedClient(root, Handler, Height, Width)
        root.mainloop()
        client.stop()
        