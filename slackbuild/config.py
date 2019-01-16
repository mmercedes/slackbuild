import yaml
import os

class Config:

    def __init__(self, filename='./config.yaml', config_override=None):
        if config_override is None:
            f = open(filename)
            self.__data = yaml.load(f.read())
            f.close()
        else:
            self.__data = config_override

        if self.__data.get('slack', {}).get('token', '') is '':
            if self.__data.get('slack', None) is None:
                self.__data['slack'] = {}
            self.__data['slack']['token'] = os.environ.get('SLACK_TOKEN', '')
            self.__data['slack']['signing_secret'] = os.environ.get('SLACK_SIGNING_SECRET', '')

    def get(self, value, default=None):
        assert type(value) is type("")
        return self.__data.get(value, default)
