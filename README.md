URL shortener API
======
A Python 3 RESTful API for URL shortening using the flask microframework

Requires
-----
  * flask
  * records
  * validators
  * hashids
  * user-agents
  * urlparse

Install dependencies by
-----
```
pip install flask records validators hashids pyyaml ua-parser user-agents urlparse
```

Run Service
-----
```
python urlShortner.py
```

Using Web Service
-----

| HTTP Method | URI                                                                    | Action                                                      |
|-------------|------------------------------------------------------------------------|-------------------------------------------------------------|
| GET         | http://[hostname]/                                                     | Retrieve the list of all the urls that exists in the system |
| POST        | http://[hostname]/ parameters: - desktop_url - mobile_url - tablet_url | Create a short URL                                          |
| GET         | http://[short_url]                                                     | Redirect to target URL depending on the device              |
| POST        | http://[short_url] parameters: - desktop_url - mobile_url - tablet_url | Update short URL                                            |

Run Tests
-----
```
python urlShortner_test.py
```

