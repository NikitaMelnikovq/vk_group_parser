import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_changed = False

    def on_modified(self, event):
        if event.is_directory:
            return
        self.file_changed = True

def file_changed(file_path):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while True:
            if event_handler.file_changed:
                observer.stop()
                return True
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    return False

# if __name__ == "__main__":
#     path_to_watch = "data.json"
#     while True:
#         if file_changed(path_to_watch):
#             print("File has been modified")
#         else:
#             print("File has not been modified")