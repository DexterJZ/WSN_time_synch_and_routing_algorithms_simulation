import random
import pylab
import SEPSimulation

def distance(node1, node2):
	dist = ((node1.position[0] - node2.position[0])**2 +
			(node1.position[1] - node2.position[1])**2)**0.5
	return dist

class Node(object):
	def __init__(self, name, energy, position):
		self.name = name
		self.energy = energy
		self.position = position
		self.advanced = False
		self.myHead = None
		self.headFlag = False
		self.headInRound = 0
		self.numMyNodes = 0

	def isHead(self, P, Round, baseStation):
		pChange = 0.0

		if self.advanced:
			pChange = P / (1.0 + 3 * 0.2) * (1 + 3)
		else:
			pChange = P / (1.0 + 3 * 0.2)

		threshold = pChange / (1.0 - pChange * (Round % (1.0 / pChange)))

		if random.random() < threshold:
			self.headFlag = True
			self.headInRound += 1
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

	def synch(self):
		if self.headFlag:
			self.energy -= (1 * self.numMyNodes * 5 * 10**(-8) +
							1 * self.numMyNodes * 10**(-10) * self.myHead[0]**2)
		else:
			self.energy -= (1 * 5 * 10**(-8) + 1 * 10**(-10) * self.myHead[0]**2)

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
				self.heads.append(node)

				if node.advanced and node.headInRound == 4:
					self.wasHead.append(node)
				elif not node.advanced:
					self.wasHead.append(node)
				else:
					pass

		for node in self.heads:
			self.nonheads.remove(node)

		for node in self.wasHead:
			if node in self.toBeHead:
				self.toBeHead.remove(node)

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

	def nodesSynch(self):
		for node in self.liveNodes:
			alive = node.synch()

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
		for node in self.wasHead:
			node.headInRound = 0

		self.wasHead = []
		self.toBeHead = self.liveNodes[:]

	def resetHeads(self):
		for node in self.heads:
			node.headFlag = False

		self.heads = []
		self.nonheads = self.liveNodes[:]

def simulateSEPandTPSN(numNodes, P):
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

	advancedNodes = random.sample(nodes, 20)

	for node in advancedNodes:
		node.energy = 4.0
		node.advanced = True

	cluster = Cluster(nodes, baseStation)
	Round = 0

	while len(cluster.liveNodes) != 0:
		if Round != 0:
			cluster.resetHeads()

			if len(cluster.toBeHead) == 0:
				cluster.resetWasHead()
				cluster.nodesSynch()

		while len(cluster.heads) == 0:
			cluster.nodesElectHeads(P, Round)

		cluster.nodesChooseHeads()
		cluster.nodesTransmit()

		if len(cluster.liveNodes) != 0:
			avgEnergys.append(cluster.getAverageEnergy())

		numLiveNodes.append(len(cluster.liveNodes))
		Round += 1

	return numLiveNodes, avgEnergys

if __name__ == '__main__':
	data1, data2 = simulateSEPandTPSN(100, 0.05)
	data3, data4 = SEPSimulation.simulateSEP(100, 0.05)

	pylab.figure(0)
	pylab.plot(data1, label = 'SEP&TPSN')
	pylab.plot(data3, label = 'only SEP')
	pylab.title('Simulation of combination of SEP and TPSN')
	pylab.xlabel('Time steps (rounds)')
	pylab.ylabel('Number of nodes still alive')
	pylab.legend()

	pylab.show()