import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def printGraph(G):
	node_colors = [G.nodes[node]['color'] for node in G.nodes()] # asigno el color a cada nodo según su tipo (D o A)
	edge_colors = [G[u][v]['color'] for u,v in G.edges()] # asigno el color a cada arco según su tipo
	plt.figure(figsize=(8, 6))  # Optional: specify figure size
	nx.draw(G,with_labels=True, node_color = node_colors, edge_color = edge_colors, font_weight='bold')
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
	estacion = None
	for service in services.items():
		id , data_ = service
		from_station = data_["stops"][0]["station"]
		to_station = data_["stops"][1]["station"]
		from_time = data_["stops"][0]["time"]
		to_time = data_["stops"][1]["time"]
		demand = data_["demand"][0]
		# estacion = from_station
		print(type(data['services']))
		G.add_node(from_time,weight=0,color='blue')
		# G.add_node(to_time,weight=0,demand=int(demand/data["rs_info"]["capacity"]),color='red')
		G.add_node(to_time,weight=0,color='red')
		G.add_edge(from_time, to_time, weight= -int(demand/data["rs_info"]["capacity"]),capacity = data["rs_info"]["max_rs"], color='green' )
		


	pass

# def addTrainEdges(data, G):
# 	pass

def addTraspasoEdges(data, G):
	keys_list = list(data["services"].keys())

	prev_service = data["services"][keys_list[0]]
	for i,key in enumerate(keys_list[1:]):
		curreny_service = data["services"][key]
		if prev_service["stops"][0]["station"] == curreny_service["stops"][0]["station"]:
			# Lado A
			from_time = prev_service["stops"][0]["time"]
			to_time = curreny_service["stops"][0]["time"]
			G.add_edge(from_time, to_time, weight=0, cost=0, color='blue')

			# Lado B
			from_time = prev_service["stops"][1]["time"]
			to_time = curreny_service["stops"][1]["time"]
			G.add_edge(from_time, to_time, weight=0, cost=0,color='blue')

		prev_service = curreny_service
		
		pass
def addTraspasoEdges2(data, G):

	for station in data["stations"]:
		station_nodes = []

		for key, value in data["services"].items():
			stops = value["stops"]
			for stop in stops:
				if stop["station"] == station:
					station_nodes.append(stop["time"])
		#station_nodes = station_nodes.sort() # TAL VEZ HAYA QUE ORDENAR ESTA LISTA
		station_nodes.sort()
		print(station_nodes)

		for i in range(len(station_nodes)-1):
			G.add_edge(station_nodes[i], station_nodes[i+1], weight=0, capacity=data["rs_info"]["max_rs"] ,color='blue')
	pass

def getFirstDeparture(estacion, data, G): 
	res = 10000000000000
	for key, value in data["services"].items():  
		stops = value["stops"]
		for stop in stops:
			if stop["time"] < res and stops[0]["station"] == estacion and stops[0]["type"] == "D": # Quiero encontrar el horario de la 1ra departure de la estación
				res = stop["time"]
	return res

def getLastArrival(estacion, data, G):
    res = -1
    for key, value in data["services"].items(): 
        stops = value["stops"]
        for stop in stops:
            if stop["station"] == estacion and stop["type"] == "A" and stop["time"] > res: # Quiero encontrar el horario del último arrival a la estación
                res = stop["time"]
    return res 

def addTrasNocheEdges(data, G): 

	for estacion in data["stations"]:
		print(estacion)

		inicio = getFirstDeparture(estacion, data, G)
		# G.node[inicio].update(demand = -1 * data["rs_info"]["capacity"])
		final = getLastArrival(estacion, data, G)
		# G.node[inicio].update(demand = data["rs_info"]["capacity"])

		G.add_edge(final, inicio, weight=1,capacity = data["rs_info"]["max_rs"],color='red')

	pass

def generateGraph(filename:str):

	data = None
	with open(filename) as json_file:
		data = json.load(json_file)
		json_file.close()

	COST_PER_UNIT = data["cost_per_unit"]
	RS_INFO = data["rs_info"]
	VAGON_CAPACITY = 100
	
	G = nx.DiGraph()

	addNodesAndTrainEdges(data, G)
	addTraspasoEdges2(data, G)
	addTrasNocheEdges(data, G)

	# pos = nx.bipartite_layout(G, [node for node in G.nodes if G.nodes[node]['bipartite']==0])
	return G
	

	
def main():
	TOY = True
	if(TOY):
		filename = "instances/toy_instance.json"
	else:
		filename = "instances/retiro-tigre-semana.json"

	G = generateGraph(filename)
	flowDict = nx.min_cost_flow(G)
	print(flowDict)
	printGraph(G)

	

if __name__ == "__main__":
	main()