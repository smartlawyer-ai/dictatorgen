from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess 
import time

class Watcher(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command

    def on_any_event(self, event):
        print(f"Change detected: {event.src_path}")
        subprocess.run(self.command, shell=True)

def main():
    path_to_watch = "./dictatorgenai"  # Répertoire à surveiller
    command = "poetry run python dictatorgenai/examples/dictator_chainlit_example.py"  # Commande à exécuter en cas de modification
    event_handler = Watcher(command)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=True)
    observer.start()
    print(f"Watching for changes in {path_to_watch}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
