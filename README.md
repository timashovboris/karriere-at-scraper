# Karriere.at Job Parser

## English

### Overview
This project is a web scraper for Karriere.at, a job search platform in Austria. It automates the process of retrieving job listings based on specified job titles and locations. The scraper extracts details such as job title, ID, URL, company, location, employment type, salary, and required experience.

### Features
- Automated job search and data extraction from Karriere.at
- Uses Selenium WebDriver for web scraping
- Proxy support for anonymous requests
- Can parse many job types and locations in one run
- Saves extracted job data to a CSV file

### Requirements
- Python 3.x
- Selenium
- a WebDriver (Geckodriver, Chromedriver, or Microsoft Edge WebDriver)
- FreeProxy (for proxy support)
- Pandas (for data processing)

---

## Deutsch

### Übersicht
Dieses Projekt ist ein Web Scraper für Karriere.at, eine Jobsuchplattform in Österreich. Es automatisiert den Prozess des Abrufs von Stellenangeboten auf der Grundlage von bestimmten Jobtiteln und Standorten. Der Scraper extrahiert Details wie Jobtitel, ID, URL, Unternehmen, Ort, Beschäftigungsart, Gehalt und erforderliche Erfahrung.

### Funktionen
- Automatisierte Jobsuche und Datenextraktion von Karriere.at
- Verwendet Selenium WebDriver für Web Scraping
- Proxy-Unterstützung für anonyme Anfragen
- Kann viele Jobtypen und Standorte in einem Durchgang analysieren
- Speichert die extrahierten Jobdaten in einer CSV-Datei

### Anforderungen
- Python 3.x
- Selenium
- ein WebDriver (Geckodriver, Chromedriver oder Microsoft Edge WebDriver)
- FreeProxy (für Proxy-Unterstützung)
- Pandas (für die Datenverarbeitung)

---

## Quick start
All you have to do is to decide what jobs and in what locations you want to find.
```python
from karriere_at_parser import KarriereAtParser

# Creates a parser object with a driver of your choice
# Browser options are "firefox", "chrome" and "edge"
# Don't forget to provide respective drivers, they are installed separately
kp = KarriereAtParser("firefox", "path/to/driver") 

jobs = ["Software Entwickler", "IT"]
locations = ["Wien", "Salzburg", "Graz"]

kp.fetch_jobs(jobs, locations) # fetches data and stores it in the object
df = kp.get_df() # returns pandas dataframe
```

## Functions
### fetch_jobs
A callable that initiates parsing.

```python
from karriere_at_parser import KarriereAtParser
kp = KarriereAtParser("firefox", "path/to/driver") 
...
kp.fetch_jobs(jobs_list=[], locations=[], remove_duplicates=True, csv_name="", length_limit=9999, export=True)
```

A stored dataframe is not being cleared when this function is called. You'll need to clean it manually with [clear_df](#clear_df) function.

#### Parameters

* jobs_list (list): A list of job titles or keywords to search for. This parameter is mandatory.
* locations (list): A list of geographical locations where the jobs should be searched. This parameter is mandatory.
* remove_duplicates (bool, optional): If set to True, duplicate job entries will be removed from the resulting DataFrame. Defaults to True.
* csv_name (str, optional): The desired name for the output CSV file. If left as an empty string (default), a name will be automatically generated.
* length_limit (int, optional): A hard limit for the maximum number of jobs to fetch. Defaults to 9999.
* export (bool, optional): If set to True, the fetched jobs will be automatically exported to a .csv file. Defaults to True.

#### Returns
* pandas.DataFrame: A DataFrame containing the parsed job listings. This DataFrame is also stored internally as self.current_df.

### export_df_to_csv
Exports the current dataframe to a csv file.

```python
from karriere_at_parser import KarriereAtParser
kp = KarriereAtParser("firefox", "path/to/driver") 
...
kp.export_df_to_csv(csv_name="")
```

#### Parameters
* csv_name: string, the name of the csv file

### get_df
Returns current dataframe.

```python
from karriere_at_parser import KarriereAtParser
kp = KarriereAtParser("firefox", "path/to/driver") 
...
df = kp.get_df()
```

### clear_df
Manually removes all the entries from the stored dataframe.
```python
from karriere_at_parser import KarriereAtParser
kp = KarriereAtParser("firefox", "path/to/driver") 
...
kp.clear_df()
```
## License
This code is open. It is distributed under the copyleft [European Union Public License v 1.2](LICENSE).

