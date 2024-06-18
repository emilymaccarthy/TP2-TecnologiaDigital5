import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

########## Funciones para hacer el grafo

def generateGraph(data,modificaciones_trasnoche):
	## Genera el grafo G
	G = nx.DiGraph()

	addNodesAndTrainEdges(data, G)
	addTraspasoEdges(data, G)
	addTrasNocheEdges(data, G,modificaciones_trasnoche)

	return G

def addService(service, G):
    ## haces los nodos
	id, data = service
	from_station = data["stops"][0]["station"]
	to_station = data["stops"][1]["station"]
	from_time = data["stops"][0]["time"]
	to_time = data["stops"][1]["time"]
	demand = data["demand"]

def addNodesAndTrainEdges(data, G):
    ## agrega los trenes de viaje
	services = data["services"]
	estacion = None
	for service in services.items():
		id , data_ = service
		from_station = data_["stops"][0]["station"]
		to_station = data_["stops"][1]["station"]
		from_time = data_["stops"][0]["time"]
		to_time = data_["stops"][1]["time"]
		capacidad = data["rs_info"]["capacity"]
		demand = data_["demand"][0]
		flow = int(np.ceil(demand/capacidad))

		from_ = get_node_name(from_time,from_station)
		to_ = get_node_name(to_time,to_station)
		G.add_node(from_,demand = flow, color='blue')
		G.add_node(to_, demand= -flow, color='red')
		G.add_edge(from_, to_, weight= 0,capacity = data["rs_info"]["max_rs"] - flow, color='green' )

def addTraspasoEdges(data, G):
	## conecta dos eventos consecutivos
	for station in data["stations"]:
		station_nodes = []

		for key, value in data["services"].items():
			stops = value["stops"]
			for stop in stops:
				if stop["station"] == station:
					station_nodes.append(stop["time"])
		#station_nodes = station_nodes.sort() # TAL VEZ HAYA QUE ORDENAR ESTA LISTA
		station_nodes.sort()

		station_nodes = [get_node_name(station_nodes[i],station) for i in range(len(station_nodes))]
		for i in range(len(station_nodes)-1):
			G.add_edge(station_nodes[i], station_nodes[i+1], weight=0, capacity=float("inf") ,color='blue')

def getFirstDeparture(estacion, data, G):
    ## primer servicio del diaa
	res = 10000000000000
	for key, value in data["services"].items():
		stops = value["stops"]
		for stop in stops:
			if stop["time"] < res and stop["station"] == estacion: # Quiero encontrar el horario de la 1ra departure de la estación
				res = stop["time"]
	return get_node_name(res, estacion)

def getLastArrival(estacion, data, G):
    ## ultimo servico del dia
    res = -1
    for key, value in data["services"].items():
        stops = value["stops"]
        for stop in stops:
            if stop["station"] == estacion and stop["time"] > res: # Quiero encontrar el horario del último arrival a la estación
                res = stop["time"]
    return get_node_name(res, estacion)

def addTrasNocheEdges(data, G, modificacion_trasnoche):
	## agregas las aristas de trasnoche
	for estacion in data["stations"]:
		inicio = getFirstDeparture(estacion, data, G)
		final = getLastArrival(estacion, data, G)
		if(modificacion_trasnoche[0] != 0):
			if(modificacion_trasnoche[1] == estacion):
				G.add_edge(final, inicio, weight=1,capacity = data["rs_info"]["max_rs"] - modificacion_trasnoche[0],color='red')
			else:
				G.add_edge(final, inicio, weight=1,capacity = float("inf"),color='red')
		else:
			G.add_edge(final, inicio, weight=1,capacity = float("inf"),color='red')


########## Funciones para imprimir el grafico

def printGraph(G,data,flow_dict):

    # Crear etiquetas para los bordes que muestren peso, capacidad y flujo
    edge_labels = {}
    for u, v, d in G.edges(data=True):
        if u in flow_dict and v in flow_dict[u]:
	    # f"w={d['weight']}, c={d['capacity']}, f={flow_dict[u][v]}" POR LAS DUDAS
            edge_labels[(u, v)] = f"w={d['weight']},f={flow_dict[u][v]}"
        else:
            print(f"Missing flow for edge ({u}, {v})")

    # Asignar colores a los nodos y bordes
    node_colors = [G.nodes[node]['color'] for node in G.nodes()]
    edge_colors = [G[u][v]['color'] for u, v in G.edges()]
    edges_curves = [G.edges()]

    edges_with_curves = get_curved_edges(G)  # Especificar aristas con curva aquí

    edge_styles = ['arc3, rad=0.45' if (u, v) in edges_with_curves else 'arc3, rad=0' for u, v in G.edges()]

    pos = getPos(data)


    plt.figure(figsize=(8, 8))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors)
    nx.draw_networkx_labels(G, pos, font_weight='bold')

    for (u, v), style in zip(G.edges(), edge_styles):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=[G[u][v]['color']], connectionstyle=style)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

	# Ajustar la posición de las etiquetas de los bordes curvados
    label_pos_adjust = {}
    for (u, v) in edges_with_curves:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        label_pos_adjust[(u, v)] = ((x1 + x2) / 2  , (y1 + y2) / 2 + 0.1)

    # Dibujar etiquetas manualmente para bordes con curvas
    for (u, v), (x, y) in label_pos_adjust.items():
        plt.text(x+0.1, y, edge_labels[(u, v)], fontsize= 12, ha='left')

    plt.show()


########## Determinar los costos (Vagones totales)

def costo_minimo(flowDict,G):
	#arregla la representacion en el grafo
	for u, v in G.edges:
		if G.edges[u,v]['color'] == 'green':
			flowDict[u][v] += G.nodes[u]["demand"]

def vagones_totales(flowDict,data, G):
	#Costo por cada estacion medido en cantidad de vagones necesarios para satisfacer la demanda

	flujo_estacion = 0

	for estacion in data["stations"]:
		inicio = getFirstDeparture(estacion, data, G)
		final = getLastArrival(estacion, data, G)
		flujo_estacion = flowDict[final][inicio]

		print(F"{estacion}: {flujo_estacion} vagones")

def getFlowCost(flowDict, G):
	#Costo total para la empresa medido en unidades de vagones
	cost = 0
	for u,v in G.edges:
		cost += flowDict[u][v] * G.edges[u,v]['weight']
	return cost


########## Genera cronograma random

def generate_random_json(
        num_services=8,
        num_stations=2,
        max_time=1440, # 1440 minutos === 60*24 minutos === 1 día
        demand_per_hour=None,
        capacity=100,
        max_rs=25,
        time_between_services = 58,
        cost_per_unit = 1.0,
        seed = 42
    ):

    random.seed(seed)
    stations = [f"{i}Station" for i in range(num_stations)]
    services = {}

    for service_id in range(1, num_services + 1):
        stops = []
        start_time = random.randint(0, max_time - time_between_services)
        hour_of_day = (start_time // 60) % 24  # Convertir minutos a hora del día (0-23)

        if demand_per_hour is not None:
            demand_value = demand_per_hour[hour_of_day]  # Usar la demanda correspondiente a la hora del día
        else:
            demand_value = 500  # Valor por defecto si no se proporciona demanda

        stationD = random.choice(stations)
        stationA = random.choice(stations)
        while stationD == stationA:
            stationA = random.choice(stations)

        stops.append({
            "time": start_time,
            "station": stationD,
            "type": "D"
        })
        stops.append({
            "time": start_time + time_between_services,
            "station": stationA,
            "type": "A"
        })

        services[str(service_id)] = {
            "stops": stops,
            "demand": [demand_value]
        }

    cost_per_unit = {station: cost_per_unit for station in stations}

    data = {
        "services": services,
        "stations": stations,
        "cost_per_unit": cost_per_unit,
        "rs_info": {
            "capacity": capacity,
            "max_rs": max_rs
        }
    }

    return data

def generate_random_json2(
        num_services=8,
        num_stations=2,
        max_time=1440, # 1440 minutos === 60*24 minutos === 1 dia
        demand_value=500,
        capacity=100,
        max_rs=25,
        time_beetween_services = 58,
        cost_per_unit = 1.0,
		seed = 42
        ):

    random.seed(seed)
    stations = [f"{i}Station" for i in range(num_stations)]
    services = {}

    for service_id in range(1, num_services + 1):
        stops = []
        time = random.randint(0, max_time - time_beetween_services)
        stationD = random.choice(stations)
        stationA = random.choice(stations)
        while stationD == stationA:
            stationA = random.choice(stations)
        stop = {
            "time": time,
            "station": stationD,
            "type": "D"
        }
        stops.append(stop)
        stop = {
            "time": time + time_beetween_services,
            "station": stationA,
            "type": "A"
        }
        stops.append(stop)
        services[str(service_id)] = {
            "stops": stops,
            "demand": [demand_value]
        }

    cost_per_unit = {station: cost_per_unit for station in stations}

    data = {
        "services": services,
        "stations": stations,
        "cost_per_unit": cost_per_unit,
        "rs_info": {
            "capacity": capacity,
            "max_rs": max_rs
        }
    }

    return data


########## Funciones auxiliares

def getDatafromPath(path):
    with open(path) as json_file:
        data = json.load(json_file)
        json_file.close()
    return data

def get_node_name(time:int,station:str):
    name = str(time)
    while len(name) < 4:
        name = '0' + name
    return name +"_" +station[:2]

def sort_nodes(nodes:list):
    sorted_nodes = []
    for i in range(len(nodes)):
        value = int(nodes[i][:4])
        sorted_nodes.append(value)
    sorted_nodes.sort()
    for i in range(len(sorted_nodes)):
        sorted_nodes[i] = get_node_name(sorted_nodes[i],nodes[i][5:])
    return sorted_nodes

def getPos(data):
	servicios:dict = data["services"]
	pos = {}
	for i, estacion in enumerate(data["stations"]):
		columna = []
		for key, value in servicios.items():

			if value["stops"][0]["station"] == estacion:
					name_value = get_node_name(value["stops"][0]["time"],value["stops"][0]["station"])
					columna.append(name_value)
			if value["stops"][1]["station"] == estacion:
					name_value = get_node_name(value["stops"][1]["time"],value["stops"][1]["station"])
					columna.append(name_value)

		columna = sort_nodes(columna)
		columna.reverse()
		for j, value in enumerate(columna):
			pos[value] = (i,j)

	return pos

def get_curved_edges(G):
	edges = []
	for u,v in G.edges():
		if u[:4] > v[:4]:
			edges.append((u,v))
	return edges


########## Funciones para la eperimentacion

def experimentacion_horarios_de_circulacion(demand, cantidad_serv, plot_graph, plot_grafo):
    #tiempo que raleway services esta abierto
	REDUCCION_CAPACIDAD_TRASNOCHE = (0,"0Station")

	resultados = []
	#voy agregandole una hora mas de funcionamiento  para la misma demanda
	for i in range(1,25):
		data = generate_random_json(
				num_services=cantidad_serv,
				num_stations=2,
				max_time= (60*i), # 1440 minutos === 60*24 minutos === 1 dia
				demand_per_hour=demand,
				capacity=100,
				max_rs=25,
				time_between_services = 60,
				cost_per_unit = 1.0,
				seed = 42
				)

		try:
			G = generateGraph(data,REDUCCION_CAPACIDAD_TRASNOCHE)
			flowDict = nx.min_cost_flow(G)

			costo = getFlowCost(flowDict, G)
			if plot_grafo:
				printGraph(G, data, flowDict)

			resultados.append((i, costo, True))  # El tercer elemento indica que no hubo error
		except Exception as e:
			print(f"Error para i = {i}: {e}")
			resultados.append((i, None, False))  # El tercer elemento indica que hubo error

	valores_x_validos = [x for x, res, valid in resultados if valid]
	valores_y_validos = [res for x, res, valid in resultados if valid]

	valores_x_invalidos = [x for x, res, valid in resultados if not valid]
	valores_y_invalidos = [0 for x, res, valid in resultados if not valid]

	if plot_graph:
		plot(valores_x_validos,valores_y_validos,valores_x_invalidos,valores_y_invalidos,"Cantidad de Vagones","Cantidad total de horas de circulacion de trenes (en un dia)",f"Costo de tener trenes circulando mas horas (en cantidad de vagones)\n para {cantidad_serv} servicios")

	return valores_x_validos, valores_y_validos, valores_x_invalidos, valores_y_invalidos

def experimentacion_capcidad_trenes(demand, cantidad_serv, plot_graph, plot_grafo):
    #modificar la capacidad de trenes ver impacto en el costo
	capacidad_trenes = [50,100,150,200,250,300,350,400]
	REDUCCION_CAPACIDAD_TRASNOCHE = (0,"0Station")

	resultados = []
	#voy agregandole una hora mas de funcionamiento  para la misma demanda
	for i in capacidad_trenes:
		data = generate_random_json(
				num_services=cantidad_serv,
				num_stations=2,
				max_time= 1440, # 1440 minutos === 60*24 minutos === 1 dia
				demand_per_hour=demand,
				capacity=i,
				max_rs=50,
				time_between_services = 60,
				cost_per_unit = 1.0,
				seed = 42
				)

		try:
			G = generateGraph(data,REDUCCION_CAPACIDAD_TRASNOCHE)
			flowDict = nx.min_cost_flow(G)

			costo = getFlowCost(flowDict, G)
			if plot_grafo:
				printGraph(G,data, flowDict)

			resultados.append((i, costo, True))  # El tercer elemento indica que no hubo error
		except Exception as e:
			print(f"Error para i = {i}: {e}")
			resultados.append((i, None, False))  # El tercer elemento indica que hubo error

	valores_x_validos = [x for x, res, valid in resultados if valid]
	valores_y_validos = [res for x, res, valid in resultados if valid]

	valores_x_invalidos = [x for x, res, valid in resultados if not valid]
	valores_y_invalidos = [0 for x, res, valid in resultados if not valid]
	if plot_graph:
		plot(valores_x_validos,valores_y_validos,valores_x_invalidos,valores_y_invalidos,"Cantidad de Vagones","Capicada de vagones (medidio en personas)",f"Costo de tener trenes de mayor capacidad para {cantidad_serv} servicios")

	return valores_x_validos, valores_y_validos, valores_x_invalidos, valores_y_invalidos

def experimentacion_tiempo_entre_servicios(demand, cantidad_serv, plot_graph, plot_grafo):
	tiempo_entre_servicios = [60, 120, 180, 240, 300, 360, 420]

	REDUCCION_CAPACIDAD_TRASNOCHE = (0,"0Station")

	resultados = []
	#voy agregandole una hora mas de funcionamiento  para la misma demanda
	for i in tiempo_entre_servicios:
		data = generate_random_json(
				num_services=cantidad_serv,
				num_stations=2,
				max_time= 1440, # 1440 minutos === 60*24 minutos === 1 dia
				demand_per_hour=demand,
				capacity=100,
				max_rs=50,
				time_between_services = i,
				cost_per_unit = 1.0,
				seed = 42
				)

		try:
			G = generateGraph(data,REDUCCION_CAPACIDAD_TRASNOCHE)
			flowDict = nx.min_cost_flow(G)

			costo = getFlowCost(flowDict, G)
			if plot_grafo:	
				printGraph(G, data, flowDict)

			resultados.append((i, costo, True))  # El tercer elemento indica que no hubo error
		except Exception as e:
			print(f"Error para i = {i}: {e}")
			resultados.append((i, None, False))  # El tercer elemento indica que hubo error

	valores_x_validos = [x for x, res, valid in resultados if valid]
	valores_y_validos = [res for x, res, valid in resultados if valid]

	valores_x_invalidos = [x for x, res, valid in resultados if not valid]
	valores_y_invalidos = [0 for x, res, valid in resultados if not valid]
	if plot_graph:
		plot(valores_x_validos,valores_y_validos,valores_x_invalidos,valores_y_invalidos,"Cantidad de Vagones","Tiempo minimo entre servicios",f"Variacion del costo segun el tiempo entre servicios de trenes \npara {cantidad_serv} servicios")

	return valores_x_validos, valores_y_validos, valores_x_invalidos, valores_y_invalidos

def plot(valores_x_validos,valores_y_validos,valores_x_invalidos,valores_y_invalidos,ylabel,xlabel,titulo):

	# Graficar los resultados
	plt.plot(valores_x_validos, valores_y_validos, marker='o', linestyle='-', label='Valores válidos')
	plt.scatter(valores_x_invalidos, valores_y_invalidos, color='red', marker='x', label='Errores')

	# Añadir etiquetas y título
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(titulo)
	plt.legend()

	# Mostrar el gráfico
	plt.show()

def plot_superpuesto(valores_x_validos, valores_y_validos, xlabel, ylabel, title, label, cant_serv):
    # Obtener número de líneas a graficar
	num_lines = len(valores_x_validos)

    # Seleccionar una paleta de colores para las líneas válidas
	colores_validos = plt.get_cmap('tab10', num_lines)
	contador = 0
    # Graficar líneas válidas
	for i in cant_serv:
		plt.plot(valores_x_validos[contador], valores_y_validos[contador], marker='o', linestyle='-', color=colores_validos(contador), label= i )
		contador += 1
    # # Graficar líneas inválidas
    # plt.plot(valores_x_invalidos, valores_y_invalidos, marker='o', linestyle='-', color='red', label=f'{label} (Invalido)')

    # Configuración adicional del gráfico
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.grid(True)
	plt.legend(title = label)
	plt.show()

def simular_demanda(tiempo, horas_pico, demanda_pico, ancho_pico, minima_demanda):
    """
    Simula la demanda de trenes a lo largo del día.

    Retorna:
    - demand: Array de demanda simulada para cada hora del día.
    """
    demand = np.full_like(tiempo, minima_demanda, dtype=float)

    for hora, alto, ancho in zip(horas_pico, demanda_pico, ancho_pico):
        demand += alto * np.exp(-0.5 * ((tiempo - hora) / ancho) ** 2)

    demand = np.round(demand).astype(int)

    return demand



def main():
	EXPERIMENTACION = False
 
	if not EXPERIMENTACION:
		print("Elegi una instancia:")
		instance = int(input(" Instancia 1: Toy instance \n Instancia 2: Cronograma real \n Instancia 3: Random Generated Instance\n"))

		if(instance <= 2):

			#ejercicio: algoritmo e implementacion
			if(instance == 1):
				filename = "instances/toy_instance.json"

			#ejercicio: datos parte real
			else:
				filename = "instances/retiro-tigre-semana.json"

			data = getDatafromPath(filename)

		#ejercicio: datos parte de generar cronogramas
		else:
			numero_servicios = int(input("Elegi una cantidad de servicios: "))
			numero_estaciones = int(input("Elegi cantidad de estaciones: "))
			data = generate_random_json(num_services=numero_servicios, num_stations=numero_estaciones,seed=42)

		reduccion = int(input("Hay problemas de mantenimiento? \n1: SI \n2: NO\n"))

		REDUCCION_CAPACIDAD_TRASNOCHE = (0,"0Station")

		#ejercicio: escenario adicional
		if(reduccion == 1):

			estaciones = []
			for estacion in data["stations"]:
				estaciones.append(estacion)

			print(estaciones)
			print(f"Capacidad Actual: {data["rs_info"]["max_rs"]}")
			nombre_estacion = input("Escriba el nombre de la estacion que tendra una reduccion: ")
			num_reduccion = int(input("Indique la reduccion de la cantidad de unidades en la cabecera: "))
			REDUCCION_CAPACIDAD_TRASNOCHE = (num_reduccion,nombre_estacion)

		G = generateGraph(data,REDUCCION_CAPACIDAD_TRASNOCHE)

		flowDict = nx.min_cost_flow(G)

		vagones_totales(flowDict, data, G)

		costo_minimo(flowDict,G)

		printGraph(G,data,flowDict)

		costo = getFlowCost(flowDict, G)

		print(f"Vagones total: {costo}")

	else:
		######################### EXPERIMENTACION #########################

		########## Generar la demanda
  
		# Configuración (esta configuracion se modifica para ver comon impacta la demanda)
		time = np.linspace(0, 24, 24)  # Horas del día de 0 a 24 en intervalos de 1 hora
		peak_hours = [7, 12, 19]         # Horas pico
		peak_heights = [1200, 900, 1500]      # Altura de los picos de demanda
		peak_widths = [1, 2, 1]          # Anchura de los picos (más pequeño = menos horas de horario pico)
		base_demand = 600                 # Demanda base mínima

		# Simulación de demanda
		demand = simular_demanda(time, peak_hours, peak_heights, peak_widths, base_demand)

		# Graficar la demanda vs tiempo par ver con que demnada estamos dealing with
		plt.figure(figsize=(10, 6))
		plt.plot(time, demand, label='Demanda simulada', marker='o', linestyle='-')
		plt.title('Simulación de Demanda de Trenes a lo largo del Día')
		plt.xlabel('Tiempo (horas del dia)')
		plt.ylabel('Demanda')
		plt.xticks(np.arange(0, 25, step=1))
		plt.grid(False)
		plt.legend()
		plt.show()

		########## Experimentación y acumulación de resultados
		cantidad_de_servicios = [5, 10, 20, 30, 40, 50]
  
		#si quere cada plot individual
		plot_individual_graphs = False
		plot_individual_grafos = False
	
		valores_x_validos_horarios = []
		valores_y_validos_horarios = []
	
		valores_x_validos_capacidad = []
		valores_y_validos_capacidad = []
		
		valores_x_validos_tiempo = []
		valores_y_validos_tiempo = []


		for cant_serv in cantidad_de_servicios:
			# Experimentación para horarios de circulación
			vxv, vyv, xinv, yinv = experimentacion_horarios_de_circulacion(demand, cant_serv, plot_individual_graphs, plot_individual_grafos)
			valores_x_validos_horarios.append(vxv)
			valores_y_validos_horarios.append(vyv)
			

			# Experimentación para capacidad de trenes
			vxv, vyv, xinv, yinv = experimentacion_capcidad_trenes(demand, cant_serv, plot_individual_graphs, plot_individual_grafos)
			valores_x_validos_capacidad.append(vxv)
			valores_y_validos_capacidad.append(vyv)
			

			# Experimentación para tiempo entre servicios
			vxv, vyv, xinv, yinv = experimentacion_tiempo_entre_servicios(demand, cant_serv, plot_individual_graphs, plot_individual_grafos)
			valores_x_validos_tiempo.append(vxv)
			valores_y_validos_tiempo.append(vyv)
			

		# Generar gráficos superpuestos con los diferentes cantidades de servicios 
		plot_superpuesto(valores_x_validos_horarios, valores_y_validos_horarios,
			"Cantidad total de horas de circulación de trenes (en un día)","Cantidad de Vagones",
			"Costo de tener trenes circulando más horas (en cantidad de vagones)", '# de servicios',cantidad_de_servicios)

		plot_superpuesto(valores_x_validos_capacidad, valores_y_validos_capacidad,
			"Capacidad de vagones (medido en personas)", "Cantidad de Vagones",
			"Costo de tener trenes de mayor capacidad", '# de servicios',cantidad_de_servicios)

		plot_superpuesto(valores_x_validos_tiempo, valores_y_validos_tiempo,
			"Tiempo mínimo entre servicios", "Cantidad de Vagones",
			"Variación del costo según el tiempo entre servicios de trenes", '# de servicios',cantidad_de_servicios)


if __name__ == "__main__":
	main()