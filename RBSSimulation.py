import random
import pylab

class Node(object):
	def __init__(self, name, clockSkew):
		self.name = name
		self.clockSkew = clockSkew
		self.data = []
		self.receivedData = []

	def generateData(self, numPacket, intervalPacket):
		mu = self.clockSkew * float(intervalPacket) / 10**6

		for i in range(numPacket):
			increase = random.gauss(mu, 11.1) + (i + 1) * intervalPacket
			self.data.append(increase)

	def receiveData(self, other):
		avgOffset = (sum(other.data) - sum(self.data)) / float(len(self.data))
		self.receivedData.append(avgOffset)

	def processData(self, real):
		realOffset = (sum(real) - sum(self.data)) / float(len(self.data))
		maxDifference = 0.0

		for data in self.receivedData:
			difference = abs(realOffset - data)

			if difference > maxDifference:
				maxDifference = difference

		return maxDifference

class Cluster(object):
	def __init__(self, nodes):
		self.nodes = nodes

	def nodesGenerateData(self, numPacket, intervalPacket):
		for node in self.nodes:
			node.generateData(numPacket, intervalPacket)

	def nodesExchangeData(self):
		for node1 in self.nodes:
			for node2 in self.nodes:
				if node1.name != node2.name:
					node1.receiveData(node2)

	def nodesProcessData(self, real):
		groupDispersion = 0.0

		for node in self.nodes:
			maxDifference = node.processData(real)

			if maxDifference > groupDispersion:
				groupDispersion = maxDifference

		return groupDispersion

def simulateRBS(numNodes, numTrails, numPacket, intervalPacket):
	avgGroupDispersions = []

	for a in range(1, numPacket + 1):
		groupDispersions = []
		absoluteTime = []

		for b in range(a):
			absoluteTime.append((b + 1) * intervalPacket)

		for b in range(numTrails):
			nodes = []

			for c in range(numNodes):
				clockSkew = 0
				nodes.append(Node(str(c), clockSkew))

			cluster = Cluster(nodes)
			cluster.nodesGenerateData(a, intervalPacket)
			cluster.nodesExchangeData()
			groupDispersions.append(cluster.nodesProcessData(absoluteTime))

		avgGroupDispersion = sum(groupDispersions) / float(numTrails)
		avgGroupDispersions.append(avgGroupDispersion)

	return avgGroupDispersions

if __name__ == '__main__':
	pylab.figure(0)
	a = simulateRBS(2, 1000, 50, 10**5)
	b = simulateRBS(9, 1000, 50, 10**5)
	c = simulateRBS(19, 1000, 50, 10**5)
	pylab.plot(range(1, 51), a, label = '3 nodes')
	pylab.plot(range(1, 51), b, label = '10 nodes')
	pylab.plot(range(1, 51), c, label = '20 nodes')
	pylab.title('Simulation of RBS')
	pylab.xlabel('Number of broadcast packets')
	pylab.ylabel('Group dispersion (usec)')
	pylab.legend()

	pylab.figure(1)
	numNodes = pylab.array(range(3, 21))
	energyConsumption = numNodes * numNodes
	pylab.plot(numNodes, energyConsumption)
	pylab.title('RBS energy consumption')
	pylab.xlabel('Number of nodes')
	pylab.ylabel('Number of communication')
	pylab.show()