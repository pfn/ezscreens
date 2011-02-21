#!/usr/bin/env python
from google.appengine.dist import use_library
use_library('django', '1.2')
import ezscreens
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import webob_monkeypatch

urls = [
    ('/',                           ezscreens.HomeHandler),
    (r'/view/([a-z0-9]{4})/(.*)',   ezscreens.ViewHandler),
    (r'/delete/([a-z0-9]{4})/(.*)', ezscreens.DeleteHandler),
    ('/capture/(.*)',               ezscreens.CaptureHandler),
    ('/upload/(.*?)/(.*)',          ezscreens.UploadHandler),
    ('/my',                         ezscreens.MyHandler),
    ('/faq',                        ezscreens.FaqHandler),
]

def main():
    webob_monkeypatch.patch()
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
