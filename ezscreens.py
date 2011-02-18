from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import logging
import time
import urllib
from random import Random

from google.appengine.api import users, memcache
from google.appengine.ext import db, blobstore
from google.appengine.ext.webapp import template, RequestHandler
from google.appengine.ext.webapp import blobstore_handlers
import django.templatetags
import templatetags.ezscreens as tt

django.templatetags.__path__.extend(
        __import__('templatetags', {}, {}, ['']).__path__)

class ScreenShot(db.Model):
    owner     = db.UserProperty()
    image     = blobstore.BlobReferenceProperty()
    create_ts = db.DateTimeProperty(auto_now=True)
    name      = db.StringProperty()
    path      = db.StringProperty()
    views     = db.IntegerProperty()

class Handler():
    def user(self):
        return users.get_current_user()

    def render(self, tmpl, params={}):
        self.response.out.write(self.process(tmpl, params))

    def process(self, tmpl, params={}):
        user = users.get_current_user()

        p = {
            'logged_in':    user != None,
            'current_user': user,
            'login_url':    users.create_login_url(self.request.uri),
            'logout_url':   users.create_logout_url('/'),
            'request_uri':  self.request.path,
        }
        p.update(params)

        path = os.path.join(os.path.dirname(__file__), "templates", tmpl)
        return template.render(path, p)

    def respond(self, body, status=200):
        if status != 200:
            self.error(status)
        self.response.out.write(body)

class HomeHandler(Handler, RequestHandler):
    def get(self):
        screenshots = ScreenShot.gql(
                "where owner = null order by create_ts desc").fetch(20)
        fill_view_count(screenshots)
        self.render("home.html", {
            "screenshots": screenshots,
        })

def fill_view_count(items):
    """ update views with cached values """
    for item in items:
        cached = memcache.get(item.key().name() + "-viewcount")
        if cached:
            d = cached.split(":")
            item.views = int(d[0])

class ViewHandler(Handler, RequestHandler):
    def get(self, prefix, name):
        name = urllib.unquote(name)
        path = "%s/%s" % (prefix, name)

        data = ScreenShot.get_by_key_name(path)
        if not data:
            self.respond("Not found", 404)
            return

        lastput = 0
        now = int(time.time())
        views = data.views

        cached_views = memcache.get(path + "-viewcount")
        if cached_views:
            d = cached_views.split(":")
            views = int(d[0])
            lastput = int(d[1])
        else:
            lastput = now

        if not views:
            views = 0
        views += 1

        if views > data.views:
            if (now - lastput) > 30:
                data.views = views
                data.put()
        else:
            views = data.views

        # update for rendering, and saving if time elapsed
        data.views = views

        memcache.set(path + "-viewcount", "%d:%d" % (views, lastput))

        self.render("view.html", {
            "screenshot": data,
            "name": name,
            "image_url": tt.to_image_url(data),
        })

class CaptureHandler(Handler, RequestHandler):
    def get(self, name):
        name = urllib.unquote(name)
        upload_url = blobstore.create_upload_url(
                "/upload/" + urllib.quote(name))
        self.render("capture.html", {
            "name": name,
            "upload_url": upload_url,
        })

class UploadHandler(Handler, blobstore_handlers.BlobstoreUploadHandler):
    def post(self, name):
        r = Random()
        prefix = hex(r.randint(0x1000, 0xffff))[2:]
        name = urllib.unquote(name)

        path = "%s/%s" % (prefix, name)

        data = ScreenShot.get_by_key_name(path)
        if not data:
            data = ScreenShot(key_name=path)
        else:
            data.image.delete()

        user = users.get_current_user()
        uploaded = self.get_uploads('file')[0]
        data.owner = user
        data.image = uploaded
        data.name  = name
        data.path  = path
        data.views = 0
        data.put()

        limit = 100 if user else 500

        to_delete = ScreenShot.gql(
                "where owner = :1 order by create_ts desc",
                users.get_current_user()).fetch(limit, offset=500)

        if len(to_delete) > 0:
            for item in to_delete:
                item.image.delete()
            db.delete(to_delete)

        self.redirect("/view/%s/%s" % (prefix, urllib.quote(name)))

class MyHandler(Handler, RequestHandler):
    def get(self):
        screenshots = ScreenShot.gql(
                "where owner = :1 order by create_ts desc",
                users.get_current_user()).fetch(100)
        fill_view_count(screenshots)
        self.render("my.html", {
            "screenshots": screenshots,
        })
class FaqHandler(Handler, RequestHandler):
    def get(self):
        self.render("faq.html")
