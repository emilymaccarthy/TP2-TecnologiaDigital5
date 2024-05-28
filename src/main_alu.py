import json
import networkx as nx
import matplotlib.pyplot as plt


def printGraph(G):
	plt.figure(figsize=(8, 6))  # Optional: specify figure size
	nx.draw(G, with_labels=True, font_weight='bold')
	plt.show()

def addService(service, G):
	id, data = service
	# print(data)
	from_station = data["stops"][0]["station"]
	to_station = data["stops"][1]["station"]
	from_time = data["stops"][0]["time"]
	to_time = data["stops"][1]["time"]
	demand = data["demand"]

	print(from_station, to_station, from_time, to_time,demand)
	


	# print(service, data["services"][service]["stops"])

def addNodesAndTrainEdges(data, G): 
	services = data["services"]
	for service in services.items():
		id , data = service
		from_station = data["stops"][0]["station"]
		to_station = data["stops"][1]["station"]
		from_time = data["stops"][0]["time"]
		to_time = data["stops"][1]["time"]
		demand = data["demand"]

		
		G.add_node(from_time,weight=0)
		G.add_node(to_time,weight=0)
		G.add_edge(from_time, to_time, weight=0, cost=0)
		


	pass

# def addTrainEdges(data, G):
# 	pass

def addTraspasoEdges(data, G):
	pass

def addTrasNocheEdges(data, G): 
	pass

def generateGraph(filename:str):

	with open(filename) as json_file:
		data = json.load(json_file)
		json_file.close()

	COST_PER_UNIT = data["cost_per_unit"]
	RS_INFO = data["rs_info"]
	VAGON_CAPACITY = 100
	
	G = nx.DiGraph()

	addNodesAndTrainEdges(data, G)
	# addTrainEdges(data, G)
	addTraspasoEdges(data, G)
	addTrasNocheEdges(data, G)

	printGraph(G)

	
def main():
	TOY = True
	if(TOY):
		filename = "instances/toy_instance.json"
	else:
		filename = "instances/retiro-tigre-semana.json"

	generateGraph(filename)

	

if __name__ == "__main__":
	main()