import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from Buscador import Buscador


# URL base

MSG_ERROR="Se ha producido un error"
URLS_FILE="Urls.txt"
SEASON_URL="?Season="
EVENT_URL="&evvent="
OUTPUT_FOLDER = "csv_files"


# Crear carpeta para almacenar los CSV
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



def obtenerUrls():
    urlsFile=open(URLS_FILE, "r")
    urls=[]
    for line in urlsFile:
        urls.append(line.strip())
    return urls


def obtenerTemporadas(url):
   try:
       response = requests.get(url, timeout=10)
       response.raise_for_status()
       soup = BeautifulSoup(response.text, "html.parser")


       # Buscar la etiqueta <select name="season">
       select_tag = soup.find("select", {"name": "season"})
       if not select_tag:
           return []


       # Extraer todas las opciones del select
       seasons = [option["value"] for option in select_tag.find_all("option") if "value" in option.attrs]
       return seasons
   except requests.RequestException as e:
       raise Exception(e)




# Obtener eventos de una temporada
def obtenerEventos(url):
   try:
       response = requests.get(url, timeout=10)
       response.raise_for_status()
       soup = BeautifulSoup(response.text, "html.parser")


       # Buscar la etiqueta <select name="season">
       select_tag = soup.find("select", {"name": "evvent"})
       if not select_tag:
           return []


       # Extraer todas las opciones del select
       seasons = [option["value"] for option in select_tag.find_all("option") if "value" in option.attrs]
       return seasons
   except requests.RequestException as e:
       raise Exception(e)








# Función principal
def main():
   urls=obtenerUrls()
   for url in urls:
        seasons = obtenerTemporadas(url)
        if not seasons:
           continue
        for season in seasons:
            url+=SEASON_URL + season
            events = obtenerEventos(url)
            if not events:
                continue


            for event in events:
                url+=EVENT_URL+event
                buscador=Buscador(url)
                buscador.obtenerCsvs()





main()


