import os
import logging
import uuid
import urllib
from urlparse import urlsplit, urlunsplit
from django.template import Library, Node, TemplateSyntaxError
from google.appengine.api import images, memcache

class RandomValueNode(Node):
    def __init__(self, outname):
        self.outname = outname
    def render(self, context):
        context[self.outname] = str(uuid.uuid4())
        return ""

register = Library()

def do_uuid(parser, token):
    params = token.contents.split()
    if len(params) != 3:
        raise TemplateSyntaxError, "uuid takes 2 arguments %s" % params
    if params[1] != 'as':
        raise TemplateSyntaxError, "'as' must be the first argument"
    return RandomValueNode(params[2])

def fix_image_url(url):
    data = urlsplit(url)
    if data[1].find("0.0.0.0") == 0:
        # hack for development environment
        data = (data[0], os.environ['HTTP_HOST']) + data[2:]
        url = urlunsplit(data)
    return url
    
def get_serving_url(image):
    url = image.image_url
    if not url:
        url = image.image_url = images.get_serving_url(str(image.image.key()))
        image.put()
    return url

def to_image_url(v, size=None):
    url = fix_image_url(get_serving_url(v))
    if size:
        sizearg = "=s%d" % 180
    else:
        sizearg = "=s0"
    return "%s%s" % (url,sizearg)

def to_encoded(v):
    return urllib.quote_plus(v, "/")

register.filter('image_url', to_image_url)
register.filter('urlencode', to_encoded)
register.tag('uuid', do_uuid)
