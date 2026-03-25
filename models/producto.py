# models/producto.py
# Modelo de Producto

class Producto:
    """Clase Producto para representar productos en el sistema"""
    
    def __init__(self, id_producto=None, nombre="", precio=0.0, stock=0, descripcion=""):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.descripcion = descripcion
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'precio': self.precio,
            'stock': self.stock,
            'descripcion': self.descripcion
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un Producto desde un diccionario"""
        return Producto(
            id_producto=data.get('id_producto'),
            nombre=data.get('nombre', ''),
            precio=data.get('precio', 0),
            stock=data.get('stock', 0),
            descripcion=data.get('descripcion', '')
        )
