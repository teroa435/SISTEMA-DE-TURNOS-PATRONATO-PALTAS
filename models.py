# models.py
# Clases para el Sistema de Citas del Patronato de Catacocha

from datetime import datetime
import sqlite3

class Paciente:
    '''Clase que representa a un paciente del Patronato'''

    def __init__(self, id=None, cedula="", nombre="", apellido="",
                 fecha_nacimiento="", telefono="", direccion="", email="", fecha_registro=None):
        self.id = id
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.direccion = direccion
        self.email = email
        self.fecha_registro = fecha_registro

    def nombre_completo(self):
        '''Retorna el nombre completo del paciente'''
        return f"{self.nombre} {self.apellido}"

    def edad(self):
        '''Calcula la edad del paciente'''
        if self.fecha_nacimiento:
            try:
                nacimiento = datetime.strptime(self.fecha_nacimiento, "%Y-%m-%d")
                hoy = datetime.now()
                edad = hoy.year - nacimiento.year
                if hoy.month < nacimiento.month or (hoy.month == nacimiento.month and hoy.day < nacimiento.day):
                    edad -= 1
                return edad
            except:
                return 0
        return 0

    def __str__(self):
        return f"Paciente: {self.nombre_completo()} - Cédula: {self.cedula}"


class Medico:
    '''Clase que representa a un médico del Patronato'''

    ESPECIALIDADES = (
        "Medicina General",
        "Pediatría",
        "Ginecología",
        "Odontología",
        "Cardiología",
        "Trabajo Social",
        "Psicología",
        "Nutrición"
    )

    def __init__(self, id=None, cedula="", nombre="", apellido="",
                 especialidad="", telefono="", email="", fecha_registro=None):
        self.id = id
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.especialidad = especialidad if especialidad in self.ESPECIALIDADES else "Medicina General"
        self.telefono = telefono
        self.email = email
        self.fecha_registro = fecha_registro

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return f"Dr. {self.nombre_completo()} - {self.especialidad}"


class Cita:
    '''Clase que representa una cita médica'''

    ESTADOS = {"Programada", "Confirmada", "En curso", "Completada", "Cancelada", "No asistió"}

    def __init__(self, id=None, paciente_id=None, medico_id=None,
                 fecha="", hora="", motivo="", estado="Programada", fecha_creacion=None):
        self.id = id
        self.paciente_id = paciente_id
        self.medico_id = medico_id
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.estado = estado if estado in self.ESTADOS else "Programada"
        self.fecha_creacion = fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"Cita #{self.id} - {self.fecha} {self.hora} - {self.estado}"


class InventarioCitas:
    '''Clase para gestionar el inventario de citas usando colecciones'''

    def __init__(self):
        self.citas = {}
        self.pacientes = {}
        self.medicos = {}
        self.citas_ordenadas = []
        self.fechas_con_citas = set()
        self.indice_paciente = {}
        self.cargar_datos()

    def cargar_datos(self):
        '''Carga los datos desde la base de datos SQLite'''
        try:
            conn = sqlite3.connect('turnos.db')
            cursor = conn.cursor()

            # Cargar pacientes
            cursor.execute("SELECT * FROM pacientes")
            for row in cursor.fetchall():
                paciente = Paciente(*row)
                self.pacientes[paciente.id] = paciente

            # Cargar médicos
            cursor.execute("SELECT * FROM medicos")
            for row in cursor.fetchall():
                medico = Medico(*row)
                self.medicos[medico.id] = medico

            # Cargar citas
            cursor.execute("SELECT * FROM turnos")
            for row in cursor.fetchall():
                cita = Cita(*row)
                self.citas[cita.id] = cita
                self.citas_ordenadas.append(cita)
                self.fechas_con_citas.add(cita.fecha)

                if cita.paciente_id not in self.indice_paciente:
                    self.indice_paciente[cita.paciente_id] = []
                self.indice_paciente[cita.paciente_id].append(cita)

            conn.close()
            print("✅ Datos cargados desde la base de datos")
        except Exception as e:
            print(f"⚠️ Error cargando datos: {e}")

    def agregar_paciente(self, paciente):
        '''Añade un nuevo paciente'''
        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO pacientes (cedula, nombre, apellido, fecha_nacimiento, telefono, direccion, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (paciente.cedula, paciente.nombre, paciente.apellido,
                  paciente.fecha_nacimiento, paciente.telefono, paciente.direccion, paciente.email))

            conn.commit()
            paciente.id = cursor.lastrowid
            self.pacientes[paciente.id] = paciente
            print(f"✅ Paciente agregado: {paciente.nombre_completo()}")
            return paciente.id
        except sqlite3.Error as e:
            print(f"❌ Error al agregar paciente: {e}")
            return None
        finally:
            conn.close()

    def buscar_paciente(self, criterio):
        '''Busca pacientes por nombre o cédula'''
        resultados = [
            p for p in self.pacientes.values()
            if criterio.lower() in p.nombre.lower() or
               criterio.lower() in p.apellido.lower() or
               criterio in p.cedula
        ]
        return resultados

    def buscar_citas_por_fecha(self, fecha):
        '''Busca citas por fecha'''
        return [c for c in self.citas.values() if c.fecha == fecha]

    def buscar_citas_por_paciente(self, paciente_id):
        '''Busca citas por paciente'''
        return self.indice_paciente.get(paciente_id, [])

    def agregar_cita(self, cita):
        '''Añade una nueva cita'''
        if cita.paciente_id not in self.pacientes:
            print("❌ Paciente no existe")
            return None
        if cita.medico_id not in self.medicos:
            print("❌ Médico no existe")
            return None

        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO turnos (paciente_id, medico_id, fecha, hora, motivo, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cita.paciente_id, cita.medico_id, cita.fecha,
                  cita.hora, cita.motivo, cita.estado))

            conn.commit()
            cita.id = cursor.lastrowid
            self.citas[cita.id] = cita
            self.citas_ordenadas.append(cita)
            self.fechas_con_citas.add(cita.fecha)

            if cita.paciente_id not in self.indice_paciente:
                self.indice_paciente[cita.paciente_id] = []
            self.indice_paciente[cita.paciente_id].append(cita)

            paciente = self.pacientes[cita.paciente_id]
            medico = self.medicos[cita.medico_id]
            print(f"✅ Cita agendada: {paciente.nombre_completo()} con {medico.nombre_completo()}")
            return cita.id
        except Exception as e:
            print(f"❌ Error al agendar cita: {e}")
            return None
        finally:
            conn.close()

    def actualizar_estado_cita(self, cita_id, nuevo_estado):
        '''Actualiza el estado de una cita'''
        if nuevo_estado not in Cita.ESTADOS:
            print(f"❌ Estado inválido")
            return False

        conn = sqlite3.connect('turnos.db')
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE turnos SET estado=? WHERE id=?", (nuevo_estado, cita_id))
            conn.commit()

            if cursor.rowcount > 0:
                if cita_id in self.citas:
                    self.citas[cita_id].estado = nuevo_estado
                print(f"✅ Estado actualizado a: {nuevo_estado}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            conn.close()

    def cancelar_cita(self, cita_id):
        '''Cancela una cita'''
        return self.actualizar_estado_cita(cita_id, "Cancelada")

    def reporte_citas_por_medico(self, medico_id):
        '''Reporte de citas por médico'''
        return [c for c in self.citas.values() if c.medico_id == medico_id]

    def estadisticas(self):
        '''Genera estadísticas del sistema'''
        return {
            "total_pacientes": len(self.pacientes),
            "total_medicos": len(self.medicos),
            "total_citas": len(self.citas),
            "citas_por_estado": {
                estado: len([c for c in self.citas.values() if c.estado == estado])
                for estado in Cita.ESTADOS
            },
            "fechas_con_citas": len(self.fechas_con_citas),
            "proximas_citas": len([c for c in self.citas.values()
                                  if c.fecha >= datetime.now().strftime("%Y-%m-%d")
                                  and c.estado not in ["Cancelada", "Completada"]])
        }

    def mostrar_todo(self):
        '''Muestra todos los elementos del sistema'''
        print("\n" + "="*60)
        print("📋 REPORTE GENERAL DEL SISTEMA")
        print("="*60)

        print(f"\n👥 PACIENTES ({len(self.pacientes)}):")
        for paciente in self.pacientes.values():
            print(f"  • {paciente}")

        print(f"\n👨‍⚕️ MÉDICOS ({len(self.medicos)}):")
        for medico in self.medicos.values():
            print(f"  • {medico}")

        print(f"\n📅 CITAS ({len(self.citas)}):")
        citas_ordenadas = sorted(self.citas.values(), key=lambda c: (c.fecha, c.hora))
        for cita in citas_ordenadas:
            paciente = self.pacientes.get(cita.paciente_id, Paciente(nombre="Desconocido"))
            medico = self.medicos.get(cita.medico_id, Medico(nombre="Desconocido"))
            print(f"  • {cita.fecha} {cita.hora} - {paciente.nombre_completo()} con {medico.nombre_completo()} [{cita.estado}]")
