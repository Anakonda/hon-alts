import xml.etree.ElementTree as xmltree
import copy

import data
import model
import os

class Alt:
	def __init__(self, xml):
		pass

def absolutepath(file, path):
	if path[0] == "/":
		return path
	return os.path.dirname(file) + "/" + path

class Hero:
	def __init__(self, xml, filename):
		self.xml = xml
		self.filename = filename
		self.abilities = []
		for i in range(0,4):
			if "inventory" + str(i) in data.abilities:
				self.abilities.push_back(data.abilities[xml.get("inventory" + str(i))])
		self.modelpath = absolutepath(self.filename, xml.get("model"))
		self.mainModel = model.Model(data.models[self.modelpath])
		
		self.projectile = self.xml.get("attackprojectile")

	def getAlts(self):
		return [alt.get("key").split(".")[1] if len(alt.get("key").split(".")) > 1 else alt.get("key") for alt in self.xml.findall("altavatar")]

	def generate(self, alt=""):
		editedfiles = dict()

		if self.xml is None:
			print(self.filename)
			return dict()

		editedxml = copy.deepcopy(self.xml)

		changes = xmltree.Element("dummy")

		newprojectile = self.projectile
		projectilesToEdit = []

		if "attackprojectile" in self.xml.attrib:
			projectile = self.xml.get("attackprojectile")
		for altTag in self.xml.findall("altavatar"):
			if alt != "" and alt in altTag.get("key"):
				changes = copy.deepcopy(altTag)
				if "attackprojectile" in altTag.attrib:
					del changes.attrib["attackprojectile"]
					newprojectile = altTag.get("attackprojectile")
				break
		for key,value in changes.attrib.items():
			editedxml.set(key, value)
		for child in list(changes):
			toremove = editedxml.find(child.tag)
			if toremove is not None:
				editedxml.remove(toremove)
		editedxml.extend(list(changes))

		newmodelpath = absolutepath(self.filename, editedxml.get("model"))
		newModel = model.Model(data.models[newmodelpath])

		for altTag in editedxml.findall("altavatar"):
			name = altTag.get("key")
			attackprojectile = altTag.get("attackprojectile")
			altModelPath = altTag.get("model")
			altTag.clear()
			altTag.tail = "\n"
			altTag.set("key", name)
			altTag.set("altavatar", "true")
			altTag.set("modpriority", "1")
			if attackprojectile is not None:
				altTag.set("attackprojectile", attackprojectile)
				projectilesToEdit.append(attackprojectile)
			if altModelPath is not None:
				altTag.set("model", altModelPath)
				altModelPath = absolutepath(self.filename, altModelPath)
				if altModelPath in data.models:
					attribs = dict()
					for attribute in ["file", "high", "low", "med"]:
						if attribute in data.models[newmodelpath].attrib:
							attribs[attribute] = "/" + absolutepath(altModelPath, data.models[newmodelpath].get(attribute))
					altModel = model.Model(data.models[altModelPath])
					editedfiles[altModelPath] = xmltree.tostring(newModel.generate(altModel.animorder, attribs, "/" + os.path.dirname(newmodelpath) + "/"), encoding="unicode")
		editedfiles[self.filename] = xmltree.tostring(editedxml, encoding="unicode")

		for ability in self.abilities:
			editedAbility = copy.deepcopy(ability[0])
			changes = xmltree.Element("dummy")
			for altTag in ability[0].findall("altavatar"):
				if alt != "" and alt in altTag.get("key"):
					changes = altTag
					break
			for key,value in changes.attrib.items():
				editedAbility.set(key, value)
			for child in list(changes):
				toremove = editedxml.find(child.tag)
				if toremove is not None:
					editedAbility.remove(toremove)
			for altTag in editedAbility.findall("altavatar"):
				name = altTag.get("key")
				projectile = altTag.get("projectile")
				altTag.clear()
				altTag.tail = "\n"
				altTag.set("name", name)
				if projectile is not None:
					altTag.set("projectile", projectile)
			editedfiles[ability[1]] = xmltree.tostring(editedAbility, encoding="unicode")

		return editedfiles
