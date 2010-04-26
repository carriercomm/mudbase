from twisted.internet import reactor, task
import network,map,auth,parser

class GameClass():
	
	plList = {}
	userList = {}

	def __init__(self):
		print "- Core init start."
		print "- Network init."
		self.network = network.NetworkClass()
		self.network.parent = self
		fact = self.network.child
		print "- Done."
		print "- Map init."
		self.map = map.MapClass()
		self.map.parent = self
		print "- Done."
		print "- Auth init."
		self.auth = auth.AuthClass()
		self.auth.parent = self
		print "- Done."
		print "- Parser init."
		self.parser = parser.ParserClass()
		self.parser.parent = self
		print "- Done."
		print "---- Core init done."
		reactor.listenTCP(8023,fact)
		self.schedule = task.LoopingCall(self.idleTest)
		self.schedule.start(60.0)
		reactor.run()
	
	def idleTest(self):
		for id in self.plList:
			self.getClient(id).idleOut()
	
	def getPlayer(self,id):
		return self.plList[id]
	
	def getClient(self,id):
		return self.plList[id].client
	
	def getTransport(self,id):
		return self.getClient(id).transport
	
	def processChat(self,line,id=-1):
		success = self.getPlayer(id).tryMove(line)
		if not success:
			return self.checkCommand(line,id)
		return 1
	
	def checkCommand(self,line,id=-1,run=1):
		line = self.parser.processLine(line)
		if line:
			verb = line[0]
			modifiers = line[1]
			return self.doCommand(verb,modifiers,id)
		else:
			return 0
	
	def doCommand(self,verb,modifiers,id):
		#FIXME eventually need to rewrite this
		if verb == "help":
			self.sendLine("Welcome.",id)
			self.sendLine("'say message' will broadcast 'message' globally to all connected clients.",id)
			self.sendLine("'auth username password' to log in.",id)
			self.sendLine("'register username password' to register an account.",id)
			self.sendLine("Use 'rename New Name Here' to rename yourself after logging in or registering.",id)
			self.sendLine("The command 'hosts' will list all connected clients and their ips.",id)
			self.sendLine("The command 'players' will only list the player names.",id)
			self.sendLine("You can quit with 'exit'",id)
		elif verb == "exit":
			self.sendLine("Goodbye.",id)
			self.disconnect(id)
		elif verb == "hosts":
			self.printHosts(id)
		elif verb == "players":
			self.printPlayers(id)
		elif verb == "rename":
			self.renamePlayer(" ".join(modifiers),id)
		elif verb == "auth":
			return self.auth.userConnected(id,modifiers[0],modifiers[1])
		elif verb == "register":
			return self.auth.userRegister(id,modifiers[0],modifiers[1])
		elif verb == "say":
			self.globalChat(" ".join(modifiers),id)	
		elif verb == "look":
			self.getPlayer(id).look()
		elif verb == "status":
			self.getPlayer(id).status()

		return 1

	
	def printPrompt(self,id):
		self.network.sendData("> ",id)
	
	def sendLine(self,line,id):
		self.network.sendLine(line,id)
		
	def disconnect(self,id):
		#cleanup here TODO
		self.sendLine("User #"+str(id)+" ("+self.getPlayer(id).name+") has disconnected.",0)
		del self.plList[id]
		if id in self.userList:
			del self.userList[id]
		self.network.disconnect(id)
	
	def renamePlayer(self,line,id):
		if self.getPlayer(id).name != line:
			x = self.auth.renamePlayer(line,id)
			if x:
				self.sendLine(self.getPlayer(id).name + " is now known as " + line + ".",-1)
				self.getPlayer(id).rename(line)
				return 1
			self.sendLine("Rename failed. Login first?",id)
	
	def printHosts(self,id=-1):
		if id!=-1:
			for pl in self.plList:
				x = str(pl) + " - "
				x = self.getPlayer(pl).name + " - "
				x += self.getClient(pl).ip
				self.sendLine(x,id)
			self.sendLine("----",id)
		else:
			for cl in self.clList:
				print str(cl) + " - " + self.getClient(cl).ip
			print "----"

	def printPlayers(self,id=-1):
		self.sendLine("There are "+str(len(self.plList))+" players online at the moment.",id)
		for pl in self.plList:
			self.sendLine("  "+self.getPlayer(pl).name,id)
		self.sendLine("----",id)

	
	def globalChat(self,line,id):
		prcLine = "Global message from "+self.getPlayer(id).getName()+": "+line
		self.sendLine(prcLine,-1)
	
	def greet(self,id):
		self.getPlayer(id).parent = self
		self.auth.greetUser(id)
		self.doCommand("help",[],id)
		self.sendLine("Everyone, please welcome user #"+str(id)+".",0)
		self.map.getRoom(1).addPlayer(self.getPlayer(id))
		self.getPlayer(id).room = self.map.getRoom(1)
		self.getPlayer(id).look()
		self.printPrompt(id)

