import logging
from urlparse import urlsplit, urlunsplit
from django.template import Library
from google.appengine.api import images

register = Library()

def fix_image_url(url):
    data = urlsplit(url)
    if data[1].find("0.0.0.0") == 0:
        data = (data[0], "192.168.56.101:8002") + data[2:]
        url = urlunsplit(data)
    return url
    
def to_image_url(v, size=None):
    url = fix_image_url(images.get_serving_url(str(v.image.key())))
    sizearg = ""
    if size:
        sizearg = "=s%d" % 180
    return "%s%s" % (url,sizearg)

register.filter('image_url', to_image_url)
