#!/usr/bin/env python
# encoding: utf-8

"""
db - Common utilities for manipuling data to and from Cassandra
db is part of Cacilda, a Python wiki.

Author: Rafael Valverde
Date: 2009-10-05
Copyright (c) 2009 codeazur brasil. All rights reserved.
"""

from time import time
from difflib import ndiff, restore
from lazyboy import *
from lazyboy.exceptions import ErrorNoSuchRecord

class Wiki(key.Key):
  def __init__(self, key_, column_family="wiki"):
    key.Key.__init__(self, "Cacilda", column_family, key_)

class WikiArticle(record.Record):
  _require = ("slug", "title", "content")

  def __init__(self, key=None, *args, **kwargs):
    record.Record.__init__(self, *args, **kwargs)
    self.key = Wiki(key)

class WikiHistory(record.Record):

  def __init__(self, key=None, *args, **kwargs):
    record.Record.__init__(self, *args, **kwargs)
    self.key = Wiki(key, "wiki_history")

def get_article(slug):
  """Returns a dictionary for corresponding article slug.
     It may rises an lazyboy.exceptions.ErrorNoSuchRecord if
     the record cannot be found.
  """
  article = WikiArticle().load(Wiki(slug))
  return article

def get_history(slug):
  pass

def save_history(slug, title, delta):
  try:
    history_record = WikiHistory().load(Wiki(slug, "wiki_history"))
  except ErrorNoSuchRecord as err:
    history_record = WikiHistory(key=slug)
  finally:
    history_key = str(time())
    title_key = "title_%s" % (history_key,)
    data = {history_key: delta, title_key: title}
    history_record.update(data)
    history_record.save()

def save_article(slug, title, content):
  try:
    article = WikiArticle().load(Wiki(slug))
    delta_gen = ndiff(content.splitlines(1),
                      article["content"].splitlines(1))
    delta = "".join([line for line in delta_gen])
    save_history(slug, article["title"], delta)
  except ErrorNoSuchRecord as article_not_found:
    article = WikiArticle(slug)
  finally:
    data = {"title": title, "content": content}
    article.update(data)
    article.save()

class Generator(object):
  def __init__(self, text):
    self.text = text
  def __iter__(self):
    for line in self.text.splitlines(1):
      yield line
