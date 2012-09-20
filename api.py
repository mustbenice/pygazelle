#!/usr/bin/env python
# Makes use of / builds on the API implementation from 'whatbetter', by Zachary Denton
# See https://github.com/zacharydenton/whatbetter

import re
import os
import json
import time
import requests
import HTMLParser
from cStringIO import StringIO

from user import User
#from artist import Artist
#from torrent import Torrent

class LoginException(Exception):
    pass

class RequestException(Exception):
    pass

class GazelleAPI(object):
    default_headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3)'\
                      'AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79'\
                      'Safari/535.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'\
                  ',*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}


    def __init__(self, username=None, password=None):
        self.session = requests.session(headers=self.default_headers)
        self.username = username
        self.password = password
        self.authkey = None
        self.passkey = None
        self.userid = None
        self.logged_in_user = None
        self.site = "http://what.cd/"
        self.last_request = time.time()
        self.rate_limit = 2.0 # seconds between requests
        self._login()

    def _login(self):
        """
        Private method.
        Logs in user and gets authkey from server.
        """
        loginpage = 'https://what.cd/login.php'
        data = {'username': self.username,
                'password': self.password}
        r = self.session.post(loginpage, data=data)
        if r.status_code != 200:
            raise LoginException
        accountinfo = self.request('index')
        self.userid = accountinfo['id']
        self.authkey = accountinfo['authkey']
        self.passkey = accountinfo['passkey']
        self.logged_in_user = User(self.userid, self)
        self.logged_in_user.set_index_data(accountinfo)

    def request(self, action, **kwargs):
        """
        Makes an AJAX request at a given action page.
        Pass an action and relevant arguments for that action.
        """
        while time.time() - self.last_request < self.rate_limit:
            time.sleep(0.1)

        ajaxpage = 'https://what.cd/ajax.php'
        params = {'action': action}
        if self.authkey:
            params['auth'] = self.authkey
        params.update(kwargs)
        r = self.session.get(ajaxpage, params=params, allow_redirects=False)
        self.last_request = time.time()
        try:
            parsed = json.loads(r.content)
            if parsed['status'] != 'success':
                raise RequestException
            return parsed['response']
        except ValueError:
            raise RequestException

    def get_user(self, id):
        """
        Returns a user for the passed ID, associated with this API object. If the ID references the currently logged in
        user, the user returned will be pre-populated with the information from an 'index' API call. Otherwise, you'll
        need to call User.update_user_data(). This is done on demand to reduce unnecessary API calls.
        """
        id = int(id)
        if id == self.userid:
            return self.logged_in_user
        else:
            return User(id, self)

    def search_users(self, search_query):
        """
        Returns a list of users returned for the search query. You can search by name, part of name, and ID number. If
        one of the returned users is the currently logged-in user, that user object will be pre-populated with the
        information from an 'index' API call. Otherwise only the limited info returned by the search will be pre-pop'd.
        You can query more information with User.update_user_data(). This is done on demand to reduce unnecessary API calls.
        """
        response = self.request(action='usersearch', search=search_query)
        results = response['results']

        found_users = []
        for result in results:
            user = User(result['userId'], self)
            user.set_search_result_data(result)
            found_users.append(user)

        return found_users
