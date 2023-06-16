import os
import re
from datetime import datetime
from flask import session

#hagoMerge = True
archivoResultados = "resultadosAlgunValor.txt"
archivosResultadosCoincidenciaCompleta = "resultadosTodosLosValores.txt"
archivoParaMergearResultadosPorFecha = "integracionResultadosVariosLogs.txt"

textosEncontrados = {}

#carpeta="/home/rmoran/workspace/epagos-apps/epagos-vagrant/data/logs/"
#nombre = input("ingresar el nombre del archivo:")
#nombre = carpeta+nombre
#listaBusqueda = ['1635337193']
#listaBusqueda = ['1635337193','\d{2}:\d{2}:\d{2},\d{3}']
#listaFiltros = ['WARN','DEBUG']

frasesPorPrefijo = {}

listaPrefijo = []
prefijoLinea = "\d{2}:\d{2}:\d{2},\d{3}"
listaPrefijo.append(prefijoLinea)
#expRegHora= "\d{2}:\d{2}:\d{2}"
#expRebFecha= "\d{4}-\d{2}-\d{2}"
#listaBusqueda.append(expRegHora)
#listaBusqueda.append(expRebFecha)


def cargarArchivoParaMergearResultadosPorFecha(nombreArchivo):

	frasesPorPrefijo = {}
	parrafo = ""
	valorPrefijo = ""
	if os.path.isfile(nombreArchivo):
		archivo = open(nombreArchivo, "r")
		for linea in archivo.readlines():
			(resultado, palabra, match) = estaPalabra(listaPrefijo, linea)
			if resultado:
				if parrafo != "":
					frasesPorPrefijo[valorPrefijo] = parrafo
				parrafo = ""
				valorPrefijo = match.group()
			if parrafo == "":
				parrafo = linea
			else:
				parrafo = parrafo + " "+linea
		frasesPorPrefijo[valorPrefijo] = parrafo
		archivo.close()
	else:
		print(f"no se encuentra el archivo:  {nombreArchivo}")
	return frasesPorPrefijo

#se espera prefijos con formato  hh:mm:ss,XXX
def compararPrefijoHora(prefijo1, prefijo2):
	listaHoraCentesimos1 = prefijo1.split(",")
	listaHoraCentesimos2 = prefijo2.split(",")
	hora1 = datetime.strptime(listaHoraCentesimos1[0], "%X").time()
	hora2 = datetime.strptime(listaHoraCentesimos2[0], "%X").time()
	cent1 = int(listaHoraCentesimos1[1])
	cent2 = int(listaHoraCentesimos2[1])
	if hora1 > hora2:
		return 1
	else:
		if hora1 < hora2:
			return -1
		else:
			if hora1 == hora2 and cent1 > cent2:
				return 1
			else:
				if hora1 == hora2 and cent1 < cent2:
					return -1
				else:
					if hora1 == hora2 and cent1 == cent2:
						return 0
					else:
						return 0

def grabarArchivoParaMergearResultadosPorFecha(diccOrig,diccBusquedas,nombreArchivo):
	archivo = open(nombreArchivo, "w")
	esMayorOriginal = True
	for claveDiccOrig in diccOrig:
		if len(diccBusquedas) > 0:
			while esMayorOriginal and len(diccBusquedas) > 0:
				for claveDiccBusquedas in diccBusquedas:
					resultado = compararPrefijoHora(claveDiccOrig, claveDiccBusquedas)
					if resultado == -1:
						archivo.write(diccOrig[claveDiccOrig])
						esMayorOriginal = False
					else:
						if resultado == 1 or resultado == 0:
							archivo.write(diccBusquedas[claveDiccBusquedas])
							diccBusquedas.pop(claveDiccBusquedas)
							esMayorOriginal = True
					break
			if esMayorOriginal:
				archivo.write(diccOrig[claveDiccOrig])
			else:
				esMayorOriginal = True
		else:
			archivo.write(diccOrig[claveDiccOrig])
	for claveDiccBusquedas in diccBusquedas:
		archivo.write(diccBusquedas[claveDiccBusquedas])
	archivo.close()

def cantidadPalabras(frase):
    palabras = frase.split(" ");
    print(f" cantidad: {len(palabras)} lista palabras: {palabras} frase: {frase}")

def estaPalabra(listaBusqueda,frase):
	palabras  =[]
	matcheo = False
	for palabra in listaBusqueda:
		patron = re.compile(palabra.lower())
		match = patron.search(frase.lower())
		if match:
			palabras.append(palabra)
			matcheo = True
	return matcheo, palabras, match

def estaTodaLaLista(listaBusqueda,frase):
	for palabra in listaBusqueda:
		patron = re.compile(palabra.lower())
		match = patron.search(frase.lower())
		if match:
			continue
		else:
			return False
	return True

def estaTodaLaListaParrafo(listaBusqueda,parrafo):
	for palabra in listaBusqueda:
		patron = re.compile(palabra.lower())
		encontrado = False
		for clave in parrafo:
			match = patron.search(parrafo[clave].lower())
			if match:
				encontrado = True
				break
		if not encontrado:
			return False
	return True

def listaToString(lista):
	texto = ""
	for e in lista:
		texto = texto+" "+e
	return texto

def agregarPalabraCoincidente(palabra,listaPalabras):
	if palabra in listaPalabras:
		return
	else:
		listaPalabras.append(palabra)

def mostrarListaGrabar(textos,nombre,coincidencias,nombreArchivo):
	archivo = open(nombreArchivo, "a")
	archivo.write("Búsqueda en archivo: "+nombre+" Coincidencias: "+listaToString(coincidencias)+"\n")
	archivo.write("____________________________________________________________________________________________________________________________________________________________"+"\n")
	for clave in textos:
		print(f" {clave} {textos[clave]}")
		archivo.write(clave+" "+textos[clave]+"\n")
	archivo.write("____________________________________________________________________________________________________________________________________________________________" + "\n")
	archivo.close()

def lecturaArchivo(form):
	nombreArchivo = form.path.data+form.nombreArchivo.data
	hagoMerge = eval(form.merge.data)
	separador = form.separador.data
	listaBusqueda = form.valores.data.split(separador)
	listaFiltros = form.filtros.data.split(separador)
	if os.path.isfile(nombreArchivo):
		archivo = open(nombreArchivo,"r")
		nroLinea = 1
		frase = {}
		frasePorPrefijoBusqueda = {}
		todasLasCoincidencias = {}
		parrafo = ""
		valorPrefijo = ""

		for linea in archivo.readlines():
			(resultado,palabra,matchPrefijo) = estaPalabra(listaPrefijo, linea)
			if resultado:
				if parrafo != "":
					(resultadoFiltro, palabras, match) = estaPalabra(listaFiltros, parrafo)
					if not resultadoFiltro:
						if estaTodaLaListaParrafo(listaBusqueda, frase):
								mostrarListaGrabar(frase, nombreArchivo, listaBusqueda, archivosResultadosCoincidenciaCompleta)
								todasLasCoincidencias[valorPrefijo] = listaBusqueda
								frasePorPrefijoBusqueda[valorPrefijo] = parrafo
						else:
							(resultadoBusqueda, palabras, match) = estaPalabra(listaBusqueda, parrafo)
							if resultadoBusqueda:
								todasLasCoincidencias[valorPrefijo] = palabras
								mostrarListaGrabar(frase, nombreArchivo, palabras, archivoResultados)
								frasePorPrefijoBusqueda[valorPrefijo] = parrafo

				valorPrefijo = matchPrefijo.group()
				frase = {}
				parrafo = ""
			if valorPrefijo != "":
				frase[str(nroLinea)] = linea
				if parrafo == "":
					# parrafo = str(nroLinea)+" "+linea
					parrafo = linea
				else:
					# parrafo = parrafo + " "+str(nroLinea)+" "+linea
					parrafo = parrafo + " " + linea
			nroLinea = nroLinea+1
		archivo.close()
		if hagoMerge:
			nombreArchivoMerge = form.pathArchivoMerge.data + form.nombreArchivoMerge.data
			frasesPorPrefijo = cargarArchivoParaMergearResultadosPorFecha(archivoParaMergearResultadosPorFecha)
			grabarArchivoParaMergearResultadosPorFecha(frasePorPrefijoBusqueda, frasesPorPrefijo, nombreArchivoMerge)
		if not frasePorPrefijoBusqueda:
			session["mensaje"] = "Sin resultados: " + "valores: "+str(listaBusqueda)+" filtros: "+str(listaFiltros)+" archivo log: "+nombreArchivo
			return False, {}, {}
		else:
			return True, frasePorPrefijoBusqueda, todasLasCoincidencias
	else:
		print(f"no se encuentra el archivo:  {nombreArchivo}")
		session["mensaje"] = " No se encuentra el archivo: "+nombreArchivo
	return False, {}, {}



