#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2009 côdeazur
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
Cacilda: Python wiki powered by Cassandra

Author: Rafael Valverde
Date: 2009-10-05
Copyright (c) 2009 codeazur brasil. All rights reserved.
"""

from cacilda import Template
from db import get_article, get_history, save_article

__author__ = ("Rafael Valverde", "rafael@codeazur.com.br",
              "http://www.historiainventada.com.br/")
__license__ = "MIT"
__all__ = ["cacilda", "db", "Template", "get_article", "get_history", "save_article"]