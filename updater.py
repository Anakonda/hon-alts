import os
import sys
import requests
import zipfile
import io

user = "Anakonda"
repo = "hon-alts"
branch = "master"

print("Checking updates")
if os.path.exists(os.path.join(os.path.dirname(__file__), ".git")):
	print("This seems to be git version. To update use 'git pull' instead")
	sys.exit(0)

request = requests.get("http://api.github.com/repos/" + user + "/" + repo + "/commits/" + branch, headers={"Accept": "application/vnd.github.v3.sha"})

uptodate = False

try:
	import version
	if version.version == request.text:
		uptodate = True
except ImportError:
	pass

if not uptodate:
	f = open(os.path.join(os.path.dirname(__file__), "version.py"), "w")
	f.write("version = '" + request.text + "'")
	f.close()

	print("Update found")

	newPackage = requests.get("http://github.com/" + user + "/" + repo + "/archive/" + branch + ".zip")
	zip = zipfile.ZipFile(io.BytesIO(newPackage.content))
	zip.extractall(os.path.dirname(__file__))
	print("Update complete")