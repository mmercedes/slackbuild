import unittest
from config import Config

class TestConfig(unittest.TestCase):

    def test_config_valid(self):
        # has all required fields and nothing else
        config = {
            'slack_channel' : '#test',
            'slack_token'   : 'test',
        }
        conf = Config(config_override=config)
        self.assertEqual(conf.get('slack_token'), 'test')

    def test_config_missing_required(self):
        # missing all required fields
        config = {
            'foo' : 'bar'
        }
        conf = Config(config_override=config)
        self.assertEqual(conf.get('foo'), 'bar')
        
    def test_config_extra(self):
        # has unnecessary extra field
        config = {
            'slack_channel' : '#test',
            'slack_token'   : 'test',
            'foo'           : 'bar'
        }
        conf = Config(config_override=config)
        self.assertEqual(conf.get('foo'), 'bar')
        self.assertEqual(conf.get('slack_token'), 'test')

    def test_config_example(self):
        # check the example config works
        configfile = './config.json.example'

        conf = Config(filename=configfile)
        self.assertEqual(conf.get('slack_channel'), '#test')
