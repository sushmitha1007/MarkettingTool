import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
import xlsxwriter
import time
from linkedinscraper.utils.logger import create_error_log
import csv
import datetime
import openpyxl
from selenium import webdriver

# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)" \
#              " Chrome/89.0.4389.114 Safari/537.36"
# options = webdriver.ChromeOptions()
# options.headless = True
# options.add_argument(f'user-agent={user_agent}')
# options.add_argument("--window-size=1920,1080")
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--allow-running-insecure-content')
# options.add_argument("--disable-extensions")
# options.add_argument("--proxy-server='direct://'")
# options.add_argument("--proxy-bypass-list=*")
# options.add_argument("--start-maximized")
# options.add_argument('--disable-gpu')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-popup-blocking')
# driver = webdriver.Chrome(executable_path = "chromedriver.exe", options = options)  # Initializing driver


# not being used currently
def containsInclusionWord(title, description):
    list_ = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
             "v", "w", "x", "y", "z"]

    if any(keyword.lower() in title.lower() for keyword in list_) or any(
            keyword.lower() in description.lower() for keyword in list_):
        return True
    else:
        return False

def write_dict_to_csv(dict_data):
    csv_columns = ['Company','link','title','description', 'searchurl', 'Name','Designation']
    csv_file = "output.csv"
    try:
        with open(csv_file, 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

# function to validate scraped urls against linkedin respective url's
def parse_results(driver, df):
    # return type(df)
    found_results = []
    links = []
    print(type(df.iterrows))
    print(df.iterrows)
    for index, row in df.iterrows():
        # if (index == 35):
        #     break
        # #perform validation on input params
        if str(row['Designation']) == "nan" or str(row['Company']) == "nan":
            continue
        if str(row['Name']) != "nan":
            homelink = "https://www.google.co.in/search?q=site:linkedin.com ({} , {}, {})".format(row['Name'],
                                                                                                  row['Designation'],
                                                                                                  row['Company'])
        else:
            homelink = "https://www.google.co.in/search?q=site:linkedin.com ({}, {})".format(row['Designation'],
                                                                                             row['Company'])

        company = row['Company']
        print("Checking url:" + company + "::" + homelink)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
        driver.get(str(homelink).strip())
        time.sleep(2)
        result_block = driver.find_elements_by_class_name('g')
        print(result_block)
        # print("class g for google")
        # print(page)
        # soup = BeautifulSoup(page.content, 'html.parser')

        rank = 0
        #time.sleep(2)
        # result_block = soup.findAll("div", {"class": "g"})
        print("Number of results:", len(result_block))

        try:

            for result in result_block:
                link = result.find_element_by_tag_name('a')
                # print(link)
                #time.sleep(1)
                title = result.find_element_by_tag_name('h3')
                # result.find('span', attrs = {'class': 'aCOpRe'})
                #time.sleep(1)
                description = result.find_element_by_class_name("IsZvec").text
                # description = " "
                print(description)
                #time.sleep(1)
                if link and title:
                    link = link.get_attribute("href")
                    print(link)
                    time.sleep(1)
                    title = title.text
                    print(title)
                    time.sleep(1)
                    # if description:
                    #     description = description.get_text()
                    # else:
                    #     description = ''
                    if link != '#' and "linkedin" in str(link):
                        # print("appending link", link)
                        found_results.append(
                            {'Company': company, 'link': link, 'title': title, 'description': description,
                             'searchurl': homelink, 'Name': row['Name'], "Designation": row['Designation']
                             })
                        links.append(link)
                        rank += 1

            if rank == 0:
                print("no results found for :" + homelink)
            # if  rank % 10 == 0 :
            #     write_dict_to_csv(found_results)
            #     found_results = []
            time.sleep(30)
        except AssertionError:
            print("Incorrect arguments parsed to function")
            e = "Incorrect arguments parsed to function"
            create_error_log(e)
        except requests.HTTPError:
            print("You appear to have been blocked by Google")
            e = "You appear to have been blocked by Google"
            create_error_log(e)
        except requests.RequestException:
            print("Appears to be an issue with your connection")
            e = "Appears to be an issue with your connection"
            create_error_log(e)
    return found_results
