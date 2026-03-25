# services/producto_service.py
# Servicio para manejar operaciones CRUD de Productos

from conexion.conexion import get_db
from models.producto import Producto

class ProductoService:
    """Servicio para gestionar productos en la base de datos"""
    
    def __init__(self):
        self.db = get_db()
    
    def crear(self, producto):
        """Crea un nuevo producto"""
        query = """
            INSERT INTO productos (nombre, precio, stock, descripcion)
            VALUES (%s, %s, %s, %s)
        """
        params = (producto.nombre, producto.precio, producto.stock, producto.descripcion)
        resultado = self.db.execute_query(query, params)
        return resultado > 0
    
    def obtener_todos(self):
        """Obtiene todos los productos"""
        query = "SELECT * FROM productos ORDER BY id_producto DESC"
        resultados = self.db.fetch_all(query)
        return [Producto.from_dict(r) for r in resultados]
    
    def obtener_por_id(self, id_producto):
        """Obtiene un producto por su ID"""
        query = "SELECT * FROM productos WHERE id_producto = %s"
        resultado = self.db.fetch_one(query, (id_producto,))
        if resultado:
            return Producto.from_dict(resultado)
        return None
    
    def actualizar(self, producto):
        """Actualiza un producto existente"""
        query = """
            UPDATE productos 
            SET nombre=%s, precio=%s, stock=%s, descripcion=%s
            WHERE id_producto=%s
        """
        params = (producto.nombre, producto.precio, producto.stock, 
                  producto.descripcion, producto.id_producto)
        resultado = self.db.execute_query(query, params)
        return resultado > 0
    
    def eliminar(self, id_producto):
        """Elimina un producto por su ID"""
        query = "DELETE FROM productos WHERE id_producto = %s"
        resultado = self.db.execute_query(query, (id_producto,))
        return resultado > 0
    
    def obtener_reporte(self):
        """Obtiene todos los productos para reporte"""
        return self.obtener_todos()
