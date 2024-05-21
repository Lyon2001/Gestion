import cx_Oracle # type: ignore
import rol
import usuario
import os
from datetime import datetime
from fpdf import FPDF # type: ignore

# Función para establecer la conexión a la base de datos
def establecer_conexion():
    try:
        conexion = cx_Oracle.connect(user='system',
                                     password='Montecristi1',
                                     dsn='127.0.0.1:1521/XEPDB1')
        print("Conexión establecida a la base de datos.")
        return conexion
    except cx_Oracle.DatabaseError as error:
        print("Error al establecer la conexión a la base de datos:", error)
        return None

# Función para cerrar la conexión a la base de datos
def cerrar_conexion(conexion, cursor=None):
    try:
        if cursor:
            cursor.close()
        conexion.close()
        print("Conexión cerrada.")
    except cx_Oracle.DatabaseError as error:
        print("Error al cerrar la conexión a la base de datos:", error)

# Función para realizar el respaldo de la base de datos
def realizar_respaldo(conexion):
    try:
        # Obtener la fecha y hora actual para usarla en el nombre del respaldo
        fecha_actual = datetime.today().strftime('%Y_%m_%d_%H_%M')

        # Definir el nombre del archivo de respaldo
        nombre_archivo_respaldo = f"respaldo_{fecha_actual}.dmp"

        # Definir la ruta completa del archivo de respaldo
        ruta_completa_respaldo = f"C:/Users/User/Desktop/Codigo-GDBD/respaldo/{nombre_archivo_respaldo}"

        # Comando para realizar el respaldo usando expdp
        comando_respaldo = f"expdp system/Montecristi1@XE schemas=VENTAS directory=DATA_PUMP_DIR dumpfile={nombre_archivo_respaldo} logfile=expdp_{fecha_actual}.log"

        # Ejecutar el comando de respaldo
        os.system(comando_respaldo)

        print(f"Respaldo de la base de datos creado correctamente en '{ruta_completa_respaldo}'.")
    except Exception as error:
        print("Error al realizar el respaldo:", error)

# Función para restaurar la base de datos desde un archivo de respaldo
def restaurar_base_de_datos(conexion, ruta_archivo_respaldo, usuario, contraseña, host='localhost', puerto='1521'):
    try:
        # Comando para restaurar la base de datos usando impdp
        comando_restaurar = f"impdp {usuario}/{contraseña}@{host}:{puerto}/XE directory=DATA_PUMP_DIR dumpfile={ruta_archivo_respaldo} logfile=impdp_restore.log"

        # Ejecutar el comando de restauración
        os.system(comando_restaurar)

        print(f"Base de datos restaurada correctamente desde '{ruta_archivo_respaldo}'.")
    except Exception as error:
        print("Error al restaurar la base de datos:", error)

# Función para listar las entidades en la base de datos
def listar_entidades_base_datos(conexion):
    try:
        cursor = conexion.cursor()

        # Consulta SQL para obtener la lista de tablas en la base de datos
        query = "SELECT table_name FROM user_tables ORDER BY table_name"

        cursor.execute(query)

        print("Lista de entidades en la base de datos:")
        
        # Iterar sobre los resultados y mostrar el nombre de cada entidad
        for table_name in cursor.fetchall():
            print("- " + table_name[0])

        cursor.close()
        
    except cx_Oracle.DatabaseError as error:
        print("Error al listar las entidades:", error)

# Función para listar los atributos por entidad
def listar_atributos_entidad(conexion):
    try:
        # Consulta SQL para obtener la lista de tablas (entidades) en la base de datos
        query = """
        SELECT table_name
        FROM user_tables
        ORDER BY table_name;
        """
        with conexion.cursor() as cursor:
            cursor.execute(query)
            entidades = cursor.fetchall()

            # Mostrar las entidades disponibles
            print("Lista de entidades en la base de datos:")
            for idx, entidad in enumerate(entidades, start=1):
                print(f"{idx}. {entidad[0]}")

            # Solicitar al usuario que seleccione una entidad
            entidad_idx = int(input("Seleccione el número de la entidad para ver sus atributos (o 0 para salir): "))
            if 0 < entidad_idx <= len(entidades):
                entidad_seleccionada = entidades[entidad_idx - 1][0]
                
                # Consulta SQL para obtener los atributos de la entidad seleccionada
                query_atributos = f"""
                SELECT column_name
                FROM user_tab_columns
                WHERE table_name = '{entidad_seleccionada}';
                """
                cursor.execute(query_atributos)
                atributos = cursor.fetchall()

                # Mostrar los atributos de la entidad seleccionada
                print(f"Atributos de la entidad '{entidad_seleccionada}':")
                for atributo in atributos:
                    print(f"- {atributo[0]}")
            elif entidad_idx == 0:
                print("Saliendo...")
            else:
                print("Selección no válida.")
    except cx_Oracle.DatabaseError as error:
        print("Error al listar los atributos de las entidades:", error)

# Función para agregar una nueva entidad con atributos a la base de datos
def agregar_entidad_con_atributos():
    try:
        # Establecer la conexión a la base de datos
        conexion = establecer_conexion()
        if conexion is None:
            return

        # Solicitar al usuario el nombre de la nueva entidad
        nombre_entidad = input("Ingrese el nombre de la nueva entidad: ")

        # Consulta SQL para crear una nueva tabla (entidad) con algunos atributos
        crear_tabla_query = f"""
            CREATE TABLE {nombre_entidad} (
                id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                nombre VARCHAR2(50),
                edad NUMBER,
                fecha_creacion TIMESTAMP,
                activo CHAR(1)
            )
        """
        
        # Ejecutar la consulta para crear la nueva tabla
        with conexion.cursor() as cursor:
            cursor.execute(crear_tabla_query)
            print(f"Se ha creado la nueva entidad '{nombre_entidad}' correctamente.")

        # Confirmar los cambios y cerrar la conexión
        conexion.commit()
        print(f"Se han agregado atributos a la entidad '{nombre_entidad}' correctamente.")
    except cx_Oracle.DatabaseError as error:
        print("Error al agregar la nueva entidad con atributos:", error)
    finally:
        # Cerrar la conexión a la base de datos
        cerrar_conexion(conexion)

# Función para generar el informe PDF
def generar_informe_pdf(connection):
    ruta_pdf = "Informe.pdf"
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    try:
        # Cabecera
        pdf.cell(200, 10, txt="Entidades y atributos de Sistema de ventas", ln=True, align="C")
        pdf.ln(10)
        
        current_entity = None
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.table_name AS TableName, c.column_name AS ColumnName 
                FROM user_tables t 
                JOIN user_tab_columns c 
                ON t.table_name = c.table_name 
                ORDER BY t.table_name, c.column_id
            """)
            for row in cursor.fetchall():
                table_name, column_name = row
                if current_entity != table_name:
                    if current_entity is not None:
                        pdf.ln()
                    pdf.cell(200, 10, txt=f"Entidad: {table_name}", ln=True)
                    current_entity = table_name
                pdf.cell(200, 10, txt=f" - {column_name}", ln=True)
        
        pdf.output(ruta_pdf)
        print("Informe PDF generado correctamente.")
    except cx_Oracle.DatabaseError as error:
        print("Error al generar el informe PDF:", error)

# Función para generar procedimientos CRUD para las tablas de la base de datos
def generar_procedimientos_almacenados(conexion):
    try:
        cursor = conexion.cursor()

        # Obtener nombres de tablas
        cursor.execute("SELECT table_name FROM user_tables")
        tablas = cursor.fetchall()

        for tabla in tablas:
            nombre_tabla = tabla[0]

            # Obtener nombres de columnas
            cursor.execute(f"SELECT column_name FROM user_tab_columns WHERE table_name='{nombre_tabla}'")
            columnas = cursor.fetchall()
            nombres_columnas = [columna[0] for columna in columnas]

            # Generar código CRUD
            print(f"--- Procedimientos CRUD para la tabla {nombre_tabla} ---")
            print("def create():")
            parametros = ", ".join([f":{i+1}" for i in range(len(nombres_columnas))])
            placeholders = ", ".join(nombres_columnas)
            print(f"    cursor.execute('INSERT INTO {nombre_tabla} ({placeholders}) VALUES ({parametros})')")
            print()
            print("def read():")
            print(f"    cursor.execute('SELECT * FROM {nombre_tabla}')")
            print()
            print("def update():")
            set_clause = ", ".join([f"{columna}=:{i+1}" for i, columna in enumerate(nombres_columnas)])
            print(f"    cursor.execute('UPDATE {nombre_tabla} SET {set_clause} WHERE id=:id')")
            print()
            print("def delete():")
            print(f"    cursor.execute('DELETE FROM {nombre_tabla} WHERE id=:id')")
            print()

        cursor.close()
    except cx_Oracle.DatabaseError as error:
        print("Error al generar procedimientos CRUD:", error)

# Ejecución del programa
def main():
    conexion = establecer_conexion()
    if conexion:
        while True:
            print("\nOpciones:")
            print("1. Realizar respaldo de la base de datos")
            print("2. Restaurar base de datos desde un archivo de respaldo")
            print("3. Listar entidades en la base de datos")
            print("4. Listar atributos por entidad")
            print("5. Agregar entidad con atributos a la base de datos")
            print("6. Generar informe PDF")
            print("7. Generar procedimientos almacenados CRUD")
            print("8. Salir")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                realizar_respaldo(conexion)
            elif opcion == "2":
                ruta_archivo_respaldo = input("Ingrese la ruta del archivo de respaldo: ")
                usuario = input("Ingrese el usuario de la base de datos: ")
                contraseña = input("Ingrese la contraseña del usuario: ")
                restaurar_base_de_datos(conexion, ruta_archivo_respaldo, usuario, contraseña)
            elif opcion == "3":
                listar_entidades_base_datos(conexion)
            elif opcion == "4":
                listar_atributos_entidad(conexion)
            elif opcion == "5":
                agregar_entidad_con_atributos()
            elif opcion == "6":
                generar_informe_pdf(conexion)
            elif opcion == "7":
                generar_procedimientos_almacenados(conexion)
            elif opcion == "8":
                break
            else:
                print("Opción no válida. Por favor, intente nuevamente.")
        
        cerrar_conexion(conexion)

if __name__ == "__main__":
    main()
