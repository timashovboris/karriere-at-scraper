import re
import time
from datetime import datetime

import pandas as pd
from fp.fp import FreeProxy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class KarriereAtParser:
    def __init__(self, geckodriver_dir):

        self.geckodriver_dir = geckodriver_dir

        self.driver = None

        df_columns = ["Name", "ID", "URL", "Company", "Location", "Employment type", "Salary", "Experience"]
        self.current_df = pd.DataFrame([], columns=df_columns)

    def create_driver(self, use_proxy=True):
        if isinstance(self.driver, WebDriver):
            self.driver.quit()

        # region driver setup
        gecko_options = Options()
        gecko_options.add_argument("--headless")  # Run in headless mode
        gecko_options.add_argument("--width=1920")
        gecko_options.add_argument("--height=1080")
        if use_proxy:
            use_proxy = FreeProxy().get()
            gecko_options.add_argument(f"--proxy-server={use_proxy}")
            print(f"=== Driver created under the proxy {use_proxy} ===")
        else:
            print(f"=== Driver created ===")
        service = Service(self.geckodriver_dir)  # Update with the path to your WebDriver
        self.driver = webdriver.Firefox(service=service, options=gecko_options)

    def get_df(self):
        return self.current_df

    def build_links(self, jobs, location):
        base_url = "https://www.karriere.at/jobs"

        # Ensure jobs is a list for uniform processing
        if isinstance(jobs, str):
            jobs = [jobs]

        # Process each job to build the URL
        job_links = []
        for job in jobs:
            job_formatted = job.lower().replace(" ", "-")
            location_formatted = location.lower().replace(" ", "-")
            job_links.append(f"{base_url}/{job_formatted}/{location_formatted}")

        # Return a single URL if only one job was provided, otherwise return the list
        return job_links

    def get_element_text(self, how, name, default_value="N/A", driver=None):
        if driver is None:
            driver = self.driver

        try:
            element = driver.find_element(how, name)
            return element.text.strip()
        except NoSuchElementException:
            return default_value
        except Exception:
            print(f"! Exception encountered while getting text of {name}")
            return "EXCEPTION"

    def remove_element(self, how, name, driver=None):
        if driver is None:
            driver = self.driver

        try:
            to_remove = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((how, name))
            )
            driver.execute_script("arguments[0].remove();", to_remove)
        except Exception:
            print(f"! Failed to remove element of {name};")

    def fetch_jobs_data(self, urls, limit=9999, use_proxy = True):
        base_url = "https://www.karriere.at/jobs"

        self.create_driver()

        self.driver.get(base_url)

        # Wait until the searchbar is loaded and click on empty space to activate the page
        searchbar_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'keywords'))
        )

        searchbar_element.click()

        # Deny the cookies
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'onetrust-reject-all-handler'))
            )
            element.click()
            time.sleep(2)
            print("+ Cookies successfully denied")
        except:
            print("- Cookies are not required this time")

        df_len_modifier = 0

        start_time = time.time()
        full_exec_time = 0

        for url in urls:
            print(f"== Start scraping through {url} ==")
            self.driver.get(url)

            # Wait until the list is loaded and click to activate the page
            job_listing_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'm-jobsSearchList__activeJobs'))
            )

            # Remove the disruptor pill
            self.remove_element(By.CLASS_NAME, 'm-alarmDisruptorPill__pill')

            # Check how many jobs to expect
            total_jobs_expected = self.get_element_text(By.CLASS_NAME, "m-jobsListHeader__title").split()[0]
            total_jobs_expected = int(total_jobs_expected) if total_jobs_expected.isdigit() else 0
            print(f"For this search a total of {total_jobs_expected} jobs is expected to be parsed")

            more_available = True
            item_counter = 0
            df_len_modifier += len(self.current_df)

            while more_available and len(self.current_df) < limit and item_counter < total_jobs_expected:
                # Iterate through jobs
                job_listing_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@class='m-jobsSearchList__activeJobs']"))
                )

                job_items = job_listing_container.find_elements(By.CLASS_NAME,
                                                                "m-jobsListItem--active")  # It will contain jobs, as well as "load more" button and some footer info

                for job_ind in range(item_counter, len(job_items)):
                    try:
                        job = job_items[job_ind]
                        job_name_element = job.find_element(By.CLASS_NAME, "m-jobsListItem__title")
                        job_name_element.click()

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '.m-jobContent__iFrame'))
                        )

                        job_name = job_name_element.text
                        job_url = self.driver.current_url

                        id_pattern = r'[^#]+$'
                        job_id = re.search(id_pattern, job_url).group(0)

                        job_url = f"{base_url}/{job_id}"

                        job_company = self.get_element_text(By.CLASS_NAME, 'm-jobsListItem__company', driver=job)
                        job_location = self.get_element_text(By.CSS_SELECTOR, '.m-keyfactBox__jobLocations')
                        job_employment_types = self.get_element_text(By.CSS_SELECTOR,
                                                                     '.m-keyfactBox__jobEmploymentTypes')
                        job_salary = self.get_element_text(By.CSS_SELECTOR,
                                                           '.m-keyfactBox__jobSalaryRange')
                        job_experience = self.get_element_text(By.CSS_SELECTOR, '.m-keyfactBox__jobLevel')

                        data = [job_name, job_id, job_url, job_company, job_location, job_employment_types, job_salary,
                                job_experience]
                        self.current_df.loc[item_counter + df_len_modifier] = data

                    except Exception as e:
                        print("An exception while parsing jobs", e)
                        self.driver.save_screenshot(f"crash_on_{item_counter}.png")

                    item_counter += 1

                # Try to find "Load more" button, quit if none
                try:
                    load_more_btn = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'm-loadMoreJobsButton__button'))
                    )
                    load_more_btn.click()

                    WebDriverWait(self.driver, 5).until(
                        lambda d: len(job_listing_container.find_elements(By.XPATH,
                                                                          "//*[@class='m-jobsList__item']")) > item_counter
                    )
                except TimeoutException:
                    # This will catch the case where the element is not found within the timeout
                    more_available = False
                except NoSuchElementException:
                    # This will catch the case where the element is not found after the wait
                    more_available = False
                except Exception as e:
                    more_available = False

            cur_time = time.time()
            cur_exec_time = cur_time - (start_time + full_exec_time)
            full_exec_time = cur_time - start_time

            print(f"Execution time: total {full_exec_time} sec, this url {cur_exec_time};")
            print(
                f"Speed: {full_exec_time / max(1, df_len_modifier + item_counter)} in total, {cur_exec_time / max(1, item_counter)} sec/elem in current url;")

        self.driver.quit()

        print("=== Finished parsing ===")

        self.current_df = self.current_df.drop_duplicates(subset="ID", keep='last')

    def fetch_jobs(self, jobs_list, location, length_limit=9999, auto_export=True):
        urls = self.build_links(jobs_list, location)
        self.fetch_jobs_data(urls, length_limit)
        if len(self.current_df) == 0:
            print("! No jobs were found")
        else:
            print(f"! {len(self.current_df)} jobs were found")
            if auto_export:
                self.current_df.to_csv(
                    f"karriere_at_paring_{jobs_list[0].replace(' ', '_')}_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.csv")
                print("! Exported data to csv")

        return self.current_df
