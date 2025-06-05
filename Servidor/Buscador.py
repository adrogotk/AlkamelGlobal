import subprocess

import pandas as pd
from pyhive import hive
from io import StringIO
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class Buscador:
    MSG_ERROR = "Se ha producido un error"
    HIVE_HOST="localhost"
    HIVE_PORT=10000
    HIVE_DATABASE="AlkamelCsvs"
    TIPOS = {
        'object': 'STRING',
        'int64': 'INT',
        'float64': 'FLOAT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP'
    }
    QUERY_LAST_INSERT_ID="SELECT MAX(id) FROM pilotos"
    QUERY_CREATE_DATABASE="CREATE DATABASE IF NOT EXISTS AlkamelCsvs"
    USE_DATABASE="USE AlkamelCsvs"
    QUERY_CREATE_TABLE_PILOTOS="""
                                CREATE TABLE IF NOT EXISTS pilotos (
                                    id INT,
                                    nombre STRING
                                )
                                STORED AS TEXTFILE
                            """
    QUERY_CREATE_TABLE_PILOTOS_URL="""
                               CREATE TABLE IF NOT EXISTS pilotos_url (
                                   piloto_id INT,
                                   tabla STRING
                               )
                               STORED AS TEXTFILE
                           """
    # Constructor
    def __init__(self, url):
        self.url=url

    # Obtiene todos los enlaces de una url
    def obtenerEnlaces(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return [urljoin(self.url, a["href"]) for a in soup.find_all("a", href=True)]
        except requests.RequestException as e:
            raise Exception(e)

    # Obtiene todos los CSVs de una lista de enlaces y descargarlos
    def obtenerCsvs(self, season ,event):
        links = self.obtenerEnlaces()
        csvLinks=[]
        for link in links:
            if (link.endswith(".CSV")):
                csvLinks.append(link)
        for csvLink in csvLinks:
            print("pasa por obtener csvs")
            self.descargarCsv(csvLink, season, event)

    # Obtiene el nombre de la tabla que se guardará en Hive
    def getTableName (self, csvUrl, season, event):
        finalUrl = csvUrl.split("/")
        tableName = os.path.basename(urlparse(csvUrl).path) + "_barra_" + finalUrl[
            6] + "_barra_" + season + "_barra_" + event + "_"
        tableName = ((((tableName.replace("%20", "_").replace(" ", "_")
                        .replace(".CSV", "").replace("-", "_"))
                       .replace(".", "_")).replace("(", "").replace(")", "")
                      .replace("+_", "")).replace("&", "").replace("", "")
                     .replace(",", "_")).replace("+", "")
        return tableName

    # Obtiene las columnas de la tabla que se guardará en Hive
    def getColumns(self, dataFrame):
        columnas="("
        for cols in dataFrame.columns:
            col = cols.split(";")
            for columna in col:
                if (columna != ""):
                    columna = columna.replace(" ", "")
                    if (columnas.find("," + columna + " " + "STRING" + ",") == -1):
                        columnas += columna + " " + "STRING" + ","
        columnas = columnas.replace(";", ",")
        columnas += ")"
        columnas = ((columnas.replace(",)", ")").replace("GROUP", "GRUPO")
                     .replace("Group", "Grupo")).replace("ï»¿", "").replace("*", "")
                    .replace("-", "_"))
        return columnas

    # Obtiene los pilotos de cada CSV
    def getColumnasPiloto(self, dataFrame):
        columns = dataFrame.columns
        drivers=[]
        if "DRIVER" in columns:
            drivers = dataFrame["DRIVER"].dropna().unique()
        elif "DRIVER_FIRSTNAME" in columns and "DRIVER_SECONDNAME" in columns:
            drivers = (dataFrame["DRIVER_FIRSTNAME"].fillna('') + " " + dataFrame["DRIVER_SECONDNAME"].fillna(
                '')).str.strip().dropna().unique()
        elif "DRIVER_1" in columns:
            driverCols = [col for col in ["DRIVER_1", "DRIVER_2", "DRIVER_3", "DRIVER_4"] if col in columns]
            drivers = pd.unique(dataFrame[driverCols].values.ravel())
            drivers = [d for d in drivers if pd.notna(d)]
        return drivers

    # Inserta un piloto en las tablas de pilotos y pilotos_url
    def insertarPiloto(self, cursor, dataFrame, tableName):
        drivers = self.getColumnasPiloto(dataFrame)
        for driver in drivers:
            driver = driver.replace("'", "''")
            cursor.execute(f"SELECT id FROM pilotos WHERE nombre = '{driver}'")
            result = cursor.fetchone()
            if result is None:
                # Obtener el último id insertado (o 0 si no hay registros)
                cursor.execute(self.QUERY_LAST_INSERT_ID)
                maxId = cursor.fetchone()[0]
                newId = (maxId or 0) + 1

                cursor.execute(f"INSERT INTO pilotos (id, nombre) VALUES ({newId}, '{driver}')")
                cursor.execute(f"INSERT INTO pilotos_url (piloto_id, tabla) VALUES ({newId}, '{tableName}')")
            else:
                piloto_id = result[0]
                cursor.execute(f"""
                    SELECT 1 FROM pilotos_url 
                    WHERE piloto_id = {piloto_id} AND tabla = '{tableName}'
                """)
                if cursor.fetchone() is None:
                    cursor.execute(f"INSERT INTO pilotos_url (piloto_id, tabla) VALUES ({piloto_id}, '{tableName}')")

    # Descarga los CSVs encontrados y los inserta en una tabla específica en Hive
    def descargarCsv(self, csvUrl, season, event):
        tableName = self.getTableName(csvUrl,season, event)
        print(tableName)
        try:
            response = requests.get(csvUrl, stream=True)
            response.raise_for_status()
            text=response.text.replace(",",".")
            if (text!=""):
                conn = hive.Connection(host=self.HIVE_HOST,
                                   port=self.HIVE_PORT
                                   )
                cursor = conn.cursor()
                cursor.execute(self.QUERY_CREATE_DATABASE)
                cursor.execute(self.USE_DATABASE)
                cursor.execute(self.QUERY_CREATE_TABLE_PILOTOS)
                cursor.execute(self.QUERY_CREATE_TABLE_PILOTOS_URL)
                cursor.execute(f"SHOW TABLES LIKE '{tableName}'")
                table_exists = cursor.fetchone() is not None
                if not table_exists:
                    dataFrame = pd.read_csv(StringIO(text))
                    columnas=self.getColumns(dataFrame)
                    print(columnas)
                    tempFile = '/tmp/temp_hive_upload.csv'
                    os.makedirs(os.path.dirname(tempFile), exist_ok=True)
                    dataFrame.to_csv(tempFile, index=False, header=False)
                    os.system(
                        f"docker exec -i namenode hdfs dfs -put -f - /tmp/{os.path.basename(tempFile)} < {tempFile}")
                    cursor.execute(f"""
                                              CREATE TABLE IF NOT EXISTS {tableName} 
                                                  {columnas}
                                              ROW FORMAT DELIMITED
                                              FIELDS TERMINATED BY ','
                                              STORED AS TEXTFILE
                                           """)
                    cursor.execute(f"SELECT COUNT(*) FROM {tableName}")
                    row_count = cursor.fetchone()[0]
                    if (row_count==0):
                        cursor.execute(f"""
                           LOAD DATA INPATH '/tmp/{os.path.basename(tempFile)}'
                           INTO TABLE {tableName}
                       """)
                        print("CSV cargado exitosamente en Hive.")
                        self.insertarPiloto(cursor, dataFrame,tableName)
        except requests.RequestException as e:
            raise Exception(e)