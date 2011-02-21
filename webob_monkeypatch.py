from cStringIO import StringIO
import sys
import urllib
import urlparse
import re

import logging

import webob
from google.appengine.ext import webapp

_SCHEME_RE = re.compile(r'^[a-z]+:', re.I)
def blank(cls, path, environ=None, base_url=None, headers=None):
    if _SCHEME_RE.search(path):
        scheme, netloc, path, qs, fragment = urlparse.urlsplit(path)
        if fragment:
            raise TypeError(
                "Path cannot contain a fragment (%r)" % fragment)
        if qs:
            path += '?' + qs
        if ':' not in netloc:
            if scheme == 'http':
                netloc += ':80'
            elif scheme == 'https':
                netloc += ':443'
            else:
                raise TypeError("Unknown scheme: %r" % scheme)
    else:
        scheme = 'http'
        netloc = 'localhost:80'
    if path and '?' in path:
        path_info, query_string = path.split('?', 1)
        path_info = urllib.unquote_plus(path_info)
    else:
        path_info = urllib.unquote_plus(path)
        query_string = ''
    env = {
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': path_info or '',
        'QUERY_STRING': query_string,
        'SERVER_NAME': netloc.split(':')[0],
        'SERVER_PORT': netloc.split(':')[1],
        'HTTP_HOST': netloc,
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': scheme,
        'wsgi.input': StringIO(''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
        }
    if base_url:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(base_url)
        if query or fragment:
            raise ValueError(
                "base_url (%r) cannot have a query or fragment"
                % base_url)
        if scheme:
            env['wsgi.url_scheme'] = scheme
        if netloc:
            if ':' not in netloc:
                if scheme == 'http':
                    netloc += ':80'
                elif scheme == 'https':
                    netloc += ':443'
                else:
                    raise ValueError(
                        "Unknown scheme: %r" % scheme)
            host, port = netloc.split(':', 1)
            env['SERVER_PORT'] = port
            env['SERVER_NAME'] = host
            env['HTTP_HOST'] = netloc
        if path:
            env['SCRIPT_NAME'] = urllib.unquote_plus(path)
    if environ:
        env.update(environ)
    obj = cls(env)
    if headers is not None:
        obj.headers.update(headers)
    return obj

def application_url(self):
    return self.host_url + urllib.quote_plus(
            self.environ.get('SCRIPT_NAME', ''), '/')

def path_url(self):
    return self.application_url + urllib.quote_plus(
            self.environ.get('PATH_INFO', ''), '/')

def path(self):
    return urllib.quote(self.script_name) + urllib.quote_plus(
            self.path_info, '/+')

def wsgi_call(self, environ, start_response):
  request = self.REQUEST_CLASS(environ)
  response = self.RESPONSE_CLASS()

  webapp.WSGIApplication.active_instance = self

  handler = None
  groups = ()
  for regexp, handler_class in self._url_mapping:
    match = regexp.match(request.path)
    if match:
      handler = handler_class()
      handler.initialize(request, response)
      groups = match.groups()
      break

  self.current_request_args = groups

  if handler:
    try:
      method = environ['REQUEST_METHOD']
      if method == 'GET':
        handler.get(*groups)
      elif method == 'POST':
        handler.post(*groups)
      elif method == 'HEAD':
        handler.head(*groups)
      elif method == 'OPTIONS':
        handler.options(*groups)
      elif method == 'PUT':
        handler.put(*groups)
      elif method == 'DELETE':
        handler.delete(*groups)
      elif method == 'TRACE':
        handler.trace(*groups)
      else:
        handler.error(501)
    except Exception, e:
      handler.handle_exception(e, self.__debug)
  else:
    response.set_status(404)

  response.wsgi_write(start_response)
  return ['']

def patch():
    webob.Request.path              = property(path)
    webob.Request.path_url          = property(path_url)
    webob.Request.application_url   = property(application_url)
    webob.Request.blank             = classmethod(blank)
    webapp.WSGIApplication.__call__ = wsgi_call
