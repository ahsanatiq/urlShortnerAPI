import json
import logging
import os
import unittest
from urllib.parse import urlparse

import urlShortner

class UrlShortnerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.app = urlShortner.app.test_client()
        self.app.testing = True
        urlShortner.app.config['DATABASE'] = os.path.join(urlShortner.app.root_path, 'urlShortner_test.db')
        urlShortner.tableCheck()

    def tearDown(self):
        pass

    def test_empty_list(self):
        urlShortner.tableEmpty()
        result = self.app.get('/')
        self.assertTrue(b'no urls found' in result.data)
        self.assertEqual(result.status_code,200)

    def test_create_url_with_empty_desktop_url(self):
        result = self.app.post('/')
        self.assertTrue(b'parameter desktop_url required' in result.data)
        self.assertEqual(400, result.status_code)

    def test_create_url_with_invalid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='httpgooglecom'))
        self.assertTrue(b'invalid desktop_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_invalid_desktop_url2(self):
        result = self.app.post('/', data=dict(desktop_url='www.google.com'))
        self.assertTrue(b'invalid desktop_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_desktop_url2(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_desktop_url3(self):
        result = self.app.post('/', data=dict(desktop_url='https://www.google.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_mobile_url_and_without_desktop_url(self):
        result = self.app.post('/', data=dict(mobile_url='http://www.google.com.au'))
        self.assertTrue(b'parameter desktop_url required' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_invalid_mobile_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='wwwyahoocom'))
        self.assertTrue(b'invalid mobile_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_invalid_mobile_url_and_valid_desktop_url2(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='wwwy.ahoo.com'))
        self.assertTrue(b'invalid mobile_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_valid_mobile_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='http://www.yahoo.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_mobile_url_and_valid_desktop_url2(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='https://www.yahoo.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_tablet_url_and_without_desktop_url(self):
        result = self.app.post('/', data=dict(tablet_url='http://www.google.com.au'))
        self.assertTrue(b'parameter desktop_url required' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_valid_tablet_url_and_valid_mobile_url_and_without_desktop_url(self):
        result = self.app.post('/', data=dict(mobile_url='http://www.yahoo.com', tablet_url='http://www.google.com.au'))
        self.assertTrue(b'parameter desktop_url required' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_invalid_tablet_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', tablet_url='wwwyahoocom'))
        self.assertTrue(b'invalid tablet_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_invalid_tablet_url_and_valid_desktop_url2(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', tablet_url='wwwy.ahoo.com'))
        self.assertTrue(b'invalid tablet_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_valid_tablet_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', tablet_url='http://www.yahoo.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_tablet_url_and_valid_desktop_url2(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', tablet_url='https://www.yahoo.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_valid_mobile_url_with_valid_tablet_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='https://www.yahoo.com', tablet_url='https://www.apple.com'))
        self.assertTrue(b'short_url' in result.data)
        self.assertEqual(result.status_code, 200)

    def test_create_url_with_invalid_mobile_url_with_valid_tablet_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='https://wwwyahoo', tablet_url='https://www.apple.com'))
        self.assertTrue(b'invalid mobile_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_create_url_with_valid_mobile_url_with_invalid_tablet_url_and_valid_desktop_url(self):
        result = self.app.post('/', data=dict(desktop_url='http://www.google.com.au', mobile_url='https://www.yahoo.com', tablet_url='https/www.applecom'))
        self.assertTrue(b'invalid tablet_url format' in result.data)
        self.assertEqual(result.status_code, 400)

    def test_url_list(self):
        urlShortner.tableEmpty()
        rv = self.submit_url()
        result = self.app.get('/')
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(len(result_json),1)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result_json[0]['desktop_url'], 'http://www.google.com.au')
        self.assertEqual(result_json[0]['mobile_url'], 'https://www.yahoo.com')
        self.assertEqual(result_json[0]['tablet_url'], 'https://www.apple.com')

        rv = self.submit_url()
        result = self.app.get('/')
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(len(result_json), 2)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result_json[1]['desktop_url'],'http://www.google.com.au')
        self.assertEqual(result_json[1]['mobile_url'], 'https://www.yahoo.com')
        self.assertEqual(result_json[1]['tablet_url'], 'https://www.apple.com')

    def test_update_url(self):
        urlShortner.tableEmpty()
        rv = self.submit_url()
        rv_json = json.loads(rv.get_data(as_text=True))
        short_url_parsed = urlparse(rv_json['short_url'])
        result = self.app.post(short_url_parsed.path,data=dict(desktop_url='http://www.python.com'))
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(len(result_json), 8)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result_json['desktop_url'], 'http://www.python.com')
        self.assertEqual(result_json['mobile_url'], 'https://www.yahoo.com')
        self.assertEqual(result_json['tablet_url'], 'https://www.apple.com')

        result = self.app.post(short_url_parsed.path, data=dict(desktop_url='http://www.python.org', mobile_url='http://flask.pocoo.org/'))
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(len(result_json), 8)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result_json['desktop_url'], 'http://www.python.org')
        self.assertEqual(result_json['mobile_url'], 'http://flask.pocoo.org/')
        self.assertEqual(result_json['tablet_url'], 'https://www.apple.com')

        result = self.app.post(short_url_parsed.path,
                               data=dict(tablet_url='https://docs.python.org/3.4'))
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(len(result_json), 8)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result_json['desktop_url'], 'http://www.python.org')
        self.assertEqual(result_json['mobile_url'], 'http://flask.pocoo.org/')
        self.assertEqual(result_json['tablet_url'], 'https://docs.python.org/3.4')

    def test_url_redirect_desktop(self):
        rv = self.submit_url()
        rv_json = json.loads(rv.get_data(as_text=True))
        short_url_parsed = urlparse(rv_json['short_url'])
        result = self.app.get(short_url_parsed.path)
        self.assertTrue(b'google' in result.data)

    def test_url_redirect_mobile(self):
        rv = self.submit_url()
        rv_json = json.loads(rv.get_data(as_text=True))
        short_url_parsed = urlparse(rv_json['short_url'])
        result = self.app.get(short_url_parsed.path,headers={'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'})
        self.assertTrue(b'yahoo' in result.data)

    def test_url_redirect_tablet(self):
        rv = self.submit_url()
        rv_json = json.loads(rv.get_data(as_text=True))
        short_url_parsed = urlparse(rv_json['short_url'])
        result = self.app.get(short_url_parsed.path,headers={'User-Agent': 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'})
        self.assertTrue(b'apple' in result.data)

    def test_url_counter(self):
        rv = self.submit_url()
        rv_json = json.loads(rv.get_data(as_text=True))
        short_url_parsed = urlparse(rv_json['short_url'])

        result = self.app.get(short_url_parsed.path)
        self.assertTrue(b'google' in result.data)
        result = self.app.post(short_url_parsed.path)
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_json['desktop_counter'], 1)

        result = self.app.get(short_url_parsed.path)
        self.assertTrue(b'google' in result.data)
        result = self.app.post(short_url_parsed.path)
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_json['desktop_counter'], 2)

        result = self.app.get(short_url_parsed.path, headers={'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'})
        self.assertTrue(b'yahoo' in result.data)
        result = self.app.post(short_url_parsed.path)
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_json['mobile_counter'], 1)

        result = self.app.get(short_url_parsed.path, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'})
        self.assertTrue(b'yahoo' in result.data)
        result = self.app.post(short_url_parsed.path)
        result_json = json.loads(result.get_data(as_text=True))
        self.assertEqual(result_json['mobile_counter'], 2)

    def submit_url(self):
        return self.app.post('/', data=dict(
            desktop_url='http://www.google.com.au',
            mobile_url='https://www.yahoo.com',
            tablet_url='https://www.apple.com'))

if __name__ == '__main__':
    unittest.main()