import random
import pylab

class Node(object):
	def __init__(self, name, clockSkew):
		self.name = name
		self.clockSkew = clockSkew
		self.data = []
		self.receivedData = []

	def generateData(self):
		mu = self.clockSkew / 1000.0

		for i in range(4):
			increase = random.gauss(mu, 11.1) + (i + 1) * 10**3
			self.data.append(increase)

	def receiveData(self, other):
		self.receivedData = pylab.array(other.data[:])

	def convert(self):
		self.data = pylab.array(self.data)

	def processData(self):
		a, b = pylab.polyfit(self.data, self.receivedData, 1)
		self.data = a * self.data + b

	def compare(self):
		return abs(10000.0 - self.data[0] - self.data[1] - self.data[2] - self.data[3]) / 4.0

class Cluster(object):
	def __init__(self, nodes):
		self.nodes = nodes

	def getNumNodes(self):
		return len(self.nodes)

	def nodesGenerateData(self):
		for node in self.nodes:
			node.generateData()

	def nodesreceiveData(self):
		numNodes = self.getNumNodes()

		for i in range(1, numNodes):
			self.nodes[i].receiveData(self.nodes[i - 1])

	def nodesConvert(self):
		for node in self.nodes:
			node.convert()

	def nodesProcessData(self):
		numNodes = self.getNumNodes()

		for i in range(1, numNodes):
			self.nodes[i].processData()

	def nodesCompare(self):
		groupDispersion = 0.0
		result = []

		for node in self.nodes:
			absError = node.compare()
			result.append(absError)

			if absError > groupDispersion:
				groupDispersion = absError

		avgDispersion = sum(result) / float(self.getNumNodes())
		return groupDispersion, avgDispersion


def simulateFTSP(numNodes, numTrials):
	avgGroupDispersions = []
	avgAvgDispersions = []

	for a in range(2, numNodes + 1):
		groupDispersions = []
		avgDispersions = []

		for b in range(numTrials):
			nodes = []

			for c in range(a):
				clockSkew = 0.0 #random.uniform(1, 100)
				nodes.append(Node(str(c), clockSkew))

			cluster = Cluster(nodes)
			cluster.nodesGenerateData()
			cluster.nodesreceiveData()
			cluster.nodesConvert()
			cluster.nodesProcessData()
			x, y = cluster.nodesCompare()
			groupDispersions.append(x)
			avgDispersions.append(y)

		avgGroupDispersion = sum(groupDispersions) / float(numTrials)
		avgGroupDispersions.append(avgGroupDispersion)
		avgAvgDispersion = sum(avgDispersions) / float(numTrials)
		avgAvgDispersions.append(avgAvgDispersion)

	return avgGroupDispersions, avgAvgDispersions

if __name__ == '__main__':
	a, b = simulateFTSP(60, 1000)

	pylab.figure(0)
	pylab.plot(range(2, 61), a)
	pylab.title('Simulation of FTSP')
	pylab.xlabel('Depth of Network')
	pylab.ylabel('Group dispersion (usec)')

	pylab.figure(1)
	pylab.plot(range(2, 61), b)
	pylab.title('Simulation of FTSP')
	pylab.xlabel('Depth of Network')
	pylab.ylabel('Averge dispersion (usec)')
	pylab.ylim(3,7)

	pylab.figure(2)
	depth = pylab.array(range(2, 61))
	energyConsumption = depth - 1
	pylab.plot(depth, energyConsumption)
	pylab.title('FTSP energy consumption')
	pylab.xlabel('Depth')
	pylab.ylabel('Number of communication')
	pylab.show()