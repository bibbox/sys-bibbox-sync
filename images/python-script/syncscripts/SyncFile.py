#DOCU:
#https://github.com/elastic/elasticsearch-x-pack-py
#https://elasticsearch-py.readthedocs.io/en/master/

from datetime import datetime
import json
import requests
import logging
import os

class SyncFile:
    def __init__(self, event_type, is_directory, src_path):
        self.logger = logging.getLogger("bibbox-sync")

        self.logger.debug("class SyncFile: event_type: " + event_type + ", is_directory: " + str(is_directory) + ", src_path: " + src_path )
        
        self.event_type = event_type
        self.is_directory = is_directory
        self.src_path = src_path
        self.elasticBaseURL = os.environ['ELASTIC_BASE_URL']
        self.logger.debug('SyncFile - elasticBaseURL: ' + self.elasticBaseURL)
        self.headersEL = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def isFolder(self):
        return self.is_directory

    def getFileInfo(self):
        file_info = "SyncFile: event_type: " + self.event_type + ", is_directory: " + str(self.is_directory) + ", src_path: " + self.src_path
        return file_info

    def updateIndex(self):
        self.logger.debug("UpdateIndex: " + self.event_type + ' - ' + self.src_path)
        if self.is_directory == False:
            if(self.event_type == 'modified'):
                return self.modifiIndex()
            if (self.event_type == 'created'):
                return self.creatIndex()
            if (self.event_type == 'moved'):
                return self.moveIndex()
            if (self.event_type == 'deleted'):
                return self.deleteIndex()
        return False

    def checkPrivacy(self, data):
        self.logger.debug("SyncFile::checkPrivacy")
        privacy = data["privacy"]
        self.logger.debug("SyncFile::checkPrivacy" + privacy)
        if privacy["share"] == 'yes':
            self.logger.debug("share" + "TRUE")
            return True
        else:
            self.logger.debug("share" + "FALSE")
            return False    
    
    def modifiIndex(self):
        self.logger.debug("SyncFile::modifiIndex")
        with open(self.src_path) as data_file:
            self.data = json.load(data_file)
        if self.checkPrivacy(self.data):
            re = requests.put(self.elasticBaseURL + self.getIdentifier(), data=json.dumps(self.data), headers=self.headersEL)
            self.logger.debug("mod" + re.text)
            return self.getInstructioncode(re.status_code)
        else:
            self.logger.debug("Sharing is disabled.")
            return self.deleteIndex()

    def creatIndex(self):
        self.logger.debug("SyncFile::creatIndex: " + self.src_path)
        try:
            with open(self.src_path) as data_file:
                self.logger.debug("SyncFile::readJson: " + data_file.read())
                self.data = json.load(data_file)
        except Exception as e:  # parent of IOError, OSError *and* WindowsError where available
            self.logger.error("Error handling file: " + self.src_path)
            self.logger.error("Error handling file: " + str(e))
        self.logger.debug("Read file done")
        if self.checkPrivacy(self.data):
            re = requests.put(self.elasticBaseURL + self.getIdentifier(), data=json.dumps(self.data), headers=self.headersEL)
            self.logger.debug("mod" + re.text)
            return self.getInstructioncode(re.status_code)
        else:
            self.logger.debug("Sharing is disabled.")
            return self.deleteIndex()

    def moveIndex(self):
        return self.modifiIndex()

    def deleteIndex(self):
        self.logger.debug("SyncFile::deleteIndex")
        re = requests.delete(self.elasticBaseURL + self.getIdentifier())
        self.logger.debug("mod" + re.text)
        self.logger.debug("Sharing is disabled.")
        return self.getInstructioncode(re.status_code)

    def getIdentifier(self):
        self.logger.debug("SyncFile::getIdentifier")
        elemets = self.src_path.split("/")
        counter = 3
        id = ''
        for element in reversed(elemets):
            if counter > 0:
                id = element + "/" + id
                counter -=1
        return id.replace(".json/", "")

    def getInstructioncode(self, code):
        self.logger.debug("SyncFile::getInstructioncode" + str(code))
        self.logger.debug("code: " + str(code))
        if code == 200 or code == 201 or code == 202 or code == 203 or code == 204:
            return True
        return False
