#!/usr/bin/env python

import os
import sys

from myapp import app
from myapp.queue import queue_daemon

queue_daemon(app)
