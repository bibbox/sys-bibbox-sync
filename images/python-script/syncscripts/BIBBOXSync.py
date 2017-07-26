import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
import queue
from threading import Thread
from SyncFile import SyncFile
import os

#DOCU:
#http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html

q = queue.Queue(maxsize=0)
path = "/opt/bibbox/sys-bibbox-sync/data"

logger = logging.getLogger("bibbox-sync")
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('/opt/log/bibbox-sync.log')
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

class BIBBOXFileHandler(FileSystemEventHandler):
    #on_modified
    #on_created
    #on_moved
    #on_deleted

    def on_any_event(self, event):
        print("EVENT: " + event.event_type + " " + str(event.is_directory) + " " + event.src_path)
        file = SyncFile(event.event_type, event.is_directory, event.src_path)
        q.put(file)

def do_stuff(q):
  while True:
    file = q.get()
    if(file.UpdateIndex()):
        q.task_done()
        print("File Updated")
    else:
        print("ERROR")
        time.sleep(30)

def get_filepaths(path):
    file_paths = []
    for root, directories, files in os.walk(path):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths

if __name__ == "__main__":

    elasticBaseURL = os.environ['DEBUSSY']
    print("Test: " + elasticBaseURL)
    logger.info("Test: " + elasticBaseURL)
    
    num_threads = 1

    for i in range(num_threads):
        worker = Thread(target=do_stuff, args=(q,))
        worker.setDaemon(True)
        worker.start()

    q.join()

    #TODO Delete index if files not existing eny more
    onlyfiles = get_filepaths(path)
    for file in onlyfiles:
        file = SyncFile("created", False, file)
        q.put(file)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = BIBBOXFileHandler()
    #event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
