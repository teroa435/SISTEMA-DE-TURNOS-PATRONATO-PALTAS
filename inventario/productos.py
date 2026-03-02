# inventario/productos.py
# Modelos adicionales para productos

class Producto:
    '''Clase Producto para manejo en memoria'''
    
    def __init__(self, id=None, nombre='', descripcion='', precio=0.0, cantidad=0):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.cantidad = cantidad
    
    def to_dict(self):
        '''Convierte a diccionario'''
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'cantidad': self.cantidad
        }
    
    @classmethod
    def from_dict(cls, datos):
        '''Crea un producto desde un diccionario'''
        return cls(
            id=datos.get('id'),
            nombre=datos.get('nombre', ''),
            descripcion=datos.get('descripcion', ''),
            precio=float(datos.get('precio', 0)),
            cantidad=int(datos.get('cantidad', 0))
        )
    
    def __str__(self):
        return f"{self.nombre} -  - {self.cantidad} unidades"
