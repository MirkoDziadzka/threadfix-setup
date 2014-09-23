
"""
Interface to the ThreadFix REST api
"""

#from Constants import THREADFIX_WAF_NAME
#from BaseClass import BaseClass
THREADFIX_WAF_NAME = "SteelApp Web App Firewall"
BaseClass=object

import sys
import os
import pprint
import simplejson
import requests
import glob

import unittest

class HttpError(Exception):
    pass
class RestError(Exception):
    pass


class Threadfix(BaseClass):
    def __init__(self, api_prefix, api_key):
        BaseClass.__init__(self)
        self.__api_prefix = api_prefix
        self.__api_key = api_key

    def get_url(self, *url):
        path = "/".join([self.__api_prefix] + list(url))
        r = requests.get(path, params = {'apiKey' :  self.__api_key}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object')

    def get_waf_list(self):
        res = []
        try:
            waf_list = self.get_url("wafs")
            print waf_list
            return ('',sorted([(waf.get('id'),waf.get('name')) for waf in waf_list if waf.get('wafTypeName','') == THREADFIX_WAF_NAME ]))
        except Exception,e:
            return (str(e),'')

    def get_waf_ruleset(self, waf_id):
        try:
            res = self.get_url("wafs",str(waf_id),"rules","app", "-1")
            return simplejson.loads(res)
        except Exception as e:
            return {'error' : str(e)}

    def get_waf_rules(self, waf_id):
        res = self.get_waf_ruleset(waf_id)
        if 'error' in res:
            return (res['error'], [])
        try:
            rules = []
            for r in res['rules']:
                if r:
                    rules.append(r)
            return ('', rules)
        except Exception as e:
            return (str(e), [])

    def get_team_by_name(self, name):
        path = path = "/".join((self.__api_prefix, 'teams', 'lookup'))
        r = requests.get(path, params = {'apiKey' :  self.__api_key, 'name' : name}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        #print result
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def create_team(self, name):
        try:
            return self.get_team_by_name(name)
        except RestError as e:
            pass
        path = path = "/".join((self.__api_prefix, 'teams', 'new'))
        r = requests.post(path, params = {'apiKey' :  self.__api_key, 'name' : name}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def get_application_by_name(self, team_name, app_name):
        team_id = self.get_team_by_name(team_name)
        path = path = "/".join((self.__api_prefix, 'applications', team_name,'lookup'))
        r = requests.get(path, params = {'apiKey' :  self.__api_key, 'name' : app_name}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def create_application(self, team_name, app_name):
        try:
            return self.get_application_by_name(team_name, app_name)
        except RestError as e:
            print 'error', e
        team_id = self.create_team(team_name)
        path = path = "/".join((self.__api_prefix, 'teams', str(team_id), 'applications', 'new'))
        r = requests.post(path, params = {'apiKey' :  self.__api_key, 'name' : app_name}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def set_waf(self, app_id, waf_id):
        path = path = "/".join((self.__api_prefix, 'applications', str(app_id), 'setWaf'))
        r = requests.post(path, params = {'apiKey' :  self.__api_key, 'wafId' : str(waf_id)}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def get_waf_by_name(self, name):
        path = path = "/".join((self.__api_prefix, 'wafs', 'lookup'))
        r = requests.get(path, params = {'apiKey' :  self.__api_key, 'name' : name}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def create_waf(self, name, waf_type = THREADFIX_WAF_NAME):
        try:
            return self.get_waf_by_name(name)
        except RestError as e:
            print 'error', e
        path = path = "/".join((self.__api_prefix, 'wafs', 'new'))
        r = requests.post(path, params = {'apiKey' :  self.__api_key, 'name' : name, 'type' : waf_type}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return result.get('object', {}).get('id')

    def upload_scan(self, app_id, filename):
        scan = open(filename,"rb").read()
        path = path = "/".join((self.__api_prefix, 'applications', str(app_id), 'upload'))
        r = requests.post(path, params = {'apiKey' :  self.__api_key}, files = {'file' : scan}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return 'OK'

    def upload_waf_log(self, waf_id, filename):
        logdata = open(filename, "r").read()
        path = path = "/".join((self.__api_prefix, 'wafs', str(waf_id), 'uploadLog'))
        r = requests.post(path, params = {'apiKey' :  self.__api_key}, files = {'file' : logdata}, headers = {'Accept': 'application/json'}, auth = lambda x : x, verify = False)
        if r.status_code != 200:
            raise HttpError(r.status_code)
        result = r.json()
        if not result.get('success', False):
            raise RestError(result.get("message", result))
        return 'OK'







if __name__ == '__main__':
    API_KEY = sys.argv[1] # '1euJTr7bcGQmEo2RsPGoRMOLd6S0ufOIDIL6R3rUgFo'
    BASE_URL = 'https://localhost:8443/threadfix/rest'
    t = Threadfix(BASE_URL, API_KEY)
    #print t.get_waf_list()
    #print t.get("wafs/1")
    #print t.get("wafs/1/rules/app/-1")
    #print t.get_waf_rules(2)
    app_id =  t.create_application("test-team", "test-app")
    app_id =  t.create_application("test-team", "test-app2")
    app_id =  t.create_application("test-team", "test-app3")
    app_id =  t.create_application("test-team2", "test-app4")
    waf_id =  t.create_waf("test-waf", waf_type = "Snort")
    waf_id =  t.create_waf("test-waf1")
    assert t.set_waf(app_id, waf_id) == app_id
    #print t.get_url("wafs")
    for filename in glob.glob(os.path.join('Threadfix', 'test-scans', '*.xml')):
        try:
            print 'uploading', filename
            t.upload_scan(app_id, filename)
        except RestError as e:
            print 'error while uploading', filename, e
    res, waf_rules = t.get_waf_rules(waf_id)
    assert not res, res
    assert len(waf_rules) >= 33, len(waf_rules)
    waf_ruleset = t.get_waf_ruleset(waf_id)
    simplejson.dump(waf_ruleset, open("waf_rules.json", "w"), sort_keys = True, indent = 4)
    #pprint.pprint(waf_rules)
    print t.upload_waf_log(waf_id,"example-waf-log.csv")


