import unittest
from build_status import BuildStatus

class TestBuildStatus(unittest.TestCase):

    def test_get_invalid(self):
        (msg, color) = BuildStatus.fromMessage({})
        self.assertIsNot(msg, '')

    def test_get_valid(self):
        (msg, color) = BuildStatus.fromMessage({ 'attributes': 
                                            {
                                             'buildId': '123',
                                             'status' : 'SUCCESS'
                                            }
                                     })
        self.assertEqual(msg, '123 : Build finished successfully')
        self.assertEqual(color, BuildStatus.SUCCESS)
        
