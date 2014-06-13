from urllib2 import Request, urlopen, HTTPError
import json
import urllib, urlparse
import time
import webbrowser
import os, os.path, sys
import re
import pickle

client_id="977e7a81b570457b9a9323cd2b6bb437"
client_secret="0664c93c371c4247a467d318d3313141"

class AuthException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class APISession:
	base_uri = "https://api.basespace.illumina.com/"
	version = "v1pre3"
	access_token=""
	runs=[]
	projects=[]
	scope = "browse global"

	def __init__(self):
		basespace_cred = os.path.join(os.path.dirname(__file__), ".cache")
		if os.path.isfile(basespace_cred):
			with open(basespace_cred, 'r') as f:
				saved_credentials = pickle.load(f)
				self.access_token = saved_credentials["t"]
				self.scope = saved_credentials["s"]
			print "Using cached credentials"
		else:
			self.authenticate()
		self.load_runs()
		self.load_projects()

		scope_changed = False
		for r in self.runs:
			if "read run %s" % r["Id"] not in self.scope:
				scope_changed = True
				self.scope += ", read run %s" % r["Id"]

		for p in self.projects:
			if "read project %s" % p["Id"] not in self.scope:
				scope_changed = True
				self.scope += ", read project %s" % p["Id"]

		if scope_changed: self.authenticate()

	# acquire access key for BaseSpace API session
	def authenticate(self):
		token = ""
		values = {"client_id":client_id, 
		"response_type":"device_code",
		"scope":self.scope}
		data = urllib.urlencode(values)
		request = Request("https://api.basespace.illumina.com/v1pre3/oauthv2/deviceauthorization", data)

		try:
			response = urlopen(request)
		except HTTPError as e:
			print json.load(e)
			raise
		js = json.load(response)

		webbrowser.open(js["verification_with_code_uri"])
		device_code = js["device_code"]
		interval = int(js["interval"])

		print "Additional permissions needed."
		print "To continue please navigate to %s" % js["verification_with_code_uri"] 

		while token is "":
			values = {"client_id":client_id,
			"client_secret":client_secret,
			"grant_type":"device",
			"code": device_code}
			data = urllib.urlencode(values)
			request = Request("https://api.basespace.illumina.com/v1pre3/oauthv2/token", data)

			try:
				response = urlopen(request)
				js = json.load(response)
				token = js["access_token"]
			except HTTPError as e:
				js = json.load(e)
				if js["error"]=="access_denied":
					raise AuthException(js["error_description"])
				
				time.sleep(interval)
		self.access_token = token

		with open(os.path.join(os.path.dirname(__file__), ".cache"), 'w') as f:
			pickle.dump(dict(t=token, s=self.scope), f)

	# make a BaseSpace API call using the current session user
	def api_call(self, call):
		# prepend API version if necessary
		uri = self.base_uri
		if(call[0]!='v'): uri = urlparse.urljoin(uri,self.version + "/")
		uri = urlparse.urljoin(uri,call)

		request = Request(uri)
		request.add_header("x-access-token", self.access_token)

		response = urlopen(request)
		js = json.load(response)
	
		return js["Response"]

	# download a file using a BaseSpace uri ("HrefContent" object property) to the given destination
	def download(self, uri, destination):
		if os.path.isfile(destination):
			sys.stdout.write("%s SKIPPED (already exists)\n" % destination)
			return
		directory = os.path.dirname(destination)
		filename = os.path.basename(destination)

		sys.stdout.write("{}\r".format(filename))
		bytes_read=0
		request = Request("https://api.basespace.illumina.com/" + uri)
		request.add_header("x-access-token", self.access_token)

		response = urlopen(request)
		info = response.info()
		size = int(info["Content-Length"])

		if(not os.path.exists(directory)): os.makedirs(directory)

		cwd = os.getcwd()
		os.chdir(directory)
		f = file(filename, 'w')

		data = response.read(8192)

		while data:
			f.write(data)
	 		bytes_read += len(data)
			sys.stdout.write("{} {:^10d} / {:^10d}\r".format(filename, bytes_read, size))
			sys.stdout.flush()
			data=response.read(8192)

		f.close()
		os.chdir(cwd)
		sys.stdout.write("%s (%d)\n" % (destination, size))

	# download files associated with BaseSpace object
	def download_files(self, obj):
		try: name = obj["ExperimentName"]
		except: name = obj["Name"]
		sys.stdout.write(name)
		sys.stdout.flush()

		samples = []
		appresults = []
		count = 0
		# download files using "HrefFiles" property (for run, sample objects)
		try:
			files = self.api_call(obj["HrefFiles"])["Items"]
			count += len(files)
			obj["Files"] = files
		except:
			obj["Files"] = []

		sys.stdout.write("\r%s (%d files)\r" % (name, count))
		sys.stdout.flush()

		# load samples belonging to this object (for projects)
		try:
			samples = self.api_call(obj["HrefSamples"])["Items"]
			for (i,sample) in enumerate(samples):
				sample_reference = self.api_call(sample["Href"])
				files = self.api_call(sample_reference["HrefFiles"])["Items"]
				count += len(files)
				samples[i]["Files"] = files
		except: pass

		sys.stdout.write("%s (%d files)\r" % (name, count))
		sys.stdout.flush()

		try: 
			appresults = self.api_call(obj["HrefAppResults"])["Items"]
			for (i, result) in enumerate(appresults):
				result_reference = self.api_call(result["Href"])
				files = self.api_call(result_reference["HrefFiles"])["Items"]
				count += len(files)
				appresults[i]["Files"] = files
		except: pass

		sys.stdout.write("%s (%d files)\n" % (name, count))
		sys.stdout.flush()

		for file_reference in obj["Files"]:
			f=self.api_call(file_reference["Href"])
			self.download(f["HrefContent"], "%s/%s" % (name, f["Path"]))

		# download files belonging to relevant samples
		for sample in samples:
			for file_reference in sample["Files"]:
				f=self.api_call(file_reference["Href"])
				self.download(f["HrefContent"], "%s/%s/%s" % (name, sample["Name"], f["Path"]) )

		for result in appresults:
			for file_reference in result["Files"]:
				f=self.api_call(file_reference["Href"])
				self.download(f["HrefContent"], "%s/%s/%s" % (name, result["Name"], f["Path"]) )

	def download_all(self):						
		for r in self.runs:
			self.download_files(r)
		for p in self.projects:
			self.download_files(p)

	def load_projects(self):
		self.projects = []
		response = self.api_call("users/current/projects")
		for item in response["Items"]:
			project = self.api_call(item["Href"])
			self.projects.append(project)

	def load_runs(self):
		self.runs = []
		response = self.api_call("users/current/runs")
		for item in response["Items"]:
			run = self.api_call(item["Href"])
			self.runs.append(run)


	# load runs and projects accessible by current user
	def load_all(self):
		self.runs = []
		self.projects = []
		response = self.api_call("users/current/runs")
		for item in response["Items"]:
			run = self.api_call(item["Href"])
			run["Files"] = []
			files = self.api_call(run["HrefFiles"])["Items"]
			for file_reference in files:
				f = self.api_call(file_reference["Href"])
				run["Files"].append(f)

			self.runs.append(run)

		response = self.api_call("users/current/projects")
		for item in response["Items"]:
			project = self.api_call(item["Href"])
			project["Samples"] = []
			samples = self.api_call(project["HrefSamples"])["Items"]
			for sample_reference in samples:
				s = self.api_call(sample_reference["Href"])
				s["Files"] = []
				files = self.api_call(run["HrefFiles"])["Items"]
				for file_reference in files:
					f = self.api_call(file_reference["Href"])
					s["Files"].append(f)

				project["Samples"].append(s)

			self.projects.append(project)

	def print_runs(self):
		for (i, r) in enumerate(self.runs):
			print "(%d) %s" % (i+1, r["ExperimentName"])

	def print_projects(self):
		for (i, p) in enumerate(self.projects):
			print "(%d) %s" % (i+1, p["Name"])	

def main():
	session = ""

	try:
		session=APISession()
	except AuthException as e:
		print e.value
		exit()

	# get information about current user
	user = session.api_call("users/current")

	print "Authenticated as %s (%s)" % (user["Email"], user["Name"])
	print "%d run%s, %d project%s available" % (len(session.runs), "" if len(session.runs) is 1 else "s", len(session.projects), "" if len(session.projects) is 1 else "s")

	choice = 0
	while choice is not 5:
		choice = raw_input("(1) Download run\n" + 
				"(2) Download project\n" +
				"(3) Download all\n" +
				"(4) BaseSpace API console\n" +
				"(5) Exit\n" +
				"Selection: ")
	 
		if choice is "1":
			while True:
				print "\nAvailable runs: "
				session.print_runs()
				print "(%d) Go Back" % (len(session.runs)+1)
				n = raw_input("Select a run to download: ")
				if not n.isdigit(): continue
				n = int(n)-1
				if n<0 or n>=len(session.runs): break

				if "read run %s" % session.runs[n]["Id"] not in session.scope:
					session.scope += ", read run %s" % session.runs[n]["Id"]
					session.authenticate()

				session.download_files(session.runs[n])
		elif choice is "2":
			while True:
				print "\nAvailable projects: "
				session.print_projects()
				print "(%d) Go Back" % (len(session.projects)+1)
				n=raw_input("Select a project to download: ")
				if not n.isdigit(): continue
				n = int(n)-1
				if n<0 or n>=len(session.projects): break

				if "read project %s" % session.projects[n]["Id"] not in session.scope:
					session.scope += ", read project %s" % session.projects[n]["Id"]
					session.authenticate()
				session.download_files(session.projects[n])
		elif choice is "3":
			session.download_all()
		elif choice is "4":
			while True:
				call = raw_input(": ")
				if not call: break
				try : response = session.api_call(call)
				except HTTPError as e:
					info = e.info()
					for key in info: print key, ":", info[key]
					response = json.load(e)
				for key in response.keys():
					print str(key) + " : " + str(response[key])
		elif choice is "5":
			sys.exit(0)
		print "\n"


if __name__ == "__main__":
	main()
