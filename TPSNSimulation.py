import random
import pylab

class Node(object):
	def __init__(self, name, clockSkew):
		self.name = name
		self.clockSkew = clockSkew
		self.data = []

	def generateData(self):
		mu = self.clockSkew / 10.0

		for i in range(2):
			increase = random.gauss(mu, 11.1) + (i + 1) * 10**5
			self.data.append(increase)

	def synchronize(self, other):
		delte = ((other.data[0] - self.data[0]) - (self.data[1] - other.data[1])) / 2.0

		for data in self.data:
			data = data + delte

	def compare(self):
		absError = abs(2 * 10**5 - self.data[1])
		return absError

class Cluster(object):
	def __init__(self, nodes):
		self.nodes = nodes

	def getNumNodes(self):
		return len(self.nodes)

	def nodesGenerateData(self):
		for node in self.nodes:
			node.generateData()

	def nodesSynchronize(self):
		numNodes = self.getNumNodes()

		for i in range(1, numNodes):
			self.nodes[i].synchronize(self.nodes[i - 1])

	def nodesCompare(self):
		groupDispersion = 0.0

		for node in self.nodes:
			absError = node.compare()

			if absError > groupDispersion:
				groupDispersion = absError

		return groupDispersion

def simulateTPSN(numNodes, numTrials):
	avgGroupDispersions = []

	for a in range(2, numNodes + 1):
		groupDispersions = []

		for b in range(numTrials):
			nodes = []

			for c in range(a):
				clockSkew = 0 #random.uniform(1, 100)
				nodes.append(Node(str(c), clockSkew))

			cluster = Cluster(nodes)
			cluster.nodesGenerateData()
			cluster.nodesSynchronize()
			groupDispersions.append(cluster.nodesCompare())

		avgGroupDispersion = sum(groupDispersions) / float(numTrials)
		avgGroupDispersions.append(avgGroupDispersion)

	return avgGroupDispersions

if __name__ == '__main__':
	pylab.figure(0)
	a = simulateTPSN(60, 5000)
	pylab.plot(range(2, 61), a)
	pylab.title('Simulation of TPSN')
	pylab.xlabel('Depth of Network')
	pylab.ylabel('Group dispersion (usec)')

	pylab.figure(1)
	depth = pylab.array(range(2, 61))
	energyConsumption = 4 * depth - 3
	pylab.plot(depth, energyConsumption)
	pylab.title('TPSN energy consumption')
	pylab.xlabel('Depth')
	pylab.ylabel('Number of communication')
	pylab.show()
