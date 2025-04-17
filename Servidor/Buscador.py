import pandas as pd
from pyhive import hive
from io import StringIO
import thrift
import os
import requests
import self
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class Buscador:
    MSG_ERROR = "Se ha producido un error"
    HIVE_HOST="localhost"
    HIVE_PORT=10000
    HIVE_DATABASE="AlkamelCsvs"
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

    def obtenerCsvs(self):
        links = self.obtenerEnlaces()
        csv_links = [link for link in links if link.endswith(".CSV")]
        for csv_link in csv_links:
            self.descargarCsv(csv_link)

    def descargarCsv(self, csvUrl):
        tableName = os.path.basename(urlparse(csvUrl).path)
        try:
            response = requests.get(csvUrl, stream=True)
            response.raise_for_status()
            dataFrame = pd.read_csv(StringIO(response.text))
            conn = hive.Connection(host=self.HIVE_HOST,
                                   port=self.HIVE_PORT,
                                   auth='NOSASL',
                                   username='hive'
                                   )
            cursor = conn.cursor()
            columnas = ', '.join([f'{col} STRING' for col in dataFrame.columns])
            cursor.execute(f"""
                           CREATE DATABASE IF NOT EXISTS AlkamelCsvs;
                           CREATE TABLE IF NOT EXISTS {tableName} (
                               {columnas}
                           )
                           ROW FORMAT DELIMITED
                           FIELDS TERMINATED BY ','
                           STORED AS TEXTFILE
                       """)
            tempFile = '/tmp/temp_hive_upload.csv'
            dataFrame.to_csv(tempFile, index=False, header=False)
            os.system(f"docker exec -i namenode hdfs dfs -put -f - /tmp/{os.path.basename(tempFile)} < {tempFile}")
            cursor.execute(f"""
                           LOAD DATA INPATH '/tmp/{os.path.basename(tempFile)}'
                           INTO TABLE {tableName}
                       """)
            print("CSV cargado exitosamente en Hive.")
        except requests.RequestException as e:
            raise Exception(e)