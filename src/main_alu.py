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
	keys_list = list(data["services"].keys())

	prev_service = data["services"][keys_list[0]]
	for i,key in enumerate(keys_list[1:]):
		curreny_service = data["services"][key]
		if prev_service["stops"][0]["station"] == curreny_service["stops"][0]["station"]:
			# Lado A
			from_time = prev_service["stops"][0]["time"]
			to_time = curreny_service["stops"][0]["time"]
			G.add_edge(from_time, to_time, weight=0, cost=0)

			# Lado B
			from_time = prev_service["stops"][1]["time"]
			to_time = curreny_service["stops"][1]["time"]
			G.add_edge(from_time, to_time, weight=0, cost=0)

		prev_service = curreny_service
		
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
		final = getLastArrival(estacion, data, G)

		G.add_edge(final, inicio, weight=0, cost=1)

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
	addTraspasoEdges(data, G)
	addTrasNocheEdges(data, G)

	# pos = nx.bipartite_layout(G, [node for node in G.nodes if G.nodes[node]['bipartite']==0])

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