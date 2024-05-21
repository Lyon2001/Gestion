import cx_Oracle # type: ignore
from cx_Oracle import sql # type: ignore

def conectar():
    try:
        conexion = cx_Oracle.connect(user='system',
                                     password='Montecristi1',
                                     dsn='127.0.0.1:1521/XEPDB1')
        return conexion
    except cx_Oracle.DatabaseError as error:
        print("Error al conectar a la base de datos:", error)
        return None

def menu_tabla_rol():
    print("""
    Indique lo que desea realizar con Rol: 
          
    1) Consultar Roles
    2) Crear un Rol
    5) Salir
    """)
    
    eleccion = int(input("Seleccione una opción: "))
    return eleccion

def consultar_roles():
    print("Consultando roles...")
    connection = conectar()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT role FROM dba_roles")
            roles = cursor.fetchall()
            print("Roles de la base de datos:")
            for role in roles:
                print(role[0])
        except cx_Oracle.DatabaseError as e:
            print("Error al obtener la lista de roles:", e)
        finally:
            if connection:
                connection.close()

def crear_rol(nombre_rol):
    print(f"Creando un Rol con nombre: {nombre_rol}")
    connection = conectar()
    if connection: 
        try: 
            cursor = connection.cursor()
            cursor.execute("SELECT role FROM dba_roles WHERE role = :1", (nombre_rol,))
            existing_role = cursor.fetchone()
            if existing_role:
                print(f"El rol {nombre_rol} ya existe.")
            else:
                cursor.execute(sql.SQL("CREATE ROLE {}").format(sql.Identifier(nombre_rol)))
                connection.commit()
                print(f"Rol {nombre_rol} creado correctamente.")
        except cx_Oracle.DatabaseError as e:
            print("Error al crear el rol:", e)
        finally:
            if connection:
                connection.close()

def asignar_rol_usuario(nombre_usuario, nombre_rol):
    print(f"Asignando rol {nombre_rol} al usuario {nombre_usuario}")
    connection = conectar()
    if connection: 
        try: 
            cursor = connection.cursor()
            cursor.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(nombre_rol), sql.Identifier(nombre_usuario)))
            connection.commit()
            print(f"Rol {nombre_rol} asignado correctamente al usuario {nombre_usuario}.")
        except cx_Oracle.DatabaseError as e:
            print("Error al asignar el rol al usuario:", e)
        finally:
            if connection:
                connection.close()

def consultar_roles_usuarios_disponibles():
    print("Roles disponibles:")
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT role FROM dba_roles")
            roles = cursor.fetchall()
            for role in roles:
                print(role[0])
        except cx_Oracle.DatabaseError as e:
            print("Error al obtener la lista de roles:", e)
        finally:
            if conexion:
                conexion.close()

    print("\nUsuarios disponibles:")
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT username FROM dba_users WHERE username NOT IN ('SYS', 'SYSTEM')")
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                print(usuario[0])
        except cx_Oracle.DatabaseError as e:
            print("Error al obtener la lista de usuarios:", e)
        finally:
            if conexion:
                conexion.close()

def main():
    while True:
        eleccion = menu_tabla_rol()
        if eleccion == 1:
            consultar_roles()
        elif eleccion == 2:
            nombre_rol = input("Ingrese el nombre del rol: ")
            crear_rol(nombre_rol)
        elif eleccion == 5:
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()
