import json
from django.conf import settings


class UsuarioController:

    def __init__(self):
        self.archivo_usuarios = settings.BASE_DIR / 'imageupload/json_db/usuarios.json'

    def cargar_usuarios(self):
        with open(self.archivo_usuarios) as f:
            data = json.load(f)
            return data['usuarios']
        
    def agregar_usuario(self, nombre, foto_path):
        try:
            with open(self.archivo_usuarios, 'r') as archivo:
                data = json.load(archivo)

            next_id = data['next_id']
            # Crear un diccionario con las claves id, nombre y foto
            nuevo_usuario = {
                "id": next_id,
                "nombre": nombre,
                "foto": foto_path
            }
            # Incrementar next_id y guardar el nuevo valor en el archivo
            data['next_id'] = next_id + 1
            
            # Agregar el nuevo usuario a la lista de usuarios en el archivo
            data["usuarios"].append(nuevo_usuario)

            with open(self.archivo_usuarios, "w") as archivo:
                json.dump(data, archivo)
            
            return True
        except Exception as e:
            return False

    def get_usuario(self):
        return None

