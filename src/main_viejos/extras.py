###cosas que no terminamos usando 


	# ## esto no funciona
	# peaks = [7,12,19]
	# peak_heights = [[800,900,800],[400,200,300],[200,300,400]]
	# can_serviclub = 20
	# #diferetnes cantidad de vagones necesarios para las peaks de las diferentes demandas
	# resultados_cantidad_de_vagones = []
	# avg_peaks = []
	# for peaks in peak_heights:
	# 	resultados_cantidad_de_vagones.append(experimentacion_demanda(peak_heights,peaks,can_serviclub))
	# 	avg_peaks.append(sum(peaks) / len(peaks))


    # # Graficar los resultados
	# plt.plot(avg_peaks, resultados_cantidad_de_vagones, marker='o', linestyle='-')


	# # Añadir etiquetas y título
	# plt.xlabel("El promedio de demanda mas alta")
	# plt.ylabel("Cantidad de vagones")
	# plt.title("Como las horas pico inlfuyen en la demanda")
	# plt.legend()

	# # Mostrar el gráfico
	# plt.show()



###### parte guidp


	# # Lista de valores de x que queremos probar
	# valores_x = range(0, 1000,50)
	# resultados = []

	# REDUCCION_CAPACIDAD_TRASNOCHE = (0,"0Station")

	# for x in valores_x:
	# 	try:
	# 		data = generate_random_json2(num_services=4, num_stations=2,demand_value = x,seed=42)
	# 		G = generateGraph(data,REDUCCION_CAPACIDAD_TRASNOCHE)
	# 		flowDict = nx.min_cost_flow(G)
	# 		vagones_totales(flowDict, data, G)
	# 		costo = getFlowCost(flowDict, G)

	# 		resultados.append((x, costo, True))  # El tercer elemento indica que no hubo error
	# 	except Exception as e:
	# 		print(f"Error para x = {x}: {e}")
	# 		resultados.append((x, None, False))  # El tercer elemento indica que hubo error

	# # Separar los resultados válidos y los que rompieron
	# valores_x_validos = [x for x, res, valid in resultados if valid]
	# valores_y_validos = [res for x, res, valid in resultados if valid]

	# valores_x_invalidos = [x for x, res, valid in resultados if not valid]
	# valores_y_invalidos = [0 for x, res, valid in resultados if not valid]  # Poner en 0 o algún valor placeholder

	# # Graficar los resultados
	# plt.plot(valores_x_validos, valores_y_validos, marker='o', linestyle='-', label='Valores válidos')
	# plt.scatter(valores_x_invalidos, valores_y_invalidos, color='red', marker='x', label='Errores')

	# # Añadir etiquetas y título
	# plt.xlabel('x')
	# plt.ylabel('mi_funcion(x)')
	# plt.title('Resultados de mi_funcion')
	# plt.legend()

	# # Mostrar el gráfico
	# plt.show()

def experimentacion_demanda(peak_heights, peak_hours, cantidad_serv):

    # Configuración (esta configurwacion deberia modificarse para ver comon impacta la demanda)
	time = np.linspace(4, 24, cantidad_serv)  # Horas del día de 0 a 24 en intervalos de 1 hora
	peak_hours = [7, 12, 19]         # Horas pico
	peak_heights = [800, 900, 800]      # Altura de los picos de demanda
	peak_widths = [1, 1, 1]          # Anchura de los picos (más pequeño = menos horas de horario pico)
	base_demand = 500                 # Demanda base mínima

	# Simulación de demanda
	demand = simular_demanda(time, peak_hours, peak_heights, peak_widths, base_demand)

	# Graficar la demanda vs tiempo par ver con que demnada estamos dealing with
	plt.figure(figsize=(10, 6))
	plt.plot(time, demand, label='Demanda simulada', marker='o', linestyle='-')
	plt.title('Simulación de Demanda de Trenes a lo largo del Día')
	plt.xlabel('Tiempo (horas)')
	plt.ylabel('Demanda')
	plt.xticks(np.arange(0, 25, step=1))
	plt.grid(False)
	plt.legend()
	plt.show()

	REDUCCION_CAPACIDAD_TRASNOCHE = (0,"0Station")

	data = generate_random_json(
				num_services=cantidad_serv,
				num_stations=2,
				max_time= 1440, # 1440 minutos === 60*24 minutos === 1 dia
				demand_per_hour=demand,
				capacity=100,
				max_rs=50,
				time_between_services = 60,
				cost_per_unit = 1.0,
				seed = 42
		)

	try:
		G = generateGraph(data,REDUCCION_CAPACIDAD_TRASNOCHE)
		flowDict = nx.min_cost_flow(G)

		costo = getFlowCost(flowDict, G)
		# printGraph(G, data, flowDict)

	except Exception as e:
		pass

	return costo
