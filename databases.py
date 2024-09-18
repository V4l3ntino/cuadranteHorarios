import pyodbc
import mysql.connector
from mysql.connector import Error
import argparse

def fetch_data_from_sql_server(query):
    try:
        # Conexión a la base de datos SQL Server
        conn_str = (
            "DRIVER={SQL SERVER};"
            "SERVER=;"
            "DATABASE=;"
            "UID=;"
            "PWD="
        )
        source_db = pyodbc.connect(conn_str)
        cursor = source_db.cursor()
        cursor.execute(query)  
        resultados = cursor.fetchall()
        datos_para_mysql = [tuple(fila) for fila in resultados]
        return datos_para_mysql
    except pyodbc.Error as e:
        print(f"ERROR EN LA CONSULTA AL SQL ->: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if source_db:
            source_db.close()

def create_and_insert_into_mysql(resultados, nombre, column_dict, primary_key):
    try:
        # Conexión a la base de datos MySQL
        dest_db = mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )
        if dest_db.is_connected():
            cursor = dest_db.cursor()
            
            create_table_query = f"CREATE TABLE IF NOT EXISTS {nombre} ("
            
            for column_name, column_details in column_dict.items():
                name = column_details[0]
                data_type = column_details[1]
                create_table_query += f"{name} {data_type}, "
            
            # Eliminar la última coma y espacio
            create_table_query = create_table_query[:-2]
            create_table_query += ")"
            
            # Crear la tabla en la base de datos MySQL
            cursor.execute(create_table_query)
            

            # Insertar los datos obtenidos
            for fila in resultados:
                # Construir la parte de los nombres de las columnas dinámicamente
                column_names = ", ".join([column[0] for column in column_dict.values()])

                # Crear una cadena de marcadores de posición para los valores (%s)
                value_placeholders = ", ".join(["%s" for _ in range(len(column_dict))])

                # Crear la consulta SQL dinámicamente
                insert_query = f"INSERT INTO {nombre} ({column_names}) VALUES ({value_placeholders})"

                # Ejecutar la consulta con los valores de la fila
                cursor.execute(insert_query, fila)
            
            if primary_key:
                try:
                    alter_query = f"ALTER TABLE {nombre} ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;"
                    cursor.execute(alter_query)
                except Error as e:
                    print(f"ERROR AL GENERAR CLAVE AUTOINCREMENTAR >  {e}")
            
            print(f"Tabla '{nombre}' creada exitosamente.")

            dest_db.commit()
    except Error as e:
        print(f"ERROR EN LA INSERCCIÓN DE DATOS MySQL: {e}")
    finally:
        if cursor:
            cursor.close()
        if dest_db:
            dest_db.close()

def main():
    nombre_tabla = input("Introduce el nombre de la tabla destino > ")
    cantidad_columnas = int(input("Introduce la cantidad de columnas que deseas en la tabla destino > "))
    column_dict = {}
    for i in range(cantidad_columnas):
        nombre_columna = f"Columna{i}"
        column_dict[nombre_columna] = []
        
    for i in range(cantidad_columnas):
        nombre_columna = f"Columna{i}"
        nombre = input(f"Introduce el nombre para la columna {i + 1}: ")
        tipo = input(f"Introduce el tipo de datos para la columna {i + 1} (ej. VARCHAR(255)): ")
        column_dict[nombre_columna] = [nombre, tipo]    
    
    auxiliar = False
    while not auxiliar:
        primary_key = input("Desea generar una clave primaria auto incremental?(Si o No) > ").strip().lower()
    
        if primary_key in ['si', 'sí', 's', 'y', 'yes']:
            primary_key = True
            auxiliar = True
        elif primary_key in ['no', 'n']:
            primary_key = False
            auxiliar = True
        
    query = input("A continuación la consulta SQL para obtener datos de SQL Server:\n")

    # Llamar a la función fetch_data_from_sql_server con la consulta proporcionada
    resultados = fetch_data_from_sql_server(query)
    if resultados:
        create_and_insert_into_mysql(resultados, nombre_tabla, column_dict, primary_key)

if __name__ == "__main__":
    main()
