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
        logger_sync = logging.getLogger("bibbox-sync")
        logger_sync.setLevel(logging.ERROR)
        # create a file handler
        handler_sync = logging.FileHandler('/opt/log/bibbox-sync.log')
        handler_sync.setLevel(logging.ERROR)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler_sync.setFormatter(formatter)
        # add the handlers to the logger
        logger_sync.addHandler(handler_sync)
        print("EVENT: " + event.event_type + " " + str(event.is_directory) + " " + event.src_path)
        logger_sync.info("BIBBOXFileHandler EVENT: " + event.event_type + " " + str(event.is_directory) + " " + event.src_path)
        file = SyncFile(event.event_type, event.is_directory, event.src_path)
        q.put(file)

def do_stuff(q):
  while True:
    logger.info("XXX")
    file = q.get()
    if(file.UpdateIndex()):
        q.task_done()
        logger.info("File Updated")
        print("File Updated")
    else:
        print("ERROR")
        logger.info("ERROR")
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
    logger.info("-------------------------------")
    logger.info("- Startign BIBBOX Sync Script -")
    logger.info("-     " + str(time.strftime("%d-%m.%Y %I:%M:%S")) + "     -")
    logger.info("-------------------------------")
    logger.info("")
    
    logger.info("Starting Thread: do_stuff")
    num_threads = 1
    q.join()
    for i in range(num_threads):
        worker = Thread(target=do_stuff, args=(q,))
        worker.setDaemon(True)
        worker.start()

    path = os.environ['SYNC_PATH']
    logger.info("Read existing Files from path: " + path)
    #TODO Delete index if files not existing eny more
    onlyfiles = get_filepaths(path)
    for file in onlyfiles:
        logger.info("INIT Sync for file: " + file)
        file_1 = SyncFile("created", False, file)
        q.put(file_1)

    logger.info("Start Event Handler Listener for path: " + path)
    event_handler = BIBBOXFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
