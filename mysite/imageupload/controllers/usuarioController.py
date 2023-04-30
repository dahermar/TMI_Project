import json
from django.conf import settings
from datetime import datetime
import pytz


class UsuarioController:

    def __init__(self):
        self.archivo_usuarios = settings.BASE_DIR / 'imageupload/json_db/usuarios.json'
        self.archivo_historial = settings.BASE_DIR / 'imageupload/json_db/historial.json'

    def cargar_usuarios(self):
        with open(self.archivo_usuarios) as f:
            data = json.load(f)
            return data['usuarios']
        
    def cargar_historial(self):
        with open(self.archivo_historial) as f:
            data = json.load(f)
            return data['usuarios']
        
    def agregar_usuario(self, nombre, foto_path):
        try:
            with open(self.archivo_usuarios, 'r') as archivo:
                data = json.load(archivo)

            next_user_id = data['next_id']
            # Crear un diccionario con las claves id, nombre y foto
            nuevo_usuario = {
                "id": next_user_id,
                "nombre": nombre,
                "foto": foto_path
            }
            # Incrementar next_id y guardar el nuevo valor en el archivo
            data['next_id'] = next_user_id + 1
            
            # Agregar el nuevo usuario a la lista de usuarios en el archivo
            data["usuarios"].append(nuevo_usuario)

            with open(self.archivo_usuarios, "w") as archivo:
                json.dump(data, archivo)

            #Historial

            with open(self.archivo_historial, 'r') as archivo:
                data = json.load(archivo)

            # Crear un diccionario con las claves id e historial
            nuevo_historial = {
                "id": next_user_id,
                "historial": []
            }
            
            data['usuarios'].append(nuevo_historial)

            with open(self.archivo_historial, "w") as archivo:
                json.dump(data, archivo)

            return True
        except Exception as e:
            print(e)
            return False

    def get_usuario(self):
        return None

    def agregar_registro(self, usuario_id, nombre):
        try:
            with open(self.archivo_historial, 'r') as archivo:
                data = json.load(archivo)

            next_id = data['next_id']
            # Crear un diccionario con las claves id, nombre y foto
            fecha = datetime.now(pytz.timezone('Europe/Madrid'))
            print(fecha)
            nuevo_registro = {
                "id": next_id,
                "animal": nombre,
                "fecha": str(fecha).split('.')[0]
            }
            # Incrementar next_id y guardar el nuevo valor en el archivo
            data['next_id'] = next_id + 1
            
            historial = self.get_registros_por_id(usuario_id=usuario_id)
            usuarios = self.cargar_historial()
            index = 0
            
            for usuario_tmp in usuarios:
                if usuario_tmp['id'] == usuario_id:
                    data['usuarios'][index]['historial'] = historial
                else: 
                    index +=1
            
            # Agregar el nuevo usuario a la lista de usuarios en el archivo
            historial.append(nuevo_registro)

            with open(self.archivo_historial, "w") as archivo:
                json.dump(data, archivo)
            
            return True
        except Exception as e:
            print(e)
            return False

    def get_registros_por_id(self, usuario_id):
        usuarios = self.cargar_historial()
        for usuario_tmp in usuarios:
            if usuario_tmp['id'] == usuario_id:
                usuario = usuario_tmp
                return usuario['historial']


