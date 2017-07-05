import copy

class Model:
	def __init__(self, xml):
		self.xml = xml
		self.animorder = []
		animations = xml.findall("anim")
		self.idle = ""
		for animation in animations:
			self.animorder.append(animation.get("name"))
			if animation.get("name") == "idle":
				self.idle = animation
		
	
	def generate(self, neworder, attribs, folder):
		editedxml = copy.deepcopy(self.xml)
		for animation in editedxml.findall("anim"):
			editedxml.remove(animation)
		for key in neworder:
			found = False
			for animation in self.xml.findall("anim"):
				if animation.get("name") == key:
					animationcopy = copy.deepcopy(animation)
					animationcopy.set("clip", folder + animationcopy.get("clip"))
					editedxml.append(animationcopy)
					found = True
					break
			if not found:
				animationcopy = copy.deepcopy(self.idle)
				animationcopy.set("name", key)
				animationcopy.set("clip", folder + animationcopy.get("clip"))
				editedxml.append(animationcopy)
		for key,value in attribs.items():
			editedxml.set(key,value)
		return editedxml
