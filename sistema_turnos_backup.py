# sistema_turnos.py
# Sistema de Gestión de Turnos - Interfaz de Consola
# Patronato de Catacocha

import os
import sys
from datetime import datetime
from models import Paciente, Medico, Turno, InventarioTurnos
from database import crear_base_datos, insertar_datos_prueba

class SistemaTurnosConsole:
    """Clase principal del sistema con interfaz de consola"""
    
    def __init__(self):
        self.inventario = None
        self.inicializar_sistema()
    
    def inicializar_sistema(self):
        """Inicializa la base de datos y carga el inventario"""
        print("\n" + "="*60)
        print("🏛️  SISTEMA DE GESTIÓN DE TURNOS - PATRONATO DE CATACOCHA")
        print("="*60)
        
        # Crear base de datos si no existe
        crear_base_datos()
        
        # Verificar si existe el archivo de base de datos
        if not os.path.exists('turnos.db'):
            respuesta = input("¿Desea insertar datos de prueba? (s/n): ")
            if respuesta.lower() == 's':
                insertar_datos_prueba()
        
        # Cargar inventario
        self.inventario = InventarioTurnos()
        print("✅ Sistema inicializado correctamente")
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pausar(self):
        """Pausa la ejecución hasta que el usuario presione Enter"""
        input("\nPresione Enter para continuar...")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema"""
        self.limpiar_pantalla()
        print("\n" + "="*60)
        print("🏛️  PATRONATO DE CATACOCHA - SISTEMA DE TURNOS")
        print("="*60)
        print("\n📌 MENÚ PRINCIPAL:")
        print("  1. 👥 Gestión de Pacientes")
        print("  2. 👨‍⚕️ Gestión de Médicos")
        print("  3. 📅 Gestión de Turnos")
        print("  4. 📊 Reportes y Estadísticas")
        print("  5. 🗄️  Mostrar Todo el Inventario")
        print("  6. ❌ Salir")
        print("-"*60)
    
    def menu_pacientes(self):
        """Menú de gestión de pacientes"""
        while True:
            self.limpiar_pantalla()
            print("\n" + "="*60)
            print("👥 GESTIÓN DE PACIENTES")
            print("="*60)
            print("\n  1. ➕ Registrar nuevo paciente")
            print("  2. 🔍 Buscar pacientes")
            print("  3. 📋 Listar todos los pacientes")
            print("  4. ✏️  Actualizar paciente")
            print("  5. ❌ Eliminar paciente")
            print("  6. 🔙 Volver al menú principal")
            print("-"*60)
            
            opcion = input("Seleccione una opción (1-6): ")
            
            if opcion == '1':
                self.registrar_paciente()
            elif opcion == '2':
                self.buscar_pacientes()
            elif opcion == '3':
                self.listar_pacientes()
            elif opcion == '4':
                self.actualizar_paciente()
            elif opcion == '5':
                self.eliminar_paciente()
            elif opcion == '6':
                break
            else:
                print("❌ Opción inválida")
                self.pausar()
    
    def registrar_paciente(self):
        """Registra un nuevo paciente"""
        self.limpiar_pantalla()
        print("\n📝 REGISTRO DE NUEVO PACIENTE")
        print("-"*40)
        
        cedula = input("Cédula: ")
        nombre = input("Nombres: ")
        apellido = input("Apellidos: ")
        fecha_nac = input("Fecha de nacimiento (YYYY-MM-DD) [opcional]: ") or None
        telefono = input("Teléfono [opcional]: ") or ""
        direccion = input("Dirección [opcional]: ") or ""
        email = input("Email [opcional]: ") or ""
        
        paciente = Paciente(
            cedula=cedula,
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=fecha_nac,
            telefono=telefono,
            direccion=direccion,
            email=email
        )
        
        paciente_id = self.inventario.agregar_paciente(paciente)
        if paciente_id:
            print(f"\n✅ Paciente registrado con ID: {paciente_id}")
        
        self.pausar()
    
    def buscar_pacientes(self):
        """Busca pacientes por criterio"""
        self.limpiar_pantalla()
        print("\n🔍 BÚSQUEDA DE PACIENTES")
        print("-"*40)
        
        criterio = input("Ingrese nombre o cédula a buscar: ")
        resultados = self.inventario.buscar_paciente(criterio)
        
        if resultados:
            print(f"\n📋 Se encontraron {len(resultados)} paciente(s):")
            for p in resultados:
                print(f"\n  ID: {p.id}")
                print(f"  Nombre: {p.nombre_completo()}")
                print(f"  Cédula: {p.cedula}")
                print(f"  Teléfono: {p.telefono}")
                print(f"  Edad: {p.edad()} años")
        else:
            print("\n❌ No se encontraron pacientes")
        
        self.pausar()
    
    def listar_pacientes(self):
        """Lista todos los pacientes"""
        self.limpiar_pantalla()
        print("\n📋 LISTA DE PACIENTES")
        print("-"*60)
        
        if self.inventario.pacientes:
            for paciente in self.inventario.pacientes.values():
                print(f"\n  ID: {paciente.id}")
                print(f"  Nombre: {paciente.nombre_completo()}")
                print(f"  Cédula: {paciente.cedula}")
                print(f"  Teléfono: {paciente.telefono}")
                print(f"  Turnos: {len(self.inventario.buscar_turnos_por_paciente(paciente.id))}")
                print("-"*30)
        else:
            print("  No hay pacientes registrados")
        
        self.pausar()
    
    def actualizar_paciente(self):
        """Actualiza datos de un paciente"""
        self.limpiar_pantalla()
        print("\n✏️  ACTUALIZAR PACIENTE")
        print("-"*40)
        
        try:
            paciente_id = int(input("Ingrese ID del paciente: "))
            if paciente_id not in self.inventario.pacientes:
                print("❌ Paciente no encontrado")
                self.pausar()
                return
            
            paciente = self.inventario.pacientes[paciente_id]
            
            print(f"\nPaciente actual: {paciente.nombre_completo()}")
            print("Deje en blanco para mantener el valor actual")
            
            cedula = input(f"Cédula [{paciente.cedula}]: ") or paciente.cedula
            nombre = input(f"Nombres [{paciente.nombre}]: ") or paciente.nombre
            apellido = input(f"Apellidos [{paciente.apellido}]: ") or paciente.apellido
            fecha_nac = input(f"Fecha nacimiento [{paciente.fecha_nacimiento}]: ") or paciente.fecha_nacimiento
            telefono = input(f"Teléfono [{paciente.telefono}]: ") or paciente.telefono
            direccion = input(f"Dirección [{paciente.direccion}]: ") or paciente.direccion
            email = input(f"Email [{paciente.email}]: ") or paciente.email
            
            paciente_actualizado = Paciente(
                id=paciente_id,
                cedula=cedula,
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nac,
                telefono=telefono,
                direccion=direccion,
                email=email
            )
            
            self.inventario.actualizar_paciente(paciente_actualizado)
        except ValueError:
            print("❌ ID inválido")
        
        self.pausar()
    
    def eliminar_paciente(self):
        """Elimina un paciente"""
        self.limpiar_pantalla()
        print("\n❌ ELIMINAR PACIENTE")
        print("-"*40)
        
        try:
            paciente_id = int(input("Ingrese ID del paciente: "))
            if paciente_id in self.inventario.pacientes:
                paciente = self.inventario.pacientes[paciente_id]
                print(f"\nPaciente: {paciente.nombre_completo()}")
                
                # Verificar turnos
                turnos = self.inventario.buscar_turnos_por_paciente(paciente_id)
                if turnos:
                    print(f"⚠️  Este paciente tiene {len(turnos)} turno(s) programados")
                
                confirmar = input("¿Está seguro de eliminar? (s/n): ")
                if confirmar.lower() == 's':
                    self.inventario.eliminar_paciente(paciente_id)
            else:
                print("❌ Paciente no encontrado")
        except ValueError:
            print("❌ ID inválido")
        
        self.pausar()
    
    def menu_medicos(self):
        """Menú de gestión de médicos"""
        while True:
            self.limpiar_pantalla()
            print("\n" + "="*60)
            print("👨‍⚕️ GESTIÓN DE MÉDICOS")
            print("="*60)
            print("\n  1. ➕ Registrar nuevo médico")
            print("  2. 🔍 Buscar médicos")
            print("  3. 📋 Listar todos los médicos")
            print("  4. 🔙 Volver al menú principal")
            print("-"*60)
            
            opcion = input("Seleccione una opción (1-4): ")
            
            if opcion == '1':
                self.registrar_medico()
            elif opcion == '2':
                self.buscar_medicos()
            elif opcion == '3':
                self.listar_medicos()
            elif opcion == '4':
                break
            else:
                print("❌ Opción inválida")
                self.pausar()
    
    def registrar_medico(self):
        """Registra un nuevo médico"""
        self.limpiar_pantalla()
        print("\n📝 REGISTRO DE NUEVO MÉDICO")
        print("-"*40)
        
        cedula = input("Cédula: ")
        nombre = input("Nombres: ")
        apellido = input("Apellidos: ")
        
        print("\nEspecialidades disponibles:")
        for i, esp in enumerate(Medico.ESPECIALIDADES, 1):
            print(f"  {i}. {esp}")
        
        try:
            esp_opcion = int(input("\nSeleccione especialidad (1-8): "))
            especialidad = Medico.ESPECIALIDADES[esp_opcion - 1]
        except:
            especialidad = "Medicina General"
            print(f"Opción inválida. Se asignó: {especialidad}")
        
        telefono = input("Teléfono [opcional]: ") or ""
        email = input("Email [opcional]: ") or ""
        
        # Insertar directamente en la base de datos
        import sqlite3
        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO medicos (cedula, nombre, apellido, especialidad, telefono, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cedula, nombre, apellido, especialidad, telefono, email))
            
            conn.commit()
            medico_id = cursor.lastrowid
            print(f"✅ Médico registrado con ID: {medico_id}")
            
            # Recargar inventario para incluir el nuevo médico
            self.inventario.cargar_datos()
            
        except sqlite3.Error as e:
            print(f"❌ Error al registrar médico: {e}")
        finally:
            conn.close()
        
        self.pausar()
    
    def buscar_medicos(self):
        """Busca médicos por criterio"""
        self.limpiar_pantalla()
        print("\n🔍 BÚSQUEDA DE MÉDICOS")
        print("-"*40)
        
        criterio = input("Ingrese nombre o especialidad a buscar: ").lower()
        
        resultados = [
            m for m in self.inventario.medicos.values()
            if criterio in m.nombre.lower() or 
               criterio in m.apellido.lower() or 
               criterio in m.especialidad.lower()
        ]
        
        if resultados:
            print(f"\n📋 Se encontraron {len(resultados)} médico(s):")
            for m in resultados:
                print(f"\n  ID: {m.id}")
                print(f"  Nombre: {m.nombre_completo()}")
                print(f"  Especialidad: {m.especialidad}")
                print(f"  Teléfono: {m.telefono}")
        else:
            print("\n❌ No se encontraron médicos")
        
        self.pausar()
    
    def listar_medicos(self):
        """Lista todos los médicos"""
        self.limpiar_pantalla()
        print("\n📋 LISTA DE MÉDICOS")
        print("-"*60)
        
        if self.inventario.medicos:
            for medico in self.inventario.medicos.values():
                print(f"\n  ID: {medico.id}")
                print(f"  Nombre: {medico.nombre_completo()}")
                print(f"  Especialidad: {medico.especialidad}")
                print(f"  Teléfono: {medico.telefono}")
                print("-"*30)
        else:
            print("  No hay médicos registrados")
        
        self.pausar()
    
    def menu_turnos(self):
        """Menú de gestión de turnos"""
        while True:
            self.limpiar_pantalla()
            print("\n" + "="*60)
            print("📅 GESTIÓN DE TURNOS")
            print("="*60)
            print("\n  1. ➕ Agendar nuevo turno")
            print("  2. 🔍 Buscar turnos por fecha")
            print("  3. 🔍 Buscar turnos por paciente")
            print("  4. 📋 Listar todos los turnos")
            print("  5. ✏️  Actualizar estado de turno")
            print("  6. ❌ Cancelar turno")
            print("  7. 🔙 Volver al menú principal")
            print("-"*60)
            
            opcion = input("Seleccione una opción (1-7): ")
            
            if opcion == '1':
                self.agendar_turno()
            elif opcion == '2':
                self.buscar_turnos_por_fecha()
            elif opcion == '3':
                self.buscar_turnos_por_paciente()
            elif opcion == '4':
                self.listar_turnos()
            elif opcion == '5':
                self.actualizar_estado_turno()
            elif opcion == '6':
                self.cancelar_turno()
            elif opcion == '7':
                break
            else:
                print("❌ Opción inválida")
                self.pausar()
    
    def agendar_turno(self):
        """Agenda un nuevo turno"""
        self.limpiar_pantalla()
        print("\n📝 AGENDAR NUEVO TURNO")
        print("-"*40)
        
        # Verificar si hay pacientes
        if not self.inventario.pacientes:
            print("❌ No hay pacientes registrados")
            self.pausar()
            return
        
        # Mostrar lista de pacientes (primeros 5)
        print("\nPacientes disponibles (mostrando primeros 5):")
        pacientes_lista = list(self.inventario.pacientes.values())[:5]
        for paciente in pacientes_lista:
            print(f"  {paciente.id}: {paciente.nombre_completo()}")
        
        try:
            paciente_id = int(input("\nID del paciente: "))
            if paciente_id not in self.inventario.pacientes:
                print("❌ Paciente no encontrado")
                self.pausar()
                return
            
            # Verificar si hay médicos
            if not self.inventario.medicos:
                print("❌ No hay médicos registrados")
                self.pausar()
                return
            
            # Mostrar médicos
            print("\nMédicos disponibles:")
            for medico in self.inventario.medicos.values():
                print(f"  {medico.id}: {medico.nombre_completo()} - {medico.especialidad}")
            
            medico_id = int(input("ID del médico: "))
            if medico_id not in self.inventario.medicos:
                print("❌ Médico no encontrado")
                self.pausar()
                return
            
            fecha = input("Fecha (YYYY-MM-DD): ")
            hora = input("Hora (HH:MM): ")
            motivo = input("Motivo de la consulta: ")
            
            turno = Turno(
                paciente_id=paciente_id,
                medico_id=medico_id,
                fecha=fecha,
                hora=hora,
                motivo=motivo,
                estado="Programado"
            )
            
            turno_id = self.inventario.agregar_turno(turno)
            if turno_id:
                print(f"\n✅ Turno agendado con ID: {turno_id}")
            
        except ValueError:
            print("❌ Error en el formato de los datos")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        self.pausar()
    
    def buscar_turnos_por_fecha(self):
        """Busca turnos por fecha"""
        self.limpiar_pantalla()
        print("\n🔍 BÚSQUEDA DE TURNOS POR FECHA")
        print("-"*40)
        
        fecha = input("Ingrese fecha (YYYY-MM-DD): ")
        resultados = self.inventario.buscar_turnos_por_fecha(fecha)
        
        if resultados:
            print(f"\n📋 Turnos para {fecha}:")
            for turno in resultados:
                paciente = self.inventario.pacientes.get(turno.paciente_id)
                medico = self.inventario.medicos.get(turno.medico_id)
                print(f"\n  ID: {turno.id}")
                print(f"  Hora: {turno.hora}")
                print(f"  Paciente: {paciente.nombre_completo() if paciente else 'N/A'}")
                print(f"  Médico: {medico.nombre_completo() if medico else 'N/A'}")
                print(f"  Estado: {turno.estado}")
        else:
            print(f"\n❌ No hay turnos para la fecha {fecha}")
        
        self.pausar()
    
    def buscar_turnos_por_paciente(self):
        """Busca turnos por paciente"""
        self.limpiar_pantalla()
        print("\n🔍 BÚSQUEDA DE TURNOS POR PACIENTE")
        print("-"*40)
        
        try:
            paciente_id = int(input("Ingrese ID del paciente: "))
            resultados = self.inventario.buscar_turnos_por_paciente(paciente_id)
            
            if resultados:
                paciente = self.inventario.pacientes.get(paciente_id)
                print(f"\n📋 Turnos para {paciente.nombre_completo() if paciente else 'Paciente'}:")
                for turno in resultados:
                    medico = self.inventario.medicos.get(turno.medico_id)
                    print(f"\n  ID: {turno.id}")
                    print(f"  Fecha: {turno.fecha} {turno.hora}")
                    print(f"  Médico: {medico.nombre_completo() if medico else 'N/A'}")
                    print(f"  Estado: {turno.estado}")
            else:
                print(f"\n❌ No hay turnos para el paciente ID {paciente_id}")
        except ValueError:
            print("❌ ID inválido")
        
        self.pausar()
    
    def listar_turnos(self):
        """Lista todos los turnos"""
        self.limpiar_pantalla()
        print("\n📋 LISTA DE TURNOS")
        print("-"*60)
        
        if self.inventario.turnos:
            # Ordenar turnos por fecha y hora
            turnos_ordenados = sorted(
                self.inventario.turnos.values(),
                key=lambda t: (t.fecha, t.hora)
            )
            
            for turno in turnos_ordenados[:10]:  # Mostrar solo primeros 10
                paciente = self.inventario.pacientes.get(turno.paciente_id)
                medico = self.inventario.medicos.get(turno.medico_id)
                
                print(f"\n  ID: {turno.id}")
                print(f"  Fecha: {turno.fecha} {turno.hora}")
                print(f"  Paciente: {paciente.nombre_completo() if paciente else 'N/A'}")
                print(f"  Médico: {medico.nombre_completo() if medico else 'N/A'}")
                print(f"  Estado: {turno.estado}")
                print("-"*30)
            
            if len(self.inventario.turnos) > 10:
                print(f"... y {len(self.inventario.turnos) - 10} turno(s) más")
        else:
            print("  No hay turnos registrados")
        
        self.pausar()
    
    def actualizar_estado_turno(self):
        """Actualiza el estado de un turno"""
        self.limpiar_pantalla()
        print("\n✏️  ACTUALIZAR ESTADO DE TURNO")
        print("-"*40)
        
        try:
            turno_id = int(input("Ingrese ID del turno: "))
            if turno_id not in self.inventario.turnos:
                print("❌ Turno no encontrado")
                self.pausar()
                return
            
            turno = self.inventario.turnos[turno_id]
            print(f"\nTurno actual: {turno.fecha} {turno.hora} - {turno.estado}")
            
            print("\nEstados disponibles:")
            for i, estado in enumerate(Turno.ESTADOS, 1):
                print(f"  {i}. {estado}")
            
            try:
                opcion = int(input("\nSeleccione nuevo estado (1-6): "))
                nuevo_estado = list(Turno.ESTADOS)[opcion - 1]
                self.inventario.actualizar_estado_turno(turno_id, nuevo_estado)
            except:
                print("❌ Opción inválida")
        
        except ValueError:
            print("❌ ID inválido")
        
        self.pausar()
    
    def cancelar_turno(self):
        """Cancela un turno"""
        self.limpiar_pantalla()
        print("\n❌ CANCELAR TURNO")
        print("-"*40)
        
        try:
            turno_id = int(input("Ingrese ID del turno a cancelar: "))
            if turno_id in self.inventario.turnos:
                turno = self.inventario.turnos[turno_id]
                paciente = self.inventario.pacientes.get(turno.paciente_id)
                print(f"\nTurno: {turno.fecha} {turno.hora}")
                print(f"Paciente: {paciente.nombre_completo() if paciente else 'N/A'}")
                
                confirmar = input("¿Está seguro de cancelar? (s/n): ")
                if confirmar.lower() == 's':
                    self.inventario.cancelar_turno(turno_id)
            else:
                print("❌ Turno no encontrado")
        except ValueError:
            print("❌ ID inválido")
        
        self.pausar()
    
    def menu_reportes(self):
        """Menú de reportes y estadísticas"""
        while True:
            self.limpiar_pantalla()
            print("\n" + "="*60)
            print("📊 REPORTES Y ESTADÍSTICAS")
            print("="*60)
            
            # Mostrar estadísticas generales
            stats = self.inventario.estadisticas()
            print("\n📈 ESTADÍSTICAS GENERALES:")
            print(f"  Total pacientes: {stats['total_pacientes']}")
            print(f"  Total médicos: {stats['total_medicos']}")
            print(f"  Total turnos: {stats['total_turnos']}")
            print(f"  Próximos turnos: {stats['proximos_turnos']}")
            
            print("\n📊 TURNOS POR ESTADO:")
            for estado, cantidad in stats['turnos_por_estado'].items():
                print(f"  {estado}: {cantidad}")
            
            print("\n  1. 📋 Reporte de turnos por médico")
            print("  2. 🔙 Volver al menú principal")
            print("-"*60)
            
            opcion = input("Seleccione una opción (1-2): ")
            
            if opcion == '1':
                self.reporte_turnos_por_medico()
            elif opcion == '2':
                break
            else:
                print("❌ Opción inválida")
                self.pausar()
    
    def reporte_turnos_por_medico(self):
        """Genera reporte de turnos por médico"""
        self.limpiar_pantalla()
        print("\n📋 REPORTE DE TURNOS POR MÉDICO")
        print("-"*40)
        
        try:
            medico_id = int(input("Ingrese ID del médico: "))
            if medico_id not in self.inventario.medicos:
                print("❌ Médico no encontrado")
                self.pausar()
                return
            
            medico = self.inventario.medicos[medico_id]
            turnos = self.inventario.reporte_turnos_por_medico(medico_id)
            
            print(f"\n📊 Turnos para {medico.nombre_completo()}:")
            if turnos:
                for turno in turnos:
                    paciente = self.inventario.pacientes.get(turno.paciente_id)
                    print(f"\n  Fecha: {turno.fecha} {turno.hora}")
                    print(f"  Paciente: {paciente.nombre_completo() if paciente else 'N/A'}")
                    print(f"  Estado: {turno.estado}")
            else:
                print("  No hay turnos para este médico")
        
        except ValueError:
            print("❌ ID inválido")
        
        self.pausar()
    
    def mostrar_inventario_completo(self):
        """Muestra todo el inventario"""
        self.limpiar_pantalla()
        self.inventario.mostrar_todo()
        self.pausar()
    
    def ejecutar(self):
        """Ejecuta el bucle principal del sistema"""
        while True:
            self.mostrar_menu_principal()
            opcion = input("Seleccione una opción (1-6): ")
            
            if opcion == '1':
                self.menu_pacientes()
            elif opcion == '2':
                self.menu_medicos()
            elif opcion == '3':
                self.menu_turnos()
            elif opcion == '4':
                self.menu_reportes()
            elif opcion == '5':
                self.mostrar_inventario_completo()
            elif opcion == '6':
                print("\n👋 ¡Gracias por usar el Sistema de Turnos del Patronato!")
                break
            else:
                print("❌ Opción inválida")
                self.pausar()

if __name__ == "__main__":
    sistema = SistemaTurnosConsole()
    sistema.ejecutar()
