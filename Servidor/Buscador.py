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
    def __init__(self, url):
        self.url=url

    def obtenerEnlaces(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return [urljoin(self.url, a["href"]) for a in soup.find_all("a", href=True)]
        except requests.RequestException as e:
            raise Exception(e)

    def obtenerCsvs(self, season ,event):
        links = self.obtenerEnlaces()
        csv_links=[]
        for link in links:
            if (link.endswith(".CSV")):
                csv_links.append(link)
        for csv_link in csv_links:
            print("pasa por obtener csvs")
            self.descargarCsv(csv_link, season, event)

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

    def getColumns(self, dataFrame):
        columnas="("
        for cols in dataFrame.columns:
            # print(cols)
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
    def getColumnasPiloto(self, dataFrame):
        columns = dataFrame.columns
        drivers=[]
        if "DRIVER" in columns:
            drivers = dataFrame["DRIVER"].dropna().unique()
        elif "DRIVER_FIRSTNAME" in columns and "DRIVER_SECONDNAME" in columns:
            drivers = (dataFrame["DRIVER_FIRSTNAME"].fillna('') + " " + dataFrame["DRIVER_SECONDNAME"].fillna(
                '')).str.strip().dropna().unique()
        elif "DRIVER_1" in columns:
            driver_cols = [col for col in ["DRIVER_1", "DRIVER_2", "DRIVER_3", "DRIVER_4"] if col in columns]
            drivers = pd.unique(dataFrame[driver_cols].values.ravel())
            drivers = [d for d in drivers if pd.notna(d)]
        return drivers

    def insertarPiloto (self, cursor, dataFrame, tableName):
        drivers = self.getColumnasPiloto(dataFrame)
        for i, driver in enumerate(drivers):
            driver = driver.replace("'", "''")  # escapa comillas simples
            cursor.execute(f"SELECT id FROM pilotos WHERE nombre = '{driver}'")
            result = cursor.fetchone()
            if result is None:
                new_id = i + 1  # ID manual (mejor si tienes una forma confiable de autoincremento)
                cursor.execute(f"INSERT INTO pilotos VALUES ({new_id}, '{driver}')")
                cursor.execute(f"INSERT INTO pilotos_url VALUES ({new_id}, '{tableName}')")
            else:
                piloto_id = result[0]
                cursor.execute(f"""
                               SELECT * FROM pilotos_url 
                               WHERE piloto_id = {piloto_id} AND tabla = '{tableName}'
                           """)
                if cursor.fetchone() is None:
                    cursor.execute(f"INSERT INTO pilotos_url VALUES ({piloto_id}, '{tableName}')")

    def descargarCsv(self, csvUrl, season, event):
        tableName = self.getTableName(csvUrl,season, event)
        print(tableName)
        try:
            response = requests.get(csvUrl, stream=True)
            response.raise_for_status()
            text=response.text.replace(",",".")
            if (text!=""):
            #print(dataFrame)
                conn = hive.Connection(host=self.HIVE_HOST,
                                   port=self.HIVE_PORT
                                   )
                cursor = conn.cursor()
                #cursor.execute("DROP DATABASE IF EXISTS AlkamelCsvs CASCADE")
                # ("eliminada")
                cursor.execute("CREATE DATABASE IF NOT EXISTS AlkamelCsvs")
                cursor.execute("USE AlkamelCsvs")
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS pilotos (
                                    id INT,
                                    nombre STRING
                                )
                                STORED AS TEXTFILE
                            """)
                cursor.execute("""
                               CREATE TABLE IF NOT EXISTS pilotos_url (
                                   piloto_id INT,
                                   tabla STRING
                               )
                               STORED AS TEXTFILE
                           """)
                cursor.execute(f"SHOW TABLES LIKE '{tableName}'")
                table_exists = cursor.fetchone() is not None
                if not table_exists:
                    dataFrame = pd.read_csv(StringIO(text))
                    columnas=self.getColumns(dataFrame)
                    print(columnas)
                    tempFile = '/tmp/temp_hive_upload.csv'
                    dataFrame.to_csv(tempFile, index=False, header=False)
                    os.system(f"docker exec -i namenode hdfs dfs -put -f - /tmp/{os.path.basename(tempFile)} < {tempFile}")
                    cursor.execute(f"""
                                              CREATE TABLE IF NOT EXISTS {tableName} 
                                                  {columnas}
                                              ROW FORMAT DELIMITED
                                              FIELDS TERMINATED BY ','
                                              STORED AS TEXTFILE
                                              TBLPROPERTIES ('skip.header.line.count'='1')
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