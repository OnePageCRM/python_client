#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''\
Connect and interface with the OnePageCRM REST API using the OnePageCRMAPI
class.\
'''

import sys
from time import time
import requests
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
from requests.utils import quote

import re
IDENTIFIER_REGEX = re.compile('^[a-z_][a-z0-9_]+$', re.I)

if sys.version_info.major > 2:
    iteritems = dict.items
    isidentifier = str.isidentifier
else:
    import keyword
    iteritems = dict.iteritems

    def isidentifier(i):
        '''Check if a scring is a valid python2 identifier'''
        ident = str(i)
        return IDENTIFIER_REGEX.match(ident) and ident not in keyword.kwlist

try:
    import json
except ImportError:
    import simplejson as json


class OnePageCRMAPI(object):
    '''\
    Wrapper to allow requests to be made in a simple and structured manner.
    Use your UserId and API key and then you will be authenticated for any request.
    '''

    BASE_URL = 'https://app.onepagecrm.com/api/v3/'
    DEFAULT_RESPONSE_TYPE = 'dict'

    def __init__(self,
                 user_id=None,
                 api_key=None,
                 base_url=None,
                 response_type=None):
        '''\
        Initializes the OnePageAPI object and authenticates
        with the OnePageCRM API.\
        '''
        self.base_url = self.BASE_URL
        self.response_type = self.DEFAULT_RESPONSE_TYPE
        if base_url:
            self.base_url = str(base_url)
        if response_type:
            self.response_type = str(response_type)
        if self.base_url[-1] == '/':
            self.base_url = self.base_url[:-1]
        self.user_id = user_id
        self.api_key = api_key
        self.lead_sources = {}
        self.statuses = {}
        self.team_stream = {}
        self.contact_counts = {}
        self.tags = {}
        if self.user_id and self.api_key:
            self.request('GET', 'bootstrap')

    def headers(self, method, url, request_body=None):
        '''\
        Build necessary headers for communicating with OnePageCRM\
        '''

        return {'X-OnePageCRM-UID': self.user_id,
                'X-OnePageCRM-Source': 'python_client',
                'Content-Type': 'application/json',
                'accept': 'application/json'}

    def url(self, resource_name, resource_id=None, sub_resource=None,
            sub_resource_id=None, **kwargs):
        '''\
        Build a request url from path fragments and query parameters

        :returns: str\
        '''
        path = (self.base_url, resource_name, resource_id,
                sub_resource, sub_resource_id)
        url = '/'.join(p for p in path if p) + '.json'
        if kwargs:
            url += '?' + '&'.join(quote(str(k)) + '=' + quote(str(v))
                                  for k, v in iteritems(kwargs))
        return url

    def request(self, method, resource_name, resource_id=None,
                sub_resource=None, sub_resource_id=None,
                resource=None, **kwargs):
        '''\
        Make a HTTP request to the OnePageCRM API

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        url = self.url(resource_name, resource_id, sub_resource,
                       sub_resource_id, **kwargs)
        body = None
        if method in {'PUT', 'POST'}:
            if resource:
                try:
                    body = resource.to_dict()
                except AttributeError:
                    body = dict(resource)
            else:
                body = {}
            body = json.dumps(body)
        headers = self.headers(method, url, body)
        response = requests.request(method, url, headers=headers, auth=HTTPBasicAuth(self.user_id, self.api_key), data=body)
        return self._handle_response(response)

    def _handle_response(self, response):
        '''\
        Handle errors and response formatting. Store bootstrap data to keep it
        up to date

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        status = response.status_code
        try:
            response_data = response.json()
        except ValueError:
            response_data = {}
        if self.response_type == 'object':
            response_data = ResponseDict.from_dict(response_data)
        if 400 <= status < 500:
            message = (response_data.get('error_message') or
                       response_data.get('message') or
                       'No error message was returned contact the developers '
                       'at forum.developer.onepagecrm.com for more help')
            raise RequestError(message, status, response_data)
        elif status >= 500:
            data = {}
            if self.response_type == 'object':
                data = ResponseDict.from_dict({})
            raise UnknownError('An unknown error has occurred. '
                               'Please inform our dev team of this issue at '
                               'forum.developer.onepagecrm.com and provide '
                               'details of how you triggered this error.',
                               status,
                               data)
        self._save_additional_data(response_data)
        try:
            return response_data['data']
        except KeyError:
            return response_data

    def _save_additional_data(self, data):
        '''\
        Store additional bootstrap data within the client\
        '''
        d = {}
        keys = ('sales', 'lead_sources', 'statuses', 'team_stream',
                'contacts_count', 'tags')
        for key in keys:
            try:
                d[key] = data[key]
            except (KeyError, AttributeError):
                d[key] = None
        if d['sales']:
            self.sales = d['sales']
        if d['lead_sources']:
            self.lead_sources = ['lead_sources']
        if d['statuses']:
            self.statuses = d['statuses']
        if d['team_stream']:
            self.team_stream = d['team_stream']
        if d['contacts_count']:
            self.contact_counts = d['contacts_count']
        if d['tags']:
            self.tags = d['tags']

    def get(self, resource_name, resource_id=None,
            sub_resource=None, sub_resource_id=None, **kwargs):
        '''\
        Make a get request to the OnePageCRM API

        Examples:
        >>> client = OnePageCRMAPI(user_id, api_key)
        >>> contacts = client.get('contacts')['contacts']
        >>> contact_id = contacts[0]['contact']['id']
        >>> contact = client.get('contacts', contact_id)['contact']
        >>> notes = client.get('contacts', contact_id, 'notes')
        >>> # Filtering
        >>> contacts = client.get('contacts', modified_since='2014-06-20')
        >>> contacts = client.get('contacts', starred=True)

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        return self.request('GET', resource_name, resource_id, sub_resource,
                            sub_resource_id, **kwargs)

    def post(self, resource_name, resource, **kwargs):
        '''\
        Make a post to the OnePageCRM API

        Examples:
        >>> client = OnePageCRMAPI(user_id, api_key)
        >>> contact = client.post('contacts', {'company_name': 'OnePageCRM'})['contact']
        >>> contact_id = contact['id']
        >>> client.post('notes', {'text': 'Met with him at the expo',
                                  'contact_id': contact_id})

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        return self.request('POST', resource_name, resource=resource, **kwargs)

    def put(self, resource_name, resource_id, resource, **kwargs):
        '''\
        Update a resource on OnePageCRM

        Examples:
        >>> client = OnePageCRMAPI(user_id, api_key)
        >>> contacts = client.get('contacts')['contacts']
        >>> contact_id = contacts[0]['contact']['id']
        >>> contact = client.get('contacts', contact_id)['contact']
        >>> # Partial Updates
        >>> client.put('contacts', contact_id, {'company_name': 'Acme Inc.'},
                       partial=True)

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        return self.request('PUT', resource_name, resource_id,
                            resource=resource, **kwargs)

    def patch(self, resource_name, resource_id, resource, **kwargs):
        '''\
        Partially update a resource on OnePageCRM

        Examples:
        >>> client = OnePageCRMAPI(user_id, api_key)
        >>> contacts = client.get('contacts')['contacts']
        >>> contact_id = contacts[0]['contact']['id']
        >>> contact = client.get('contacts', contact_id)['contact']
        >>> contact['company_name'] = 'Big Company Inc.'
        >>> client.patch('contacts', contact_id, contact)
        >>> # Partial Updates
        >>> client.patch('contacts', contact_id, {'company_name': 'Acme Inc.'})

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        kwargs['partial'] = True
        return self.put(resource_name, resource_id, resource, **kwargs)

    def delete(self, resource_name, resource_id=None, resource=None, **kwargs):
        '''\
        Delete a resource from OnePageCRM

        Examples:
        >>> client = OnePageCRMAPI(user_id, api_key)
        >>> contacts = client.get('contacts')['contacts']
        >>> contact_id = contacts[0]['contact']['id']
        >>> contact = client.get('contacts', contact_id)['contact']
        >>> notes = client.get('contacts', contact_id, 'notes')
        >>> # Filtering
        >>> contacts = client.get('contacts', modified_since='2014-06-20')
        >>> contacts = client.get('contacts', starred=True)

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        return self.request('DELETE', resource_name, resource_id,
                            resource=resource, **kwargs)

    def get_contacts(self, contact_id=None, sub_resource=None,
                     sub_resource_id=None, **kwargs):
        '''\
        Get Contacts or associated resource for a contact from the OnePageCRM
        API

        :returns: dict, ResponseDict
        :raises: RequestError, UnknownError\
        '''
        data = self.get('contacts', contact_id, sub_resource, sub_resource_id,
                        **kwargs)
        # Return a contacts actions, deals or notes if requested
        for resource in ('contacts', 'actions', 'deals', 'notes'):
            try:
                return data[resource]
            except KeyError:
                continue
        return data


class BaseError(Exception):
    '''\
    Base API exception\
    '''

    def __init__(self, message, status, data=None):
        super(BaseError, self).__init__()
        if data is None:
            data = {}
        self.message = str(message)
        self.status = status
        self.data = data

    def __str__(self):
        return 'Response Code: [%d]\nMessage: %s' % (self.status, self.message)

    def __repr__(self):
        return '%s %s' % (self.__class__, str(self))


class RequestError(BaseError):
    '''\
    Exception raised when there is some problem with the request sent to the
    server\
    '''
    pass


class UnknownError(BaseError):
    '''\
    Exception raised when there has been an internal server error has occurred\
    '''
    pass


class ResponseDict(OrderedDict):
    '''\
    Dictionary where keys can be used as attributes of the object\
    '''
    def __init__(self, **kwargs):
        OrderedDict.__init__(self, kwargs)
        self.__dict__.update(kwargs)

    def __contains__(self, k):
        try:
            return dict.__contains__(self, k) or hasattr(self, k)
        except AttributeError:
            return False

    def __getattr__(self, k):
        try:
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                return None

    def __setattr__(self, k, v):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
                self.__dict__.update({k: v})
            except KeyError:
                return None
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
                del self.__dict__[k]
            except KeyError:
                pass
        else:
            object.__delattr__(self, k)

    @classmethod
    def from_dict(cls, obj):
        '''\
        Convert a dictionary to a ResponseDict object\
        '''
        if isinstance(obj, dict):
            d = {str(k): cls.from_dict(v) for k, v in iteritems(obj)
                 if isidentifier(k)}
            return cls(**d)
        elif isinstance(obj, (list, tuple, set)):
            return [cls.from_dict(v) for v in obj]
        else:
            return obj

    def to_dict(self):
        '''\
        Convert a ResponseDict object to a dictionary\
        '''
        def _to_dict(obj):
            '''\
            Recursively convert all sub ResponseDict objects to dicts\
            '''
            if isinstance(obj, dict):
                return {k: _to_dict(v) for k, v in iteritems(obj)}
            elif isinstance(obj, (list, tuple, set)):
                return [_to_dict(v) for v in obj]
            else:
                return obj
        return {k: _to_dict(v) for k, v in iteritems(vars(self))}

    def __repr__(self):
        d = self.to_dict()
        return d.__repr__()

    def __str__(self):
        d = self.to_dict()
        return str(d)
