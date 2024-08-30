import os
import datetime
from selenium import webdriver
import boto3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd


def get_jobs():
    options = Options()
    service = Service()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(service=service, options=options)

    url = "https://www.glassdoor.com/Job/remote-us-data-engineer-jobs-SRCH_IL.0,9_IS11047_KO10,23.htm"
    driver.get(url)

    time.sleep(50)

    company_name = []
    company_rating = []
    location = []
    job_title = []
    job_description = []
    company_size = []
    company_type = []
    company_revenue = []
    company_founded = []
    salary_estimate = []
    company_sector = []
    company_industry = []

    def extract_text(card, xpath, default="#N/A"):
        try:
            return card.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            return default

    done = False
    while not done:
        try:
            # Click load-more button if it exists
            try:
                driver.find_element(By.XPATH, ".//button[@data-test='load-more']").click()
                time.sleep(2)
            except NoSuchElementException:
                time.sleep(2)
                pass

            # Locate all job cards
            cards = driver.find_elements(By.XPATH, "//ul[@class='JobsList_jobsList__lqjTr']/li[@data-test='jobListing']")
            for card in cards:
                try:
                    driver.find_element(By.XPATH, ".//button[@class='CloseButton']").click()
                    print("X button touched")
                    time.sleep(2)
                except NoSuchElementException:
                    time.sleep(2)
                    pass

                card.click()

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ".//button[@class='JobDetails_showMore___Le6L']")))
                    driver.find_element(By.XPATH, ".//button[@class='JobDetails_showMore___Le6L']").click()
                    print("Button Clicked")
                except (NoSuchElementException, TimeoutException):
                    print("Button not clicked")
                    pass

                # Append values to lists
                job_title.append(extract_text(card, './/a[@data-test="job-title"]'))
                job_description.append(extract_text(driver, './/div[@class="JobDetails_jobDescription__uW_fK JobDetails_showHidden__C_FOA"]'))
                location.append(extract_text(card, './/div[@data-test="emp-location"]'))
                salary_estimate.append(extract_text(card, './/div[@data-test="detailSalary"]'))
                company_rating.append(extract_text(card, './/div[@class="EmployerProfile_ratingContainer__ul0Ef"]'))
                company_name.append(extract_text(card, './/div[@class="EmployerProfile_profileContainer__VjVBX EmployerProfile_compact__nP9vu"]'))

                company_sector_value = "#N/A"
                company_type_value = "#N/A"
                company_size_value = "#N/A"
                company_founded_value = "#N/A"
                company_revenue_value = "#N/A"
                company_industry_value = "#N/A"

                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ".//div[@class='JobDetails_overviewItem__cAsry']")))
                    overview_items = driver.find_elements(By.XPATH, ".//div[@class='JobDetails_overviewItem__cAsry']")
                    for item in overview_items:
                        label = item.find_element(By.XPATH, ".//span[@class='JobDetails_overviewItemLabel__KjFln']").text
                        value = item.find_element(By.XPATH, ".//div[@class='JobDetails_overviewItemValue__xn8EF']").text
                        if "Sector" in label:
                            company_sector_value = value
                        elif "Type" in label:
                            company_type_value = value
                        elif "Size" in label:
                            company_size_value = value
                        elif "Founded" in label:
                            company_founded_value = value
                        elif 'Revenue' in label:
                            company_revenue_value = value
                        elif 'Industry' in label:
                            company_industry_value = value

                except (NoSuchElementException, TimeoutException):
                    pass

                company_sector.append(company_sector_value)
                company_type.append(company_type_value)
                company_size.append(company_size_value)
                company_founded.append(company_founded_value)
                company_revenue.append(company_revenue_value)
                company_industry.append(company_industry_value)

            done = True

        except Exception as e:
            print(f"An error occurred: {e}")
            done = True

    driver.close()

    lists = [
        company_name, company_rating, location, job_title,
        job_description, company_size, company_type, company_revenue,
        company_founded, salary_estimate, company_sector, company_industry
    ]
    
    # Check lengths of all lists
    lengths = [len(lst) for lst in lists]
    print("Lengths of all lists: ", lengths)

    # Find the maximum length among the lists
    max_length = max(lengths)

    # Ensure all lists are of the same length by filling with '#N/A'
    def pad_list(lst, length, fill_value="#N/A"):
        return lst + [fill_value] * (length - len(lst))
    
    company_name = pad_list(company_name, max_length)
    company_rating = pad_list(company_rating, max_length)
    location = pad_list(location, max_length)
    job_title = pad_list(job_title, max_length)
    job_description = pad_list(job_description, max_length)
    company_size = pad_list(company_size, max_length)
    company_type = pad_list(company_type, max_length)
    company_revenue = pad_list(company_revenue, max_length)
    company_founded = pad_list(company_founded, max_length)
    salary_estimate = pad_list(salary_estimate, max_length)
    company_sector = pad_list(company_sector, max_length)
    company_industry = pad_list(company_industry, max_length)

    df = pd.DataFrame({
        'company': company_name, 
        'company_rating': company_rating,
        'location': location,
        'job_title': job_title,
        'job_description': job_description,
        'salary_estimate': salary_estimate,
        'company_size': company_size,
        'company_type': company_type,
        'company_sector': company_sector,
        'company_industry': company_industry,
        'company_founded': company_founded,
        'company_revenue': company_revenue
    })

    print(df.head())




path = "chromedriver"
get_jobs() 
