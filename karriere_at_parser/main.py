import re
import time
from datetime import datetime

import pandas as pd
from fp.fp import FreeProxy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class KarriereAtParser:
    # Website base url
    BASE_URL = "https://www.karriere.at/jobs"

    # Columns for dataframe
    DF_COLUMNS = ["Name", "ID", "URL", "Company", "Location", "Employment type", "Salary", "Experience"]

    # IDs and classes of utility elements
    SEARCHBAR_ID = 'keywords'
    COOKIE_DENY_ID = 'onetrust-reject-all-handler'
    JOB_LIST_HEADER_CLASS = 'm-jobsListHeader__title'
    JOB_LIST_CLASS = 'm-jobsSearchList__activeJobs'
    DISRUPTOR_CLASS = 'm-alarmDisruptorPill__pill'
    ACTIVE_JOBS_CLASS = 'm-jobsListItem--active'
    JOB_IFRAME_SELECTOR = '.m-jobContent__iFrame'
    LOAD_MORE_BTN_CLASS = 'm-loadMoreJobsButton__button'

    # IDs and Classes of job fields
    JOB_TITLE_CLASS = 'm-jobsListItem__title'
    COMPANY = 'm-jobsListItem__company'
    LOCATION = '.m-keyfactBox__jobLocations'
    EMPLOYMENT_TYPE = '.m-keyfactBox__jobEmploymentTypes'
    SALARY = '.m-keyfactBox__jobSalaryRange'
    EXPERIENCE = '.m-keyfactBox__jobLevel'

    # Utility values
    WAIT_TIMER = 5
    DRIVER_RETRIES = 2

    def __init__(self, geckodriver_dir):
        self.__geckodriver_dir = geckodriver_dir
        self.__driver = None
        self.__current_df = pd.DataFrame([], columns=self.DF_COLUMNS)

    def get_df(self):
        """Returns current dataframe"""
        return self.__current_df

    def __create_driver(self, use_proxy=True):
        """
        Creates selenium webdriver

        :param use_proxy: True if you want to connect with a proxy
        """

        # Check if driver already exists
        if self.__driver:
            self.__driver.quit()

        # region Driver setup
        gecko_options = Options()
        gecko_options.add_argument("--headless")  # Run in headless mode
        gecko_options.add_argument("--width=1920")
        gecko_options.add_argument("--height=1080")
        # Add proxy when required
        if use_proxy:
            use_proxy = FreeProxy().get()
            gecko_options.add_argument(f"--proxy-server={use_proxy}")
            print(f"=== Driver created under the proxy {use_proxy} ===")
        else:
            print(f"=== Driver created ===")
        # Updated with the path to WebDriver
        service = Service(self.__geckodriver_dir)
        # endregion

        self.__driver = webdriver.Firefox(service=service, options=gecko_options)

    def __build_links(self, jobs, locations):
        """
        Creates a list of URLs
        :param jobs: a list of jobs
        :param locations: a list of locations
        :return: a list of URLs
        """
        # If a single string is given
        if isinstance(jobs, str):
            jobs = [jobs]
        # Create urls
        job_links = [
            f"{self.BASE_URL}/{job.lower().replace(' ', '-')}/{location.lower().replace(' ', '-')}"
            for job in jobs
            for location in locations
        ]
        return job_links

    def __get_element(self, how, name, driver=None, hard=False):
        """
        Tries to get an element from a page, will retry if encounters a StaleElementReferenceException

        :param how: how to get the element (selenium.webdriver.common.by.By). Example: By.ID
        :param name: a value to be used with "how" - selector for a By.CSS_SELECTOR, id for By.ID, etc.
        :param driver: a custom selenium webdriver (or element), self.driver by default
        :param hard: False to wait before trying to get an element, True to do it straight ahead, False by default
        :return: a WebElement or None
        """

        driver = driver or self.__driver  # If no custom driver provided

        for attempt in range(self.DRIVER_RETRIES):
            try:
                if not hard:  # if wanted to wait before getting an element
                    element = WebDriverWait(driver, self.WAIT_TIMER).until(
                        ec.presence_of_element_located((how, name))
                    )
                else:  # if wanted to try to get an element straight ahead
                    element = driver.find_element(how, name)
                return element
            except StaleElementReferenceException:
                if attempt < self.DRIVER_RETRIES:
                    # Element disappeared from DOM, will retry
                    pass
                else:
                    # Element disappeared from DOM after retrying
                    return None
            except (NoSuchElementException, TimeoutException):
                return None
            except Exception as e:
                print(f"Failed to get element of {name}: {e}")
                return None

        return None

    def __get_elements(self, how, name, driver=None):
        """
        Returns a list of WebElements, handles a NoSuchElementException, will wait before trying to get elements

        :param how: how to get the element (selenium.webdriver.common.by.By). Example: By.ID
        :param name: a value to be used with "how" - selector for a By.CSS_SELECTOR, id for By.ID, etc.
        :param driver: a custom selenium webdriver (or element), self.driver by default
        :return: a list of WebElements or an empty list
        """

        # If no custom driver provided
        if driver is None:
            driver = self.__driver
        try:
            return WebDriverWait(driver, self.WAIT_TIMER).until(
                ec.presence_of_all_elements_located((how, name))
            )
        except NoSuchElementException:
            return []
        except Exception as e:
            print(f"! Failed to get elements of {name}: {e}")
            return []

    def __get_element_text(self, how, name, default_value="N/A", driver=None, hard=False):
        """
        Gets a WebElement and returns its text

        :param how: how to get the element (selenium.webdriver.common.by.By). Example: By.ID
        :param name: a value to be used with "how" - selector for a By.CSS_SELECTOR, id for By.ID, etc.
        :param default_value: default string value
        :param driver: a custom selenium webdriver (or element), self.driver by default
        :param hard: False to wait before trying to get an element, True to do it straight ahead, False by default
        :return:
        """

        driver = driver or self.__driver

        for attempt in range(self.DRIVER_RETRIES):  # Retry once
            try:
                # Re-fetch the element right before getting its text
                elem = self.__get_element(how, name, driver, hard)
                if elem is None:
                    return default_value
                else:
                    res = elem.text.strip()
                    return res
            except StaleElementReferenceException:
                if attempt < 1:
                    pass
                    # print(f"Element {name} disappeared from DOM while getting text. Retrying...")
                else:
                    # print(f"Element {name} disappeared from DOM after retry while getting text.")
                    return "EXCEPTION"
            except Exception as e:
                print(f"Exception encountered while getting text of {name}: {e}")
                return "EXCEPTION"

        return default_value

    def __remove_element(self, how, name):
        """
        Removes an element from the page

        :param how: how to get the element (selenium.webdriver.common.by.By). Example: By.ID
        :param name: a value to be used with "how" - selector for a By.CSS_SELECTOR, id for By.ID, etc.
        :return: True if the element was removed, False otherwise
        """
        try:
            to_remove = self.__get_element(how, name)
            self.__driver.execute_script("arguments[0].remove();", to_remove)
            return True
        except Exception as e:
            print(f"! Failed to remove element of {name}: {e}")
            return False

    def __deny_cookies(self):
        """
        Waits for a cookies request and declines it
        :return: True if cookies were declined, False otherwise
        """
        try:
            element = self.__get_element(By.ID, self.COOKIE_DENY_ID)
            element.click()
            time.sleep(2)
            print("+ Cookies successfully denied")
            return True
        except Exception:
            print("- Cookies are not required this time")
            return False

    def __fetch_jobs_data(self, urls, limit=9999, use_proxy=True):
        """
        Fetches all the available jobs for all provided URLs, only unique entries are kept, data is stored in a current_df
        :param urls: a list of URLs
        :param limit: a hard limit on how many jobs to fetch
        :param use_proxy: True if you want to connect with proxy
        """
        self.__create_driver(use_proxy=use_proxy)

        self.__driver.get(self.BASE_URL)

        # region Wait until the searchbar is loaded and click on empty space to activate the page
        searchbar_element = self.__get_element(By.ID, self.SEARCHBAR_ID)
        searchbar_element.click()
        # endregion

        # Deny the cookies
        self.__deny_cookies()

        df_len_modifier = 0  # It stores how many items are already stored in self.df
        start_time = time.time()  # The time when parsing started after creating self.driver
        full_exec_time = 0  # Time of processing all urls

        for url in urls:
            print(f"== Start scraping through {url} ==")
            self.__driver.get(url)

            # Wait until the list is loaded and get the number of available jobs
            job_listing_amount = self.__get_element_text(By.CLASS_NAME, self.JOB_LIST_HEADER_CLASS).split()[0]

            # Check how many jobs to expect
            total_jobs_expected = int(job_listing_amount) if job_listing_amount.isdigit() else 0
            print(f"For this search a total of {total_jobs_expected} jobs is expected to be parsed")
            print("=" * 12)

            # Remove the disruptor pill
            self.__remove_element(By.CLASS_NAME, 'm-alarmDisruptorPill__pill')

            more_available = True  # If it's possible to "load more"
            item_counter = 0  # How many items were on this page
            df_len_modifier += len(self.__current_df)

            while more_available and len(self.__current_df) < limit and item_counter < total_jobs_expected:
                # Load all available jobs, as well as "load more" button and some footer info
                job_items = self.__get_elements(By.CLASS_NAME, self.ACTIVE_JOBS_CLASS)

                # Iterate through jobs
                for job_ind in range(item_counter, len(job_items)):
                    try:
                        job = job_items[job_ind]
                        job_name_element = self.__get_element(By.CLASS_NAME, self.JOB_TITLE_CLASS, driver=job)
                        job_name_element.click()

                        self.__get_element(By.CSS_SELECTOR, self.JOB_IFRAME_SELECTOR)

                        job_name = job_name_element.text
                        job_url = self.__driver.current_url

                        id_pattern = r'[^#]+$'
                        job_id = re.search(id_pattern, job_url).group(0)

                        job_url = f"{self.BASE_URL}/{job_id}"

                        job_company = self.__get_element_text(By.CLASS_NAME, 'm-jobsListItem__company', driver=job,
                                                              hard=True)
                        job_location = self.__get_element_text(By.CSS_SELECTOR, '.m-keyfactBox__jobLocations',
                                                               hard=True)
                        job_employment_types = self.__get_element_text(By.CSS_SELECTOR,
                                                                       '.m-keyfactBox__jobEmploymentTypes', hard=True)
                        job_salary = self.__get_element_text(By.CSS_SELECTOR, '.m-keyfactBox__jobSalaryRange',
                                                             hard=True)
                        job_experience = self.__get_element_text(By.CSS_SELECTOR, '.m-keyfactBox__jobLevel', hard=True)

                        data = [job_name, job_id, job_url, job_company, job_location, job_employment_types, job_salary,
                                job_experience]
                        self.__current_df.loc[item_counter + df_len_modifier] = data

                    except Exception as e:
                        print("An exception while parsing jobs", e)
                        self.__driver.save_screenshot(f"crash_on_{item_counter}.png")

                    item_counter += 1

                print(
                    f"{item_counter / total_jobs_expected:.2%} ({item_counter} / {total_jobs_expected} elements)")

                more_available = self.__load_more_jobs(item_counter)

            cur_time = time.time()
            cur_exec_time = cur_time - (start_time + full_exec_time)
            full_exec_time = cur_time - start_time

            print("=" * 12)
            print(f"Execution time: total {full_exec_time:.2f} sec, this url {cur_exec_time:.2f}")
            print(
                f"Speed: {full_exec_time / max(1, df_len_modifier + item_counter):.2f} in total, {cur_exec_time / max(1, item_counter):.2f} sec/elem in current url;")

        self.__driver.quit()

        print("=== Finished parsing ===")

        self.__current_df = self.__current_df.drop_duplicates(subset="ID", keep='last')

    def __load_more_jobs(self, item_counter):
        """
        Clicks a load-more button and waits until it loads more jobs.
        :param item_counter: the last old element number
        :return: returns True if successful, False otherwise
        """

        try:
            load_more_btn = self.__get_element(By.CLASS_NAME, self.LOAD_MORE_BTN_CLASS, hard=True)
            if load_more_btn is not None:
                load_more_btn.click()
            else:
                return False
            WebDriverWait(self.__driver, self.WAIT_TIMER).until(
                lambda d: len(d.find_elements(By.XPATH, "//*[@class='m-jobsList__item']")) > item_counter
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            print(f"Exception while loading more jobs: {e}")
            return False

    def fetch_jobs(self, jobs_list, locations, length_limit=9999, auto_export=True):
        """
        A callable function to initiate parsing
        :param jobs_list: a list of jobs
        :param locations: a list of locations
        :param length_limit: a hard limit for the number of jobs
        :param auto_export: True to automatically export jobs to .csv file, True by default
        :return: a dataframe with results (self.current_df)
        """
        urls = self.__build_links(jobs_list, locations)
        self.__fetch_jobs_data(urls, length_limit)
        if len(self.__current_df) == 0:
            print("! No jobs were found")
        else:
            print(f"! {len(self.__current_df)} jobs were found")
            if auto_export:
                self.__current_df.to_csv(
                    f"karriere_at_parsing_{"_und_".join(jobs_list)}_in_{"_und_".join(locations)}_am_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.csv".replace(' ','_'))
                print("! Exported data to csv")

        return self.__current_df
