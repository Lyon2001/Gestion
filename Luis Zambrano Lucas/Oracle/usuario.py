import cx_Oracle # type: ignore

def conectar():
    try:
        # Conexión a la base de datos Oracle
        conexion = cx_Oracle.connect(user='system',
                                     password='Montecristi1',
                                     dsn='127.0.0.1:1521/XEPDB1')
        return conexion
    except cx_Oracle.DatabaseError as error:
        print("Error al conectar a la base de datos:", error)
        return None

def menu_tabla_usuario():
    print("""
    Indique lo que desea realizar con Usuario: 
          
    1) Consultar Usuarios
    2) Crear un Usuario
    5) Salir
    """)
    
    eleccion = int(input("Seleccione una opción: "))
    return eleccion

def consultar_usuarios():
    print("Consultando usuarios...")
    connection = conectar()
    if connection:
        try:
            cursor = connection.cursor()
            # Consulta para obtener la lista de usuarios en Oracle
            cursor.execute("SELECT username FROM dba_users WHERE username NOT IN ('SYS', 'SYSTEM')")
            users = cursor.fetchall()
            print("Usuarios de la base de datos:")
            for user in users:
                print(user[0])
        except cx_Oracle.DatabaseError as e:
            print("Error al obtener la lista de usuarios:", e)
        finally:
            if connection:
                connection.close()

# Función para crear usuario 
def crear_usuario():
    print("Creando un Usuario...")
    username = input("Ingrese el nombre del nuevo usuario: ")
    password = input("Ingrese la contraseña del nuevo usuario: ")
    connection = conectar()
    if connection: 
        try: 
            cursor = connection.cursor()
            # Verificar si el usuario ya existe en Oracle
            cursor.execute("SELECT username FROM dba_users WHERE username = :1", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                print(f"El usuario {username} ya existe.")
            else:
                # Crear el usuario en Oracle
                cursor.execute(f"CREATE USER {username} IDENTIFIED BY {password}")
                cursor.execute(f"GRANT CONNECT, RESOURCE TO {username}")
                connection.commit()
                print(f"Usuario {username} creado correctamente.")
        except cx_Oracle.DatabaseError as e:
            print("Error al crear el usuario:", e)
        finally:
            if connection:
                connection.close()

# Función para obtener información de la metadata
def get_metadata():
    connection = conectar()
    if connection:
        try:
            cursor = connection.cursor()
            # Ejemplo: obtener nombres de todas las tablas en el esquema del usuario
            cursor.execute("SELECT table_name FROM user_tables")
            tables = cursor.fetchall()
            print("Tablas en el esquema del usuario:")
            for table in tables:
                print(table[0])
        except cx_Oracle.DatabaseError as e:
            print("Error al obtener metadata:", e)
        finally:
            if connection:
                connection.close()

# Ejemplo de uso
if __name__ == "__main__":
    while True:
        eleccion = menu_tabla_usuario()
        if eleccion == 1:
            consultar_usuarios()
        elif eleccion == 2:
            crear_usuario()
        elif eleccion == 5:
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida, intente de nuevo.")
