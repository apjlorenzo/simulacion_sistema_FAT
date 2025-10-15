import json
import os
from datetime import datetime

class SistemaFAT:
    def __init__(self):
        self.directorio_fat = "tabla_fat"
        self.directorio_bloques = "bloques_datos"
        self.usuarios = ["admin", "Pablo"]
        self.usuario_actual = "admin"

        os.makedirs(self.directorio_fat, exist_ok=True)
        os.makedirs(self.directorio_bloques, exist_ok=True)

    def crear_archivo(self, nombre, contenido, propietario=None):
        if propietario is None:
            propietario = self.usuario_actual

        if self.existe_archivo(nombre):
            return False, "El archivo ya existe"

        bloques = self.segmentar_contenido(contenido)
        ruta_inicial = self.guardar_bloques(nombre, bloques)

        entrada_fat = {
            "nombre": nombre,
            "ruta_inicial": ruta_inicial,
            "papelera": False,
            "cantidad_caracteres": len(contenido),
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_modificacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_eliminacion": None,
            "propietario": propietario,
            "permisos": {}
        }

        ruta_fat = os.path.join(self.directorio_fat, f"{nombre}.json")
        with open(ruta_fat, 'w', encoding='utf-8') as f:
            json.dump(entrada_fat, f, indent=2, ensure_ascii=False)

        return True, "Archivo creado exitosamente"

    def segmentar_contenido(self, contenido):
        bloques = []
        for i in range(0, len(contenido), 20):
            bloques.append(contenido[i:i+20])
        return bloques

    def guardar_bloques(self, nombre_archivo, bloques):
        rutas = []
        for i, bloque in enumerate(bloques):
            nombre_bloque = f"{nombre_archivo}_bloque_{i}.json"
            ruta_bloque = os.path.join(self.directorio_bloques, nombre_bloque)

            es_ultimo = (i == len(bloques) - 1)
            siguiente = None if es_ultimo else f"{nombre_archivo}_bloque_{i+1}.json"

            datos_bloque = {
                "datos": bloque,
                "siguiente_archivo": siguiente,
                "eof": es_ultimo
            }

            with open(ruta_bloque, 'w', encoding='utf-8') as f:
                json.dump(datos_bloque, f, indent=2, ensure_ascii=False)

            rutas.append(nombre_bloque)

        return rutas[0] if rutas else None

    def listar_archivos(self, incluir_papelera=False):
        archivos = []
        for archivo in os.listdir(self.directorio_fat):
            if archivo.endswith('.json'):
                ruta = os.path.join(self.directorio_fat, archivo)
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    if incluir_papelera or not datos.get('papelera', False):
                        archivos.append(datos)
        return archivos

    def obtener_archivo(self, nombre):
        ruta_fat = os.path.join(self.directorio_fat, f"{nombre}.json")
        if not os.path.exists(ruta_fat):
            return None
        with open(ruta_fat, 'r', encoding='utf-8') as f:
            return json.load(f)

    def leer_contenido(self, nombre, usuario):
        archivo = self.obtener_archivo(nombre)
        if not archivo:
            return None
        if not self.verificar_permiso(nombre, usuario, "lectura"):
            return None

        contenido = ""
        bloque_actual = archivo['ruta_inicial']

        while bloque_actual:
            ruta_bloque = os.path.join(self.directorio_bloques, bloque_actual)
            if not os.path.exists(ruta_bloque):
                break
            with open(ruta_bloque, 'r', encoding='utf-8') as f:
                datos_bloque = json.load(f)
                contenido += datos_bloque['datos']
                if datos_bloque['eof']:
                    break
                bloque_actual = datos_bloque['siguiente_archivo']

        return contenido

    def modificar_archivo(self, nombre, nuevo_contenido, usuario):
        archivo = self.obtener_archivo(nombre)
        if not archivo:
            return False, "Archivo no encontrado"
        if not self.verificar_permiso(nombre, usuario, "escritura"):
            return False, "No tienes permiso de escritura"

        self.eliminar_bloques(nombre, archivo['ruta_inicial'])
        bloques = self.segmentar_contenido(nuevo_contenido)
        nueva_ruta_inicial = self.guardar_bloques(nombre, bloques)

        archivo['ruta_inicial'] = nueva_ruta_inicial
        archivo['cantidad_caracteres'] = len(nuevo_contenido)
        archivo['fecha_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ruta_fat = os.path.join(self.directorio_fat, f"{nombre}.json")
        with open(ruta_fat, 'w', encoding='utf-8') as f:
            json.dump(archivo, f, indent=2, ensure_ascii=False)

        return True, "Archivo modificado exitosamente"

    def eliminar_bloques(self, nombre_archivo, bloque_inicial):
        bloque_actual = bloque_inicial
        while bloque_actual:
            ruta_bloque = os.path.join(self.directorio_bloques, bloque_actual)
            if not os.path.exists(ruta_bloque):
                break
            with open(ruta_bloque, 'r', encoding='utf-8') as f:
                datos_bloque = json.load(f)
                es_ultimo = datos_bloque['eof']
                siguiente = datos_bloque['siguiente_archivo']
            os.remove(ruta_bloque)
            if es_ultimo:
                break
            bloque_actual = siguiente

    def eliminar_archivo(self, nombre):
        archivo = self.obtener_archivo(nombre)
        if not archivo:
            return False, "Archivo no encontrado"

        archivo['papelera'] = True
        archivo['fecha_eliminacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ruta_fat = os.path.join(self.directorio_fat, f"{nombre}.json")
        with open(ruta_fat, 'w', encoding='utf-8') as f:
            json.dump(archivo, f, indent=2, ensure_ascii=False)

        return True, "Archivo movido a la papelera"

    def recuperar_archivo(self, nombre):
        archivo = self.obtener_archivo(nombre)
        if not archivo:
            return False, "Archivo no encontrado"

        archivo['papelera'] = False
        archivo['fecha_eliminacion'] = None

        ruta_fat = os.path.join(self.directorio_fat, f"{nombre}.json")
        with open(ruta_fat, 'w', encoding='utf-8') as f:
            json.dump(archivo, f, indent=2, ensure_ascii=False)

        return True, "Archivo recuperado exitosamente"

    def existe_archivo(self, nombre):
        ruta_fat = os.path.join(self.directorio_fat, f"{nombre}.json")
        return os.path.exists(ruta_fat)

    def asignar_permisos(self, nombre_archivo, usuario, lectura, escritura):
        archivo = self.obtener_archivo(nombre_archivo)
        if not archivo:
            return False, "Archivo no encontrado"
        if archivo['propietario'] != self.usuario_actual and self.usuario_actual != "admin":
            return False, "Solo el propietario puede asignar permisos"

        if 'permisos' not in archivo:
            archivo['permisos'] = {}

        archivo['permisos'][usuario] = {"lectura": lectura, "escritura": escritura}

        ruta_fat = os.path.join(self.directorio_fat, f"{nombre_archivo}.json")
        with open(ruta_fat, 'w', encoding='utf-8') as f:
            json.dump(archivo, f, indent=2, ensure_ascii=False)

        return True, "Permisos asignados correctamente"

    def verificar_permiso(self, nombre_archivo, usuario, tipo_permiso):
        archivo = self.obtener_archivo(nombre_archivo)
        if not archivo:
            return False
        if usuario == "admin" or archivo['propietario'] == usuario:
            return True
        permisos = archivo.get('permisos', {})
        if usuario not in permisos:
            return False
        return permisos[usuario].get(tipo_permiso, False)
