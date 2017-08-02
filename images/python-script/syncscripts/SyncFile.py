#DOCU:
#https://github.com/elastic/elasticsearch-x-pack-py
#https://elasticsearch-py.readthedocs.io/en/master/

from datetime import datetime
import json
import requests
import logging
import os
#from elasticsearch import Elasticsearch
#from elasticsearch_xpack import XPackClient

class SyncFile:
    def __init__(self, event_type, is_directory, src_path):
        
        self.logger = logging.getLogger("bibbox-sync")
        self.logger.setLevel(logging.DEBUG)
        # create a file handler
        handler = logging.FileHandler('/opt/log/bibbox-sync.log')
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        self.logger.addHandler(handler)
        
        self.logger.info("--------------------------------")
        self.logger.info("SyncFile")
        
        self.event_type = event_type
        self.is_directory = is_directory
        self.src_path = src_path
        self.elasticBaseURL = os.environ['ELASTIC_BASE_URL']
        self.logger.info('SyncFile - elasticBaseURL: ' + self.elasticBaseURL)
        self.headersEL = {'Content-type': 'application/json', 'Accept': 'text/plain'}    
        
    def UpdateIndex(self):
        print(self.event_type + ' - ' + self.src_path)
        self.logger.info("UpdateIndex: " + self.event_type + ' - ' + self.src_path)

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
        self.logger.info("data" + data)
        privacy = json.load(data["privacy"])
        self.logger.info("privacy" + privacy)
        if privacy["share"] == 'yes':
            self.logger.info("share" + "TRUE")
            return True
        else:
            self.logger.info("share" + "FALSE")
            return False    
    
    def modifiIndex(self):
        self.logger.info("SyncFile::modifiIndex")
        with open(self.src_path) as data_file:
            self.logger.info("data_file: " + data_file)
            self.data = json.load(data_file)
        if self.checkPrivacy(self.data):
            re = requests.put(self.elasticBaseURL + self.getIdentifier(), data=json.dumps(self.data), headers=self.headersEL)
            print("mod" + re.text)
            self.logger.info("mod" + re.text)
            return self.getInstructioncode(re.status_code)
        else:
            return self.deleteIndex()

    def creatIndex(self):
        self.logger.info("SyncFile::creatIndex")
        with open(self.src_path) as data_file:
            self.data = json.load(data_file)
        self.logger.info("data" + self.data)
        if self.checkPrivacy(self.data):
            re = requests.put(self.elasticBaseURL + self.getIdentifier(), data=json.dumps(self.data["_source"]), headers=self.headersEL)
            print(re.text)
            self.logger.info("mod" + re.text)
            return self.getInstructioncode(re.status_code)
        else:
            return self.deleteIndex()

    def moveIndex(self):
        return self.modifiIndex()

    def deleteIndex(self):
        self.logger.info("SyncFile::deleteIndex")
        re = requests.delete(self.elasticBaseURL + self.getIdentifier())
        print(re.text)
        self.logger.info("mod" + re.text)
        return self.getInstructioncode(re.status_code)

    def getIdentifier(self):
        self.logger.info("SyncFile::getIdentifier")
        elemets = self.src_path.split("\\")
        counter = 3
        id = ''
        for element in reversed(elemets):
            if counter > 0:
                id = element + "/" + id
                counter -=1
        return id.replace(".json/", "")

    def getInstructioncode(self, code):
        self.logger.info("SyncFile::getInstructioncode" + str(code))
        print(code)
        self.logger.info("code: " + code)
        if code == 200 or code == 201 or code == 202 or code == 203 or code == 204:
            return True
        return False
