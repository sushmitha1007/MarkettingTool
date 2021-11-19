# Linkedin Profile scraper
from selenium import webdriver
from bs4 import BeautifulSoup
import crochet
from typing import Optional

crochet.setup()
from datetime import datetime
import uvicorn
import pandas as pd

from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
import os

from fastapi.responses import JSONResponse
from word_count_git.info_scraper.info_scraper.spiders.info import DatabloggerSpider
from word_count_git.error_handler.error_handler import InternalServerError, JsonSyntaxError, SuccessResponse
from word_count_git.utils.logger import create_error_log
from word_count_git.utils.to_excel import write_to_excel
from word_count_git.utils.dropboxFileUploadword import upload_to_dropbox_word
from fastapi import FastAPI, UploadFile, File, Form

from linkedinscraper.config import constants
from linkedinscraper.error_handler.error_handler import InternalServerError, JsonSyntaxError, SuccessResponse
from linkedinscraper.utils.logger import create_error_log
from linkedinscraper.utils.to_excel import read_excel_linked, createFileWithDetaillList
from linkedinscraper.utils.dropboxFileUpload import upload_to_dropbox
from linkedinscraper.core.LinkedInGoogleSearcher_Gen import parse_results

import codecs
import re

# from gmbcontractscraper.config import constants
# from gmbcontractscraper.config.constants import OUTPUT_FOLDERNAME
# from gmbcontractscraper.Scrape.demo_project.spiders.datascraper import DatabloggerSpiderScraper
# from gmbcontractscraper.error_handler.error_handler import InternalServerError, JsonSyntaxError, SuccessResponse
# from gmbcontractscraper.utils.logger import create_error_log_message
# from gmbcontractscraper.utils.to_excel_scraper import write_to_excel_scraper, read_excel
# from gmbcontractscraper.utils.dropboxFileUpload_scraper import upload_to_dropbox_scrapy
import sys

# print(sys.path)
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
output_data = []

crawl_runner = CrawlerRunner()
code_value = ["POO567", "RIJ257", "KAR964"]
# Web Scarping
Title = []
Rating = []
NumberOfReviews = []
Address = []
Pages = []
MobileNo = []
Website = []
Description = []
excelArray = []
# For Headless Browser
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
# driver = webdriver.Chrome(executable_path="./chromedriver", options=options)  # Initializing driver
driver = webdriver.Chrome("./chromedriver")

name1 = []
loc = []
Company_name = []
connection11 = []
website = []
linked_in = []
email = []
twitter = []
Phone = []


@app.post("/gf/scraper/linkedin/profile", tags=['Linkedin_Profile_Scraper'])
def linkedin_profile_scraper(code: str = Form(...), fileb: UploadFile = File(...)):
    """
            This API takes list of urls as input in a csv file .
            It scrapes the Linkedin profile details and the data obtained is saved in the company dropbox account.
            The following data is obtained for each business listing:
            - **Name**
            - **Location**
            - **Company_name**
            - **Connection**
            - **Linkedin Url**
            - **Website**
            - **twitter**
            - **email**
        """
    if code in code_value:
        name = fileb.filename
        create_error_log(name)
        driver.get('https://www.linkedin.com')
        username = driver.find_element_by_name('session_key')
        username.send_keys('sushmithasherigar1998@gmail.com')
        time.sleep(1)
        password = driver.find_element_by_name('session_password')
        password.send_keys('Sush@1007')
        time.sleep(1)
        # Login to LinkedIn account.
        login_button = driver.find_element_by_class_name('sign-in-form__submit-button')
        login_button.click()
        # driver.find_element_by_class_name('linkedin-logo').click()
        contents = fileb.file.read()
        # return contents
        byte_to_string = codecs.decode(contents, "utf-8")  # convert byte to string
        # return byte_to_string
        regex = re.compile(r'[\r\t]')
        string = regex.sub(" ", byte_to_string)
        # remove_first_line = string[9:]
        # s =next(string)
        # print(s)
        output = string.split(" \n")
        del output[0]
        # print(output)
        for i in range(len(output) - 1):
            # print(output[i])

            profile_url = output[i]
            # Getting each url
            driver.get(profile_url)
            # Scroll down to last page.
            Scroll_pause_Time = 5
            last_height = driver.execute_script('return document.body.scrollHeight')
            for j in range(3):
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                time.sleep(Scroll_pause_Time)
                new_height = driver.execute_script('return document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height
            # page_source method is used retrieve the page source of the webpage the user is currently accessing.
            src = driver.page_source
            soup = BeautifulSoup(src, 'lxml')
            time.sleep(4)
            # print(soup)
            # Extracting name using BeautifulSoup.
            try:
                name_div = soup.find('div', {'class': 'mt2 relative'})
                time.sleep(4)
                name_loc = soup.find('ul', {'class': 'pv-top-card--list pv-top-card--list-bullet display-flex pb1'})
                time.sleep(4)
                try:
                    no_connection = name_loc.find(('span', {'class': 't-bold'})).get_text().strip()
                    create_error_log(no_connection)
                    print(no_connection)
                    connection11.append(no_connection)
                    time.sleep(4)
                except Exception as e:
                    print("not found")
                    connection11.append("connection not foud")
                    create_error_log(e)
                try:
                    colege_name = name_div.find('span', {
                        'class': 'text-body-small inline t-black--light break-words'}).get_text().strip()
                    create_error_log(colege_name)
                    print(colege_name)
                    Company_name.append(colege_name)
                    time.sleep(4)
                except Exception as e:
                    print("not found")
                    Company_name.append("company not found")
                    create_error_log(e)
                try:
                    loc_fetch = name_div.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()
                    print(loc_fetch)
                    create_error_log(loc_fetch)

                    loc.append(loc_fetch)
                    time.sleep(4)
                except Exception as e:
                    print("loacton not found")
                    loc.append("location not found")
                    create_error_log(e)
                try:
                    name_fetch = name_div.find('h1',
                                               {'class': 'text-heading-xlarge inline t-24 v-align-middle break-words'
                                                }).get_text().strip()
                    create_error_log(name_fetch)
                    print(name_fetch)
                    name1.append(name_fetch)
                    time.sleep(4)
                except Exception as e:
                    name1.append("name not found")
                    create_error_log(e)

                # Extracting location and name . In name_loc ,ul has 2 li's, first li contains name and second li
                # contains location.

                # Execute Javascript code on webpage
                driver.execute_script(
                    "(function(){try{for(i in document.getElementsByTagName('a')){let el = "
                    "document.getElementsByTagName('a')[i]; "
                    "if(el.innerHTML.includes('Contact info')){el.click();}}}catch(e){}})()")
                # Wait 5 seconds for the page to load
                time.sleep(4)
                # Scrape the linkedin url from the 'Contact info' popup
                linkedin_profile = driver.execute_script(
                    "return (function(){try{for (i in document.getElementsByClassName("
                    "'pv-contact-info__contact-type')){ let el = "
                    "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
                    "'ci-vanity-url')){ "
                    "return el.children[2].children[0].innerText; } }} catch(e){return '';}})()")
                print(linkedin_profile)
                linked_in.append(linkedin_profile)
                # Scrape the website from the 'Contact info' popup
                website1 = driver.execute_script(
                    "return (function(){try{for (i in document.getElementsByClassName("
                    "'pv-contact-info__contact-type')){ let el = "
                    "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
                    "'ci-websites')){ "
                    "return el.children[2].children[0].innerText; } }} catch(e){return 'website not found';}})()")
                print(website1)
                website.append(website1)
                create_error_log(website1)
                # Scrape the twitter link from the 'Contact info' popup
                twitter1 = driver.execute_script(
                    "return (function(){try{for (i in document.getElementsByClassName("
                    "'pv-contact-info__contact-type')){ let el = "
                    "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
                    "'ci-twitter')){ "
                    "return el.children[2].children[0].innerText; } }} catch(e){return 'twitter not found';}})()")
                print(twitter1)
                twitter.append(twitter1)
                # Scrape the email address from the 'Contact info' popup

                phone = driver.execute_script(
                    "return (function(){try{for (i in document.getElementsByClassName("
                    "'pv-contact-info__contact-type')){ let el = "
                    "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
                    "'ci-phone')){ "
                    "return el.children[2].children[0].innerText; } }} catch(e){return 'phone not found';}})()")
                print(phone)
                Phone.append(phone)
                email1 = driver.execute_script(
                    "return (function(){try{for (i in document.getElementsByClassName("
                    "'pv-contact-info__contact-type')){ let el = "
                    "document.getElementsByClassName('pv-contact-info__contact-type')[i]; if(el.className.includes("
                    "'ci-email')){ "
                    "return el.children[2].children[0].innerText; } }} catch(e){return 'email not found';}})()")
                print(email1)
                email.append(email1)

            except Exception as e:
                create_error_log(e)
        print(len(name1))
        print(len(loc))
        print(len(Company_name))
        print(len(connection11))
        print(len(linked_in))
        print(len(website))
        print(len(twitter))
        print(len(email))
        print(len(Phone))
        print(name)
        df = pd.DataFrame(
            {'Name': name1, 'Location': loc, 'company_name': Company_name, 'connection': connection11,
             'linkedin url': linked_in,
             'website': website, 'twitter': twitter, 'email': email, 'phone': Phone
             })  # Initialize every field with the resultant array
        # y = input("Xls  Name :")  # Input excel name
        file_path = os.path.join(os.getcwd(), "output",
                                 name + '_Linkedin_profile_scraper_output_{}.xlsx'.format(
                                     datetime.now().strftime('%d%m%y-%H%M%S')))
        df.to_excel(file_path, index=False)

        create_error_log("Saved successfully")
        try:
            status = upload_to_dropbox(file_path)
            create_error_log("uploaded")
            if status:
                return True
            else:
                return False

        except Exception as e:
            create_error_log("exception" + str(e))
    else:
        return "Login Failed"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
