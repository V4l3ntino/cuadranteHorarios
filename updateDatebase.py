import pyodbc
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def fetch_data_from_sql_server(query):
    try:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=;"
            "DATABASE=;"
            "UID=;"
            "PWD="
        )
        source_db = pyodbc.connect(conn_str)
        cursor = source_db.cursor()
        resultados = cursor.execute(query).fetchall()
        datos_para_mysql = [tuple(fila) for fila in resultados]    
        return datos_para_mysql
    
    except pyodbc.Error as e:
        print(f"ERROR EN LA CONSULTA SQL ->: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if source_db:
            source_db.close()

def update_table_mysql(resultados, nombre_tabla, columns):
    try:
        dest_db = mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )
    
        if dest_db.is_connected():
            cursor = dest_db.cursor()
            cursor.execute(f"TRUNCATE TABLE {nombre_tabla}")
            
            for fila in resultados:
                column_names = ", ".join([column for column in columns])
                values_placeholders = ", ".join(["%s" for _ in range(len(columns))])
                insert_query = f"INSERT INTO {nombre_tabla} ({column_names}) VALUES ({values_placeholders})"
                cursor.execute(insert_query, fila)

            print(f"La tabla {nombre_tabla} ha sido actualizada correctamente")
            
            dest_db.commit()
                 
            
    except Error as e:
        print(f"ERROR EN LA ACTUALIZACIÓN DE LA TABLA {nombre_tabla} > {e}")
    finally:
        if cursor:
            cursor.close()
        if dest_db:
            dest_db.close()
        

def main():
    anio = datetime.now().year
    query = f""
    resultados = fetch_data_from_sql_server(query)
    if resultados:
        columns = ["operario_id", "nombre", "fecha_alta", "fecha_baja", "tipo"]
        update_table_mysql(resultados, "operarios_fechas", columns)
        
    query = f""
    resultados = fetch_data_from_sql_server(query)
    if resultados:
        columns = ["fecha_trabajo", "id_operario", "grupo_maquina"]
        update_table_mysql(resultados, "operarios_maquina_actual", columns)
        
    query = f""
    resultados = fetch_data_from_sql_server(query)
    if resultados:
        columns = ["operario_id", "operacion", "autos", "bordadoras", "cosido", "digital", "horno", "laser", "otros", "planchas", "sublimacion", "pulpos", "tampografia", "termograbado"]
        update_table_mysql(resultados, "operarios_maquinas_anio_entero", columns)
    
    query = f""
    resultados = fetch_data_from_sql_server(query)
    if resultados:
        columns = ["Fecha_Inicio", "Operario", "Maquina"]
        update_table_mysql(resultados, "picaje", columns)


if __name__ == "__main__":
    main()