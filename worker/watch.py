 bank-ml-mvp/worker/watch.py
import time, subprocess, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

STATEMENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "statements"))

class NewPDFHandler(FileSystemEventHandler):
    def on_created(self, event):
         Only act on files, not directories
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            print(f"[watcher] Detected new PDF: {event.src_path}")
             Launch parse job in background
            subprocess.Popen(["python", "worker/parse.py", event.src_path])

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(NewPDFHandler(), path=STATEMENTS_DIR, recursive=False)
    observer.start()
    print(f"[watcher] Watching {STATEMENTS_DIR} for new PDFs…")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
