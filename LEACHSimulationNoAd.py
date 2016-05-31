import random
import pylab

def distance(node1, node2):
	dist = ((node1.position[0] - node2.position[0])**2 +
			(node1.position[1] - node2.position[1])**2)**0.5
	return dist

class Node(object):
	def __init__(self, name, energy, position):
		self.name = name
		self.energy = energy
		self.position = position
		self.myHead = None
		self.headFlag = False
		self.headInRound = []
		self.numMyNodes = 0

	def isHead(self, P, Round, baseStation):
		threshold = P / (1.0 - P * (Round % (1.0 / P)))

		if random.random() < threshold:
			self.headFlag = True
			self.headInRound.append(Round)
			dist = distance(self, baseStation)
			self.myHead = (dist, baseStation)

	def chooseHead(self, heads):
		selectiveHeads = []

		for head in heads:
			dist = distance(self, head)
			selectiveHeads.append((dist, head))

		selectiveHeads.sort()
		self.myHead = selectiveHeads[0]

	def informHead(self):
		self.myHead[1].numMyNodes += 1

	def transmit(self):
		if self.headFlag:
			self.energy -= (4 * self.numMyNodes * 5 * 10**(-8) +
							4 * self.numMyNodes * 10**(-10) * self.myHead[0]**2)
		else:
			self.energy -= (8 * 5 * 10**(-8) + 8 * 10**(-10) * self.myHead[0]**2)

		if self.energy <= 0:
			return False

		return True

class Cluster(object):
	def __init__(self, nodes, baseStation):
		self.nodes = nodes
		self.baseStation = baseStation
		self.deadNodes = []
		self.liveNodes = self.nodes[:]
		self.wasHead = []
		self.toBeHead = self.nodes[:]
		self.heads = []
		self.nonheads = self.nodes[:]

	def nodesElectHeads(self, P, Round):
		for node in self.toBeHead:
			node.isHead(P, Round, self.baseStation)

			if node.headFlag:
				self.wasHead.append(node)
				self.heads.append(node)

		for node in self.heads:
			self.toBeHead.remove(node)
			self.nonheads.remove(node)

	def nodesChooseHeads(self):
		for node in self.nonheads:
			node.chooseHead(self.heads)
			node.informHead()

	def nodesTransmit(self):
		for node in self.liveNodes:
			alive = node.transmit()

			if not alive:
				self.deadNodes.append(node)

				if node in self.toBeHead:
					self.toBeHead.remove(node)

		for node in self.deadNodes:
			if node in self.liveNodes:
				self.liveNodes.remove(node)

	def getAverageEnergy(self):
		totalEnergy = 0.0

		for node in self.liveNodes:
			totalEnergy += node.energy

		avgEnergy = totalEnergy / len(self.liveNodes)
		return avgEnergy

	def resetWasHead(self):
		self.wasHead = []
		self.toBeHead = self.liveNodes[:]

	def resetHeads(self):
		for node in self.heads:
			node.headFlag = False

		self.heads = []
		self.nonheads = self.liveNodes[:]

def simulateLEACH(numNodes, P):
	numLiveNodes = []
	avgEnergys = []
	baseStation = Node('baseStation', 1.0, (200.0, 200.0))
	nodes = []
	count = 0

	for a in range(int(numNodes**0.5)):
		for b in range(int(numNodes**0.5)):
			node = Node(str(count), 1.0, (float(a), float(b)))
			nodes.append(node)
			count += 1

	cluster = Cluster(nodes, baseStation)
	Round = 0

	while len(cluster.liveNodes) != 0:
		if Round != 0:
			cluster.resetHeads()

			if len(cluster.toBeHead) == 0:
				cluster.resetWasHead()

		while len(cluster.heads) == 0:
			cluster.nodesElectHeads(P, Round)

		cluster.nodesChooseHeads()
		cluster.nodesTransmit()

		if len(cluster.liveNodes) != 0:
			avgEnergys.append(cluster.getAverageEnergy())

		numLiveNodes.append(len(cluster.liveNodes))
		Round += 1

	return numLiveNodes, avgEnergys
