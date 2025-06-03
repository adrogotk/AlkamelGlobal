import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from Buscador import Buscador


# URL base

MSG_ERROR="Se ha producido un error"
URLS_FILE="Urls.txt"
SEASON_URL="?season="
EVENT_URL="&evvent="
OUTPUT_FOLDER = "csv_files"


os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# Obtiene las urls a scrapear procedentes del fichero Urls.txt
def obtenerUrls():
    urlsFile=open(URLS_FILE, "r")
    urls=[]
    for line in urlsFile:
        urls.append(line.strip())
    return urls

# Obtiene las temporadas de una url base
def obtenerTemporadas(url):
   try:
       response = requests.get(url, timeout=10)
       response.raise_for_status()
       soup = BeautifulSoup(response.text, "html.parser")


       selectTag = soup.find("select", {"name": "season"})
       if not selectTag:
           return []


       seasons = [option["value"] for option in selectTag.find_all("option") if "value" in option.attrs]
       return seasons
   except requests.RequestException as e:
       raise Exception(e)




# Obtiene los eventos de una temporada
def obtenerEventos(url):
   try:
       response = requests.get(url, timeout=10)
       response.raise_for_status()
       soup = BeautifulSoup(response.text, "html.parser")

       selectTag = soup.find("select", {"name": "evvent"})
       if not selectTag:
           return []

       events = [option["value"] for option in selectTag.find_all("option") if "value" in option.attrs]
       return events
   except requests.RequestException as e:
       raise Exception(e)


# Función principal. Por cada evento de una temporada de una url, obtiene los CSVs y los guarda en Hive
def main():
   urls=obtenerUrls()
   for url in urls:
        seasons = obtenerTemporadas(url)
        if not seasons:
           continue
        for season in seasons:
            urlSeason=url + SEASON_URL + season
            events = obtenerEventos(urlSeason)
            if not events:
                continue


            for event in events:
                urlEvent=urlSeason + EVENT_URL+event
                buscador=Buscador(urlEvent)
                buscador.obtenerCsvs(season, event)





main()


