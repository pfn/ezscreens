#!/usr/bin/env python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import ezscreens
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import webob_monkeypatch

urls = [
    ('/',                           ezscreens.HomeHandler),
    (r'/view/([a-z0-9]{4})/(.*)',   ezscreens.ViewHandler),
    (r'/delete/([a-z0-9]{4})/(.*)', ezscreens.DeleteHandler),
    ('/capture/(.*)',               ezscreens.CaptureHandler),
    ('/uploadinfo/(.*)',            ezscreens.UploadInfoHandler),
    ('/upload/(.*?)/(.*)',          ezscreens.UploadHandler),
    ('/my',                         ezscreens.MyHandler),
    ('/faq',                        ezscreens.FaqHandler),
]

def main():
    #webob_monkeypatch.patch()
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

application = webapp.WSGIApplication(urls, debug=True)
