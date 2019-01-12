import vocab
import actor
import thing
from string import lower
# Class for IntFicPy verbs
class Verb:
	word = ""
	hasDobj = False
	hasIobj = False
	impDobj = False
	impIobj = False
	preposition = False
	syntax = []
	dscope = "room" # "knows", "near", "room" or "inv"
	iscope = "room"
	
	def __init__(self, word):
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
		self.word = word
		self.dscope = "room"
		
	def addSynonym(self, word):
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
	
	def verbFunc(self, me, dobj):
		print("You " + self.word + dobj.getArticlce(True) + dobj.verbose_name + ".")
		
	def getImpDobj(self, me):
		print("Error: no implicit direct object defined")

	def getImpIobj(self, me):
		print("Error: no implicit indirect object defined")


# Below are IntFicPy's built in verbs
###########################################################################

# GET/TAKE
getVerb = Verb("get")
getVerb.addSynonym("take")
getVerb.syntax = [["get", "<dobj>"], ["take", "<dobj>"]]
getVerb.hasDobj = True

def getVerbFunc(me, dobj):
	if dobj.invItem:
		print("You take " + dobj.getArticle(True) + dobj.verbose_name + ".")
		for thing in dobj.containsIn:
			dobj.location.sub_contains.remove(thing)
			me.sub_inventory.append(thing)
		for thing in dobj.containsOn:
			dobj.location.sub_contains.remove(thing)
			me.sub_inventory.append(thing)
		dobj.location.removeThing(dobj)
		me.inventory.append(dobj)
	else:
		print(dobj.cannotTakeMsg)

getVerb.verbFunc = getVerbFunc

# DROP
dropVerb = Verb("drop")
dropVerb.syntax = [["drop", "<dobj>"]]
dropVerb.hasDobj = True
dropVerb.dscope = "inv"

def dropVerbFunc(me, dobj):
	print("You drop " + dobj.getArticle(True) + dobj.verbose_name + ".")
	for thing in dobj.containsIn:
		me.location.sub_contains.append(thing)
	for thing in dobj.containsOn:
		me.location.sub_contains.append(thing)
	me.location.addThing(dobj)
	me.inventory.remove(dobj)

dropVerb.verbFunc = dropVerbFunc

# PUT/SET ON
setOnVerb = Verb("set")
setOnVerb.addSynonym("put")
setOnVerb.syntax = [["put", "<dobj>", "on", "<iobj>"], ["set", "<dobj>", "on", "<iobj>"]]
setOnVerb.hasDobj = True
setOnVerb.dscope = "inv"
setOnVerb.hasIobj = True
setOnVerb.iscope = "room"
setOnVerb.preposition = "on"

def setOnVerbFunc(me, dobj, iobj):
	if isinstance(iobj, thing.Surface):
		print("You set " + dobj.getArticle(True) + dobj.verbose_name + " on " + iobj.getArticle(True) + iobj.verbose_name + ".")
		me.inventory.remove(dobj)
		iobj.addOn(dobj)
	else:
		print("There is no surface to set it on.")

setOnVerb.verbFunc = setOnVerbFunc

# PUT/SET IN
setInVerb = Verb("set")
setInVerb.addSynonym("put")
setInVerb.syntax = [["put", "<dobj>", "in", "<iobj>"], ["set", "<dobj>", "in", "<iobj>"]]
setInVerb.hasDobj = True
setInVerb.dscope = "inv"
setInVerb.hasIobj = True
setInVerb.iscope = "room"
setInVerb.preposition = "in"

def setInVerbFunc(me, dobj, iobj):
	if isinstance(iobj, thing.Container):
		print("You set " + dobj.getArticle(True) + dobj.verbose_name + " in " + iobj.getArticle(True) + iobj.verbose_name + ".")
		me.inventory.remove(dobj)
		iobj.addIn(dobj)
	else:
		print("There is no way to put it inside.")

setInVerb.verbFunc = setInVerbFunc

# VIEW INVENTORY
invVerb = Verb("inventory")
invVerb.addSynonym("i")
invVerb.syntax = [["inventory"], ["i"]]
invVerb.hasDobj = False

def invVerbFunc(me):
	if len(me.inventory)==0:
		print("You don't have anything with you.")
	else:
		invdesc = "You have "
		for thing in me.inventory:
			invdesc = invdesc + thing.getArticle() + thing.verbose_name
			if len(thing.containsIn) > 0:
				c = lower(thing.containsDesc)
				c =c[1:-1]
				invdesc = invdesc + " (" + c + ")"
			if thing is me.inventory[-1]:
				invdesc = invdesc + "."
			elif thing is me.inventory[-2]:
				invdesc = invdesc + " and "
			else:
				invdesc = invdesc + ", "
		print(invdesc)
invVerb.verbFunc = invVerbFunc


# LOOK (general)
lookVerb = Verb("look")
lookVerb.addSynonym("l")
lookVerb.syntax = [["look"], ["l"]]
lookVerb.hasDobj = False

def lookVerbFunc(me):
	me.location.describe(me)

lookVerb.verbFunc = lookVerbFunc

# EXAMINE (specific)
examineVerb = Verb("examine")
examineVerb.addSynonym("x")
examineVerb.syntax = [["examine", "<dobj>"], ["x", "<dobj>"]]
examineVerb.hasDobj = True
examineVerb.dscope = "near"

def examineVerbFunc(me, dobj):
	print (dobj.xdesc)

examineVerb.verbFunc = examineVerbFunc

# ASK (Actor)
askVerb = Verb("ask")
askVerb.syntax = [["ask", "<dobj>", "about", "<iobj>"]]
askVerb.hasDobj = True
askVerb.hasIobj = True
askVerb.iscope = "knows"
askVerb.impDobj = True

def getImpAsk(me):
	import parser
	people = []
	for p in me.location.contains:
		if isinstance(p, actor.Actor):
			people.append(p)
	if len(people)==0:
		print("There's no one here to ask.")
	elif len(people)==1:
		return people[0]
	elif isinstance(parser.lastTurn.dobj, actor.Actor):
		return parser.lastTurn.dobj
	else:
		print("Please specify a person to ask.")
		parser.lastTurn.ambiguous = True

askVerb.getImpDobj = getImpAsk

def askVerbFunc(me, dobj, iobj):
	if isinstance(dobj, actor.Actor):
		if iobj in dobj.ask_topics:
			dobj.ask_topics[iobj].func()
		else:
			dobj.defaultTopic()
	else:
		print("You cannot talk to that.")

askVerb.verbFunc = askVerbFunc
