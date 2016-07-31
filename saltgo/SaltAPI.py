#!/usr/bin/python
# coding: utf8


from django.conf import settings
import urllib2
import urllib
import json


class SaltAPI(object):
    def __init__(self):
        self.__token = ''
#        self.__url = settings.SALT_API_URL
#        __user = settings.SALT_API_USER
#        __passwd = settings.SALT_API_PASSWD
        self.__url = 'http://172.16.23.154:8000'
        __user = 'admin'
        __passwd = 'admin'
        obj = {'eauth': 'pam', 'username': __user, 'password': __passwd}
        context = self.post_request(obj, '/login')
        try:
            self.__token = context['return'][0]['token']
        except KeyError:
            raise KeyError

    def post_request(self, obj, prefix='/'):
        url = self.__url + prefix
        headler = {'X-Auth-Token': self.__token}
        obj = urllib.urlencode(obj)
        req = urllib2.Request(url, obj, headler)
        opener = urllib2.urlopen(req)
        context = json.loads(opener.read())
        return context

    def get_request(self, prefix='/'):
        url = self.__url + prefix
        headler = {'X-Auth-Token': self.__token}
        req = urllib2.Request(url, headers=headler)
        opener = urllib2.urlopen(req)
        context = json.loads(opener.read())
        return context

    def cmd_async(self, tgt, fun, arg=(), expr_form='glob'):
        obj = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': expr_form}
        context = self.post_request(obj)
        ret = context['return'][0]
        return ret

    def shell_cmd(self, tgt, arg, expr_form='glob'):
        fun = 'cmd.run'
        ret = self.cmd_async(tgt, fun, arg, expr_form)
        return ret

    def execute_state(self, tgt, sls, expr_form='glob'):
        fun = 'state.sls'
        ret = self.cmd_async(tgt, fun, sls, expr_form)
        return ret

    def execute_highstate(self, tgt, expr_form='glob'):
        fun = 'state.highstate'
        ret = self.cmd_async(tgt, fun, expr_form=expr_form)
        return ret

    def jobs_lookup(self, jid):
        obj = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        context = self.post_request(obj)
        ret = context.get('return')[0]
        return ret

    def runner_sync(self, fun):
        obj = {'client': 'runner', 'fun': fun}
        context = self.post_request(obj)
        ret = context.get('return')[0]
        return ret

    def wheel_key_list(self):
        obj = {'client': 'wheel', 'fun': 'key.list_all'}
        context = self.post_request(obj)
        ret = context.get('return')[0]
        return ret

    def file_find_sync(self, tgt, path, expr_form='glob'):
        obj = {'client': 'local', 'fun': 'file.find', 'tgt': tgt, 'arg': path, 'expr_form': expr_form}
        context = self.post_request(obj)
        ret = context.get('return')[0]
        return ret

if __name__ == '__main__':
    c = SaltAPI()
    print c.jobs_lookup('20160730161804299812')
