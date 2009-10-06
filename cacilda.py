#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Cacilda: Python wiki powered by Cassandra

Author: Rafael Valverde
Date: 2009-10-05
Copyright (c) 2009 codeazur brasil. All rights reserved.
"""

import string
import re
from textile import textile
import urlparse, cgi
from db import get_article, get_history, save_article
from lazyboy import connection
from lazyboy.exceptions import ErrorNoSuchRecord
from mimetypes import types_map as MIMETYPES
from os import path

route_tracer = re.compile(r"""^                                # string start
                          (?P<index>\/(?:index/?)?$)         | # match a single slash
                          /static/(?P<static>[\w\.\_\-\/]+)  | # match static files
                          /edit/(?P<edit>[\w\_\-]+)          | # match edition requests
                          /(?P<article_slug>[\w\_\-]+/?)       # match articles slugs
                          """,
                          re.X)

# Adding the ico extension to mimetypes dict as the same of png files.
# Browsers were getting a bad mimetype - mimetype defaults to text/html -
# for the not found favicon.ico file
MIMETYPES[".ico"] = MIMETYPES[".png"]

class Cacilda:
  """Cacilda: Python wiki powered by Cassandra
  """
  def __init__(self, environ, start_response):
    self.environ = environ
    self.start_response = start_response
    # Let's assume a positive behaviour here :)
    self.status = "200 OK"
    self.headers = {"Content-type": "text/html"}
    # Dispatching
    self.route(self.environ["PATH_INFO"])

  def route(self, path_info):
    self._process_parameters()
    self.define_mimetype()
    route_match = route_tracer.match(path_info)
    if not route_match:
      return self.not_found

    action = route_match.groupdict()
    if action["index"]:
      return self.index()
    elif action["static"]:
      return self.serve_static(action["static"])
    elif action["edit"]:
      return self.edit(action["edit"])
    elif action["article_slug"]:
      return self.article(action["article_slug"])

  def is_post(self):
    post_ct = ["application/x-www-form-urlencoded", "multipart/form-data"]
    return self.environ["REQUEST_METHOD"].upper() == "POST" or \
        self.environ["CONTENT_TYPE"].lower() in post_ct

  def _process_parameters(self):
    input_ = self.environ['wsgi.input']
    if self.is_post():
        fs = cgi.FieldStorage(fp=input_,
                              environ=self.environ,
                              keep_blank_values=1)
        self.post = {}
        for key in fs.keys():
          self.post[key] = fs.getvalue(key)

    elif self.environ["REQUEST_METHOD"].upper() == "GET" or \
          self.environ["QUERY_STRING"]:
      self.get = urlparse.parse_qs(self.environ["QUERY_STRING"])

  def index(self):
    try:
      article = get_article("index")
      data = {"content": textile(article["content"]),
              "title": article["title"]}
    except ErrorNoSuchRecord as not_found_err:
      data = {"content": textile(open("readme.textile").read())}
    self.response = Template.render(filename="index.html", **data)

  def serve_static(self, filename):
    filename = path.join("./static/", filename)
    if path.isfile(filename):
      self.response = open(filename).read()
    else:
      self.not_found()

  def edit(self, slug):
    if self.is_post():
      self._save()
    else:
      try:
        article = get_article(slug)
        data = {"title": article["title"],
                "content": article["content"],
                "slug": slug}
      except ErrorNoSuchRecord as not_found_err:
        data = {"title": "New article: %s" % (slug,),
                "content": "Fill this field in with information. " \
                            "Textile is alright.",
                "slug": slug}
      self.response = Template.render(filename="edit.html", **data)

  def _save(self):
    slug = self.post['slug']
    title = self.post['title']
    content = self.post['content']
    save_article(slug, title, content)
    self.redirect("/%s" % (slug,))

  def article(self, slug):
    try:
      article = get_article(slug)
      data = {"title": article["title"],
              "slug": slug,
              "content": textile(article["content"])}
      self.response = Template.render(filename="article.html", **data)
    except ErrorNoSuchRecord as not_found_err:
      self.not_found(slug)

  def not_found(self, slug=None):
    self.status = "404 Not Found"
    if self.headers.get("Content-type", "text/html") == "text/html":
      self.response = Template.render(filename="404.html", **{"slug": slug})
    else:
      self.response = ""

  def define_mimetype(self):
    filename = self.environ["PATH_INFO"]
    self.headers["Content-type"] = MIMETYPES.get(path.splitext(filename)[1],
                                                 "unknown")
    if self.headers["Content-type"] == "unknown":
      del self.headers["Content-type"]

  def redirect(self, fully_qualified_url):
    self.status = "307 Temporary Redirect"
    self.headers = {"Location": fully_qualified_url}
    self.response = ""
    self.__iter__()

  def __iter__(self):
    if hasattr(self.response, "__len__"):
      self.headers['Content-length'] = str(len(self.response))
    headers = [(header, value) for header, value in self.headers.items()]
    self.start_response(self.status, headers)
    yield self.response

class Template:
  """A simple wrapper to string.Template class.
  """

  @staticmethod
  def render(template_str=None, filename=None, **kwargs):
    if filename:
      filename = path.join("./templates", filename)
      template_str = open(filename).read()

    template =  string.Template(template_str).safe_substitute(kwargs)
    return template

if __name__ == "__main__":
  from wsgiref.simple_server import make_server
  server = make_server("", 8000, Cacilda)
  print("Listening to port 8000…")
  try:
    connection.add_pool("Cacilda", ["localhost:9160"])
    server.serve_forever()
  except KeyboardInterrupt as stopped_by_user_error:
    print("Shutting server down.")
