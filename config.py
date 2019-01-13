import json
import os

class Config:

    def __init__(self, filename='./config.json', config_override=None):
        if config_override is None:
            f = open(filename)
            self.__data = json.load(f)
            f.close()
        else:
            self.__data = config_override

        if self.__data.get('slack_token', '') is '':
            self.__data['slack_token'] = os.environ.get('SLACK_TOKEN', '')

    def get(self, value):
        assert type(value) is type("")
        return self.__data[value]
