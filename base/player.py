class PlayerClass():
	
	def __init__(self,client,name):
		self.parent = 0
		self.room = 0
		self.client = client
		self.name = name
		self.id = self.client.id
	
	def getName(self):
		return self.name

	def status(self):
		self.parent.sendLine("You remember you're called "+self.name+".",self.id)
		self.look()

	def look(self):
		self.parent.sendLine("     "+self.room.name,self.id)
		self.parent.sendLine(self.room.desc,self.id)
		exitList = self.room.getExits()
		if exitList != []:
			self.parent.sendLine("You see the following exits: " + ','.join(exitList),self.id)

	def tryMove(self,name):
		#x[0] = id of the dest room
		#x[1] = description of road
		x = self.room.checkLink(name)
		if x:
			self.movePlayer(x[0],x[1])		
			return 1		
		return 0	

	def movePlayer(self,destID,text=0):
		self.room.removePlayer(self.id)
		self.parent.map.getRoom(destID).addPlayer(self)
		self.room = self.parent.map.getRoom(destID)
		if text:
			self.parent.sendLine(text,self.id)
		if destID != 0:
			self.parent.auth.conn.execute('update players set room = ? where id = ?',[destID,self.parent.userList[self.id][1]])
		self.look()

	def rename(self,name):
		self.name = name

	def disconnect(self,reason):
		self.parent.auth.conn.execute('update players set room = ? where id = ?',
			[self.room.id,self.parent.userList[self.id][1]])
		self.client.disconnect(reason)		
	
	def sendLine(self,line):
		self.client.sendLine(line)
	
	
	
