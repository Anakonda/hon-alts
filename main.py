import zipfile
import os
import xml.etree.ElementTree as xmltree

import hero
import data
import settings

zipfiles = dict()
def getzip(path):
	if path not in zipfiles.keys():
		zipfiles[path] = zipfile.ZipFile(path)
	return zipfiles[path]

files = dict()

resources = [os.path.join(settings.honpath, "game", f) for f in os.listdir(os.path.join(settings.honpath, "game")) if (os.path.isfile(os.path.join(settings.honpath, "game", f)) and f[0:len("resources")] == "resources" and f[-len(".s2z"):] == ".s2z" and f != "resources999.s2z" )]

resources.sort()

translationsfile = getzip(os.path.join(settings.honpath, "game/resources0.s2z")).open("stringtables/entities_en.str")
for line in translationsfile.readlines():
	line = line.decode("utf-8").strip()
	if line == "" or line[0:1] == "//":
		continue
	split=line.split()
	data.translations[split[0]] = " ".join(split[1:])

for resource in resources:
	zip = getzip(resource)
	for file in zip.namelist():
		files[file] = resource
		if file[-len(".entity"):] == ".entity":
			xml = xmltree.fromstring(zip.open(file).read().decode("utf-8"))
			collection = None
			if xml.tag == "hero":
				collection = data.heroes
			if xml.tag == "ability":
				collection = data.abilities
			if xml.tag == "item":
				collection = data.items
			if xml.tag == "projectile":
				collection = data.projectiles
			if collection is not None:
				collection[xml.attrib["name"]] = [xml, file]
		if file[-len(".mdf"):] == ".mdf":
			data.models[file] = xmltree.fromstring(zip.open(file).read().decode("utf-8"))

modzip = zipfile.ZipFile(os.path.join(settings.honpath, "game/resourcesAutomaticAlts.s2z"), "w")
for entityname, (xml, file) in data.heroes.items():
	heroobject = hero.Hero(xml, file, data.abilities)
	for filename, content in heroobject.generate().items():
		if content is not None:
			modzip.writestr(filename, content)
modzip.close()

for name in zipfiles:
	zipfiles[name].close()
