#!/usr/bin/env python
from google.appengine.dist import use_library
use_library('django', '1.2')
import ezscreens
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

urls = [
    ('/',                         ezscreens.HomeHandler),
    (r'/view/([a-z0-9]{4})/(.*)', ezscreens.ViewHandler),
    ('/capture/(.*)',             ezscreens.CaptureHandler),
    ('/my',                       ezscreens.MyHandler),
    ('/faq',                      ezscreens.FaqHandler),
    ('/upload/(.*)',              ezscreens.UploadHandler),
    ('/upload/(.*)',              ezscreens.UploadHandler),
]

def main():
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
