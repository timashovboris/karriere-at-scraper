# Karriere.at Job Scraper

## Overview

### English

This software is a web scraper for [karriere.at](https://www.karriere.at/), an Austrian job search platform. It automates the process of retrieving
job listings based on specified job titles and locations. The scraper extracts details such as job title, ID, URL,
company,
location, employment type, salary and job level.

The exported data are raw strings that need to be further processed for any data analysis. Some analysis instruments are
provided with the package.

### Deutsch

Diese Software ist ein Web Scraper für [karriere.at](https://www.karriere.at/), eine österreichische Jobsuchplattform. Es automatisiert den Prozess
des Abrufs von
Stellenangeboten auf der Grundlage von bestimmten Jobtiteln und Standorten. Der Scraper extrahiert Details wie Jobtitel,
ID, URL, Unternehmen, Ort, Beschäftigungsart, Gehalt und Joblevel.

Die exportierten Daten sind Rohdaten, die für eine Datenanalyse weiterverarbeitet werden müssen. Einige
Analyseinstrumente sind mit dem Paket mitgeliefert.

---

## Features

- Automated job search and data extraction from Karriere.at
- Uses Selenium WebDriver for web scraping
- Proxy support for anonymous requests
- Software can scrape many job types and locations in one run
- Saves extracted job data to a CSV file

## Requirements

- Python 3.x
- Selenium
- a WebDriver (Geckodriver, Chromedriver, or Microsoft Edge WebDriver)
- [FreeProxy](https://github.com/jundymek/free-proxy) (for proxy support)
- Pandas (for data processing)
- Numpy,
- Matplotlib,
- Seaborn

### Webdriver note

Selenium requires a web driver to work, it depends on your browser. This software supports firefox, chrome, and
Microsoft Edge. Firefox was the target browser during development.

You can find webdrivers in the official sources:

- Firefox - [Geckodriver](https://firefox-source-docs.mozilla.org/testing/geckodriver/index.html)
- Google Chrome - [ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads)
- Microsoft
  Edge - [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver?form=MA13LH)

### Data integrity note

The website underwent a design change in 2025. Currently, similar elements on two different pages may have two different
classes. For example, the labels 'salary' and 'location' may have a similar class without any IDs or unique styles.
Unfortunately, this software will not collect this data. This issue will be addressed later.

---

## Quick start

All you have to do is to decide what jobs and in what locations you want to find.

```python
from karriere_at_scraper import KarriereAtScraper

# Creates a parser object with a driver of your choice
# Browser options are "firefox", "chrome" and "edge"
# Don't forget to provide respective drivers, they are installed separately
kp = KarriereAtScraper("firefox", "path/to/driver")

jobs = ["Software Entwickler", "IT"]
locations = ["Wien", "Salzburg", "Graz"]

kp.fetch_jobs(jobs, locations)  # fetches data and stores it in the object
df = kp.get_df()  # returns pandas dataframe
```

Gathering information may take considerable time depending on your machine. To avoid the need for repeated scraping, the
results are automatically saved in csv to the runtime directory.

---

## Functions

### fetch_jobs

A callable that initiates parsing.

```python
from karriere_at_scraper import KarriereAtScraper

kp = KarriereAtScraper("firefox", "path/to/driver")
...
kp.fetch_jobs(jobs_list=[], locations=[], remove_duplicates=True, csv_name="", length_limit=9999, export=True)
```

A stored dataframe is not being cleared when this function is called. You'll need to clean it manually
with ```clear_df``` function.

#### Parameters

* ```jobs_list``` (list): A list of job titles or keywords to search for. This parameter is mandatory.
* ```locations``` (list): A list of geographical locations where the jobs should be searched. This parameter is
  mandatory.
* ```use_proxy``` (bool, optional): True if you want to connect with proxy. Defaults to True. Keep in mind that it may be unstable at times.
* ```remove_duplicates``` (bool, optional): If set to True, duplicate job entries will be removed from the resulting
  DataFrame. Defaults to True.
* ```csv_name``` (str, optional): The desired name for the output CSV file. If left as an empty string (default), a name
  will
  be automatically generated.
* ```length_limit``` (int, optional): A hard limit for the maximum number of jobs to fetch. Defaults to 9999.
* ```export``` (bool, optional): If set to True, the fetched jobs will be automatically exported to a .csv file.
  Defaults to
  True.

#### Returns

* pandas.DataFrame: A DataFrame containing the parsed job listings. This DataFrame is also stored internally as
  self.current_df.

### export_df_to_csv

Exports the current dataframe to a csv file.

```python
from karriere_at_scraper import KarriereAtScraper

kp = KarriereAtScraper("firefox", "path/to/driver")
...
kp.export_df_to_csv(csv_name="")
```

#### Parameters

* csv_name: string, the name of the csv file

### get_df

Returns current dataframe.

```python
from karriere_at_scraper import KarriereAtScraper

kp = KarriereAtScraper("firefox", "path/to/driver")
...
df = kp.get_df()
```

### clear_df

Manually removes all the entries from the stored dataframe.

```python
from karriere_at_scraper import KarriereAtScraper

kp = KarriereAtScraper("firefox", "path/to/driver")
...
kp.clear_df()
```

---

## Analysing the collected data

This software provides some tools to analyse and visualise the collected data.

### process_salaries

Initially, the data are not normalised in any way after collection. Calling this function will add columns to the
dataframe with the maximum, minimum, and estimated average monthly salary based on the available data.

```python
from karriere_at_scraper import process_salaries

df = ...
process_salaries(df)
```

### draw_salaries_chart

After calling ```process_salaries``` you can draw a salaries distribution chart.
It includes average and median values, 25 and 75 percentiles and a kernel density estimate.
It drops extreme values automatically using interquartile range.

You can choose two locales for labels - English ("en", default) and German ("de")

```python
from karriere_at_scraper import process_salaries, draw_salaries_chart

df = ...
process_salaries(df)
draw_salaries_chart(df, locale="de")
```

### draw_employment_types_chart

This function draws a distribution chart of available employment types among job offers.

```python
from karriere
```

---

### draw_employment_types_chart

This function allows you to draw a distribution chart of available employment types.

You can choose two locales for labels - English ("en", default) and German ("de"). Keep in mind that employmen types' labels are not translated and are displayed as on the website (in german).

```python
from karriere_at_scraper import draw_employment_types_chart

df = ...
draw_employment_types_chart(df, locale="de")
```

## License

This is open software. It is distributed under the [European Union Public License v 1.2](LICENSE).

