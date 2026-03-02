# inventario/inventario.py
# Clases para manejar persistencia con archivos TXT, JSON, CSV

import json
import csv
import os
from datetime import datetime

class PersistenciaTXT:
    '''Maneja la persistencia en archivos TXT'''
    
    def __init__(self, archivo='inventario/data/datos.txt'):
        self.archivo = archivo
        self.crear_directorio()
    
    def crear_directorio(self):
        '''Crea el directorio si no existe'''
        directorio = os.path.dirname(self.archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def guardar(self, datos):
        '''Guarda datos en archivo TXT'''
        try:
            with open(self.archivo, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {datos}\n")
            return True
        except Exception as e:
            print(f"Error guardando TXT: {e}")
            return False
    
    def leer(self):
        '''Lee datos del archivo TXT'''
        try:
            if not os.path.exists(self.archivo):
                return []
            with open(self.archivo, 'r', encoding='utf-8') as f:
                return [linea.strip() for linea in f.readlines()]
        except Exception as e:
            print(f"Error leyendo TXT: {e}")
            return []


class PersistenciaJSON:
    '''Maneja la persistencia en archivos JSON'''
    
    def __init__(self, archivo='inventario/data/datos.json'):
        self.archivo = archivo
        self.crear_directorio()
    
    def crear_directorio(self):
        '''Crea el directorio si no existe'''
        directorio = os.path.dirname(self.archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def guardar(self, datos):
        '''Guarda datos en archivo JSON'''
        try:
            # Leer datos existentes
            existentes = self.leer()
            if not isinstance(existentes, list):
                existentes = []
            
            # Agregar nuevos datos
            if isinstance(datos, dict):
                datos['fecha_registro'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                existentes.append(datos)
            elif isinstance(datos, list):
                for item in datos:
                    if isinstance(item, dict):
                        item['fecha_registro'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                existentes.extend(datos)
            
            # Guardar
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump(existentes, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando JSON: {e}")
            return False
    
    def leer(self):
        '''Lee datos del archivo JSON'''
        try:
            if not os.path.exists(self.archivo):
                return []
            with open(self.archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo JSON: {e}")
            return []


class PersistenciaCSV:
    '''Maneja la persistencia en archivos CSV'''
    
    def __init__(self, archivo='inventario/data/datos.csv'):
        self.archivo = archivo
        self.crear_directorio()
        self.crear_archivo_si_no_existe()
    
    def crear_directorio(self):
        '''Crea el directorio si no existe'''
        directorio = os.path.dirname(self.archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
    
    def crear_archivo_si_no_existe(self):
        '''Crea el archivo CSV con cabeceras si no existe'''
        if not os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['fecha', 'nombre', 'descripcion', 'precio', 'cantidad'])
            except Exception as e:
                print(f"Error creando CSV: {e}")
    
    def guardar(self, datos):
        '''Guarda datos en archivo CSV'''
        try:
            with open(self.archivo, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if isinstance(datos, dict):
                    writer.writerow([
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        datos.get('nombre', ''),
                        datos.get('descripcion', ''),
                        datos.get('precio', 0),
                        datos.get('cantidad', 0)
                    ])
                elif isinstance(datos, list):
                    for item in datos:
                        if isinstance(item, dict):
                            writer.writerow([
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                item.get('nombre', ''),
                                item.get('descripcion', ''),
                                item.get('precio', 0),
                                item.get('cantidad', 0)
                            ])
            return True
        except Exception as e:
            print(f"Error guardando CSV: {e}")
            return False
    
    def leer(self):
        '''Lee datos del archivo CSV'''
        try:
            if not os.path.exists(self.archivo):
                return []
            with open(self.archivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
        except Exception as e:
            print(f"Error leyendo CSV: {e}")
            return []
