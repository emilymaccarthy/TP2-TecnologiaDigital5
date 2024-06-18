from funciones import *

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