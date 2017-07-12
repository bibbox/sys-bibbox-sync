#DOCU:
#https://github.com/elastic/elasticsearch-x-pack-py
#https://elasticsearch-py.readthedocs.io/en/master/

from datetime import datetime
import json
import requests
from elasticsearch import Elasticsearch
#from elasticsearch_xpack import XPackClient

class SyncFile:
    def __init__(self, event_type, is_directory, src_path):
        self.event_type = event_type
        self.is_directory = is_directory
        self.src_path = src_path
        self.elasticBaseURL = "http://elastic-el.demo.bibbox.org/"
        self.headersEL = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def UpdateIndex(self):
        print(self.event_type + ' - ' + self.src_path)

        if self.is_directory == False:
            if(self.event_type == 'modified'):
                return self.modifiIndex()
            if (self.event_type == 'created'):
                return self.creatIndex()
            if (self.event_type == 'moved'):
                return self.moveIndex()
            if (self.event_type == 'deleted'):
                return self.deleteIndex()

        sampleDescription='{"author": "kimchy","text": "a12344"}'

        #print(self.data)

        #print(re.status_code)
        #print(re.text)

        # IF Successfule updatet remove from queue
        return False

    def modifiIndex(self):
        with open(self.src_path) as data_file:
            self.data = json.load(data_file)
        re = requests.put(
            self.elasticBaseURL + self.getIdentifier(),
            data=json.dumps(self.data["_source"]), headers=self.headersEL)
        print("mod" + re.text)
        return self.getInstructioncode(re.status_code)

    def creatIndex(self):
        with open(self.src_path) as data_file:
            self.data = json.load(data_file)
        re = requests.put(self.elasticBaseURL + self.getIdentifier(), data=json.dumps(self.data["_source"]), headers=self.headersEL)
        print(re.text)
        return self.getInstructioncode(re.status_code)

    def moveIndex(self):
        return self.modifiIndex()

    def deleteIndex(self):
        re = requests.delete(self.elasticBaseURL + self.getIdentifier())
        print(re.text)
        return self.getInstructioncode(re.status_code)

    def getIdentifier(self):
        elemets = self.src_path.split("\\")
        counter = 3
        id = ''
        for element in reversed(elemets):
            if counter > 0:
                id = element + "/" + id
                counter -=1
        return id.replace(".json/", "")

    def getInstructioncode(self, code):
        print(code)
        if code == 200 or code == 201 or code == 202 or code == 203 or code == 204:
            return True
        return False