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

###################################
# DOCU:
# Filde/Folder watcher:
# http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html

###################################
# Define Variables
# Queue for running in the Task scheduler
q = queue.Queue(maxsize=0)
# Define Logger
loglevel = os.environ['LOGGER_LEVEL']
logger = logging.getLogger("bibbox-sync")
if loglevel == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)
handler = logging.FileHandler('/opt/log/bibbox-sync.log')
if loglevel == "DEBUG":
    handler.setLevel(logging.DEBUG)
else:
    handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
###################################
# File watcher handler class
class BIBBOXFileHandler(FileSystemEventHandler):
    #on_modified
    #on_created
    #on_moved
    #on_deleted

    def on_any_event(self, event):
        if event.is_directory == False:
            logger.info("BIBBOXFileHandler EVENT: " + event.event_type + " - " + str(event.is_directory) + " - " + event.src_path)
            file = SyncFile(event.event_type, event.is_directory, event.src_path)
            q.put(file)

###################################
# Thread Worker to update files in the Queue
def threadWorker(q):
  while True:
    logger.debug("threadWorker...")
    try:
        file = q.get()
        if file.getCounter() > 10:
            q.task_done()
            file = q.get()
        if file.isFolder():
            q.task_done()
            file = q.get()
        if(file.updateIndex()):
            logger.info("File Updated: " + file.getFileInfo())
            q.task_done()
        else:
            logger.error("ERROR updating file: " + file.getFileInfo())
            time.sleep(30)
    except Exception as ex:
        logger.error("Error handling threadWorker: " + file.getFileInfo())
        logger.error("Error handling threadWorker: " + str(ex))

###################################
# Helper fuction to get all files in a path
def get_filepaths(path):
    file_paths = []
    for root, directories, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

###################################
# Main Fuction
if __name__ == "__main__":
    logger.info("-------------------------------")
    logger.info("- Startign BIBBOX Sync Script -")
    logger.info("-     " + str(time.strftime("%d-%m.%Y %I:%M:%S")) + "     -")
    logger.info("-------------------------------")
    logger.info("")

    logger.debug("Startign Threads...")
    num_threads = 1
    q.join()
    for i in range(num_threads):
        worker = Thread(target=threadWorker, args=(q,))
        worker.setDaemon(True)
        worker.start()
    logger.debug("Startign Threads... done")

    path = os.environ['SYNC_PATH']
    logger.debug("Read existing Files from path: " + path)
    #TODO Delete index if files not existing eny more
    onlyfiles = get_filepaths(path)
    for file in onlyfiles:
        logger.debug("INIT Sync for file: " + file)
        file_object = SyncFile("created", False, file)
        if file_object.isFolder() == False:
            logger.debug("Created Object: " + file_object.getFileInfo())
            q.put(file_object)

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
    logger.info("End Event Handler Listener")
