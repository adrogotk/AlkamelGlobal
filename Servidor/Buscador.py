import os
import requests
import self
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Buscador:
    MSG_ERROR = "Se ha producido un error"
    OUTPUT_FOLDER="QUITAR"
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
        filename = os.path.join(self.OUTPUT_FOLDER,
                                self.url + os.path.basename(urlparse(csvUrl).path))
        try:
            response = requests.get(csvUrl, stream=True)
            response.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.RequestException as e:
            raise Exception(e)