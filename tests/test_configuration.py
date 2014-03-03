""" Tests for jtime configuration module. """
import base64
import httpretty
import mock
import os
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from jtime import configuration
from jtime import custom_exceptions
from jtime import jtime


class JtimeConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.config_file_path = os.path.abspath('.jtime.ini')
        self._config_patch = mock.patch('jtime.configuration._config',
                                        self.config_file_path)
        self._config_patch.start()

    def tearDown(self):
        self._config_patch.stop()

        # Delete the configuration file if we've created it
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)

    @httpretty.activate
    def test__save_config(self):
        httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com')
        configuration._save_config('jira.atlassian.com', '', '')

        assert os.path.exists(self.config_file_path)

    @mock.patch('urllib.urlopen', side_effect=IOError)
    def test__save_config_url_not_found(self, patch):
        with self.assertRaises(SystemExit):
            configuration._save_config('url', '', '')

    @httpretty.activate
    def test_load_config(self):
        httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com', status=200)
        jira_url = 'jira.atlassian.com'
        username = 'test_user'
        password = 'test_pass'
        configuration._save_config(jira_url, username, password)
        config_dict = configuration.load_config()

        assert username == config_dict.get('jira').get('username')
        assert base64.b64encode(password) == config_dict.get('jira').get('password')

    def test_load_config__NotConfigured(self):
        with self.assertRaises(custom_exceptions.NotConfigured):
            configuration.load_config()

    @httpretty.activate
    @mock.patch('jtime.utils.get_input', side_effect=['jira.atlassian.com', 'user', 'pass'])
    def test_jtime_configure(self, input):
        httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com', status=200)
        jtime.configure()

    def test__save_cookie(self):
        configuration._save_cookie('test', 'cookie')

        assert os.path.exists(self.config_file_path)

    def test__get_cookies_as_dict(self):
        cookie_name = 'test'
        cookie_value = 'cookie'
        configuration._save_cookie(cookie_name, cookie_value)
        cookie_dict = configuration._get_cookies_as_dict()

        self.assertEquals(cookie_dict.get(cookie_name), cookie_value)
