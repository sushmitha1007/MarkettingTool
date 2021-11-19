from selenium import webdriver
from bs4 import BeautifulSoup
import crochet

crochet.setup()
from datetime import datetime

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
from gmbcontractscraper.config import constants
from gmbcontractscraper.config.constants import OUTPUT_FOLDERNAME
from gmbcontractscraper.Scrape.demo_project.spiders.datascraper import DatabloggerSpiderScraper
from gmbcontractscraper.error_handler.error_handler import InternalServerError, JsonSyntaxError, SuccessResponse
from gmbcontractscraper.utils.logger import create_error_log_message
from gmbcontractscraper.utils.to_excel_scraper import write_to_excel_scraper, read_excel
from gmbcontractscraper.utils.dropboxFileUpload_scraper import upload_to_dropbox_scrapy

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
# driver = webdriver.Chrome(executable_path = "./chromedriver", options = options)  # Initializing driver

# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

# options = webdriver.ChromeOptions() 
# options.add_argument("start-maximized")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# driver = webdriver.Chrome(options=options, executable_path=r'./chromedriver.exe')
# driver.get("https://www.inipec.gov.it/cerca-pec/-/pecs/companies")

driver = webdriver.Chrome("./chromedriver")
@app.post("/gf/scraper/linkedin/salesnav", tags = ['Linkedin_salesnav'])
def linkedin_profile_scraper(code: str = Form(...), Username: str = Form(...), Password: str = Form(...),
                             Url: str = Form(...)):
    if code in code_value:
        driver.get('https://www.linkedin.com')
        username = driver.find_element_by_name('session_key')
        username.send_keys(Username)
        time.sleep(1)
        password = driver.find_element_by_name('session_password')
        password.send_keys(Password)
        time.sleep(1)
        # Login to LinkedIn account.
        login_button = driver.find_element_by_class_name('sign-in-form__submit-button')
        login_button.click()
        driver.get(Url)
        create_error_log("page loaded sleeping")
        time.sleep(7)
        while (True):
            try:
                try:
                    driver.find_element_by_class_name("bulk-actions__action-item").click()  # Clicking select all
                except:
                    break

                driver.find_element_by_css_selector("button[data-control-name ='account_list_bulk_add']").click()
                time.sleep(2)
                ul = driver.find_element_by_class_name("save-to-list-dropdown__no-max-height")  # .click()
                create_error_log(ul)
                ul.find_elements_by_tag_name("li")[0].click()
                create_error_log(ul)
                # print(li.text)
                # driver.find_element_by_id("ember5125").click()
                create_error_log("clicked li")
                time.sleep(2)
                # To scroll down
                Scroll_pause_Time = 5
                last_height = driver.execute_script('return document.body.scrollHeight')
                for j in range(3):
                    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                    time.sleep(Scroll_pause_Time)
                    new_height = driver.execute_script('return document.body.scrollHeight')
                    if new_height == last_height:
                        break
                    last_height = new_height
                driver.find_element_by_class_name("search-results__pagination-next-button").click()
                time.sleep(2)
            except Exception as e:
                create_error_log("no element found")


@app.post('/gf/scraper/gmb', tags = [' Google Business Listing Scraper'], summary = "upload_file_n_scraping")
def upload_file_n_scraping(code: str = Form(...), keyword: str = Form(...)):
    """
        This API takes list of keywords like ['Auto repair near michigan',
        'Pumps repair near arizona',
        'Hydraulic repair near kentucky USA',
        'Pneumatic repair near kentucky USA',
        'Motor repair near kentucky USA' ] as input in a csv file .
         It scrapes the google business listing and the data obtained is saved in the company dropbox account.
         The following data is obtained for each business listing:
        - **Name**
        - **Rating**
        - **NumberOfReviews**
        - **Address**
        - **MobileNumber**
        - **Website**
        - **Description**
    """
    if code in code_value:
        driver.get("https://google.co.in/search?q=" + keyword)  # Search the given url using chrome driver
        element = driver.find_element_by_class_name(
            'Q2MMlc')  # Finding Anchor tag of search result
        href = element.get_attribute('href')  # Extract the search result link
        driver.get(href)  # Open the extracted link
        names = driver.find_elements_by_class_name(
            'VkpGBb')  # Getting all the results of first page and it will return an array

        def extract_data(names):
            for name in names:
                try:
                    Title.append(name.find_element_by_tag_name('a').find_element_by_class_name(
                        'dbg0pd').text)  # 'dbg0pd' is the class name of the Title
                    # print(Title)
                    time.sleep(1.5)
                except Exception as e:  # try except because if the field is empty then it will throw an exception
                    create_error_log(e)
                    Title.append('Title not found')
                try:
                    Rating.append(name.find_element_by_tag_name('a').find_element_by_xpath(
                        './/span/div[1]/span').text)  # xpath uses to navigate in same directory
                    time.sleep(1.5)
                    # print(Rating)
                except Exception as e:
                    create_error_log(e)
                    Rating.append('Rating not found')
                try:
                    NumberOfReviews.append(
                        name.find_element_by_tag_name('a').find_element_by_xpath(
                            './/span/div[1]/span[2]').text.replace(
                            '(',
                            '').replace(
                            ')', ''))
                    time.sleep(1.5)
                except Exception as e:
                    create_error_log(e)
                    NumberOfReviews.append('NumberOfReviews not found')
                try:
                    web = name.find_elements_by_xpath(".//a[contains(@class,'yYlJEf L48Cpd')]")[0].get_attribute(
                        "href").split("/")
                    Website.append(web[2])
                    # print(web[2])
                    time.sleep(1.5)
                except Exception as e:
                    create_error_log(e)
                    Website.append('Website not found')
                try:
                    name.click()  # To click on single result and get full address
                    time.sleep(
                        3)  # if we wont use sleep,we will no get HTML of popup , so that we wont get full address
                    span_add = driver.find_element_by_class_name('LrzXr')
                    Address.append(span_add.text)
                    # print(span_add.text)
                    time.sleep(1.5)
                except Exception as e:
                    create_error_log(e)
                    Address.append('Address not found')
                try:
                    mobile_no = driver.find_element_by_xpath(
                        './/div[@class="wDYxhc"]/div/div/span[2]/span/a/span').text
                    MobileNo.append(mobile_no)
                    create_error_log(mobile_no)
                    time.sleep(1.5)
                except Exception as e:
                    create_error_log(e)
                    MobileNo.append('Number not found')
                try:
                    name.click()  # to click on single result and get full address
                    time.sleep(
                        1)  # if we wont use sleep,we will no get HTML of popup , so that we wont get full address1
                    x = driver.find_element_by_class_name('YhemCb')
                    Description.append(x.text)
                    # print(x.text)
                    time.sleep(1.5)
                except Exception as e:
                    create_error_log(e)
                    Description.append('Description not found')

        extract_data(names)  # Extracting all the details
        
        # total_pages = driver.find_elements_by_xpath('//*[@id="rl_ist0"]/div[2]/div/table/tbody/tr')[
        #     0].find_elements_by_tag_name(
        #     'a')  # Since we get only limited result in first page, we have to move to the next page using anchor
        # tag
        total_pages = driver.find_elements_by_xpath('//*[@id="rl_ist0"]/div/div[2]/div/table/tbody/tr')[
            0].find_elements_by_tag_name(
            'a')

        for page in total_pages:  # To restrict same link multiple times
            if page.get_attribute('href') in Pages:
                print('double')
            else:
                Pages.append(page.get_attribute('href'))

        for singlePage in Pages:
            driver.get(singlePage)
            names = driver.find_elements_by_class_name('VkpGBb')
            extract_data(names)

        df = pd.DataFrame(
            {'Name': Title, 'Address': Address, 'Rating': Rating, 'Total Reviews': NumberOfReviews,
             'Mobile-Number': MobileNo,
             'Website': Website, 'Description': Description
             })  # Initialize every field with the resultant array
        # y = input("Xls  Name :")  # Input excel name
        file_path = os.path.join(os.getcwd(), "output",
                                 keyword + '{}.xlsx'.format(datetime.now().strftime('%d%m%y-%H%M%S')))
        df.to_excel(file_path, index = False)
        # file_path = output[i] + '.csv'
        # # df.to_csv(output[i] + '.csv', index = False, encoding = 'utf-8-sig')  # Create a CSV file
        create_error_log("Saved successfully")

        try:
            upload_to_dropbox(file_path)
            create_error_log("uploaded")

        except Exception as e:
            create_error_log("exception" + str(e))
    else:
        return "Login failed"


# Linkedin Profile scraper

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


# Linkedin Profile Scraping
# app = FastAPI()


def allowed_file_element(filename):
    allowed_ext = constants.ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


# main function that'll process the execution

@app.post('/gf/scraper/linkedin/contact', tags = ['Linkedin Scraper'])
def linkedin_scraper(code: str = Form(...), fileb: UploadFile = File(...)):
    """
            This API takes list of keywords as input in a csv file .
            It scrapes the linkedin contact details and the data obtained is saved in the company dropbox account.
            The following data is obtained for each details:
            - **Name**
            - **Designation**
            - **Company**
            - **Search Url**
            - **Confidence Score**
        """
    if code in code_value:
        try:
            name_contact = fileb.filename
            create_error_log(name_contact)
            data_frame = read_excel_linked(name_contact)
            create_error_log(data_frame)
            # create_error_log("parsing results, this is df" + data_frame)
            results = parse_results(driver, data_frame)
            print("value")
            # print(results)
            # create_error_log(results)
            if not results:
                create_error_log("status is false")
                return False
            else:
                print("writing into excel")
                create_error_log("writing into excel")
                output_file_path = createFileWithDetaillList(results, name_contact)
                create_error_log(output_file_path)
                create_error_log("uploading to dropbox")
                status = upload_to_dropbox(output_file_path)
                if status:
                    return True
                else:
                    return False
        except Exception as e:
            # create_error_log(e)
            create_error_log(e)
            return False
    else:
        return "Login Failed"


# Contact Scraping


def allowed_file(filename):
    allowed_ext = constants.ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


@app.post('/gf/scraper/contact', tags = ['Contact Scraper'])
def upload_file(code: str = Form(...), fileb: UploadFile = File(...)):
    """
           This API takes list of keywords as input in a csv file .
           It scrapes the google contact details and the data obtained is saved in the company dropbox account.
           The following data is obtained for each details:
           - **site_url**
           - **email**
           - **number**
           - **social_accounts**
       """
    name = fileb.filename
    if code in code_value:

        contents = fileb.file.read()
        # return contents
        byte_to_string = codecs.decode(contents, "utf-8")  # convert byte to string
        # return byte_to_string
        regex = re.compile(r'[\r\t]')
        string = regex.sub(" ", byte_to_string)
        # remove_first_line = string[9:]
        output = string.split(" \n")
        del output[0]
        # return output
        for i in range(len(output) - 1):
            # args = arg_parser.parse_args()
            url = output[i]
            url_len = len(str(url).split(","))
            time_out = url_len * 16
            params = {'url': url, 'timeout': time_out}
            global baseData
            baseData = params
            try:
                scrape_with_crochet_(base_data = baseData)  # Passing that Data to our Scraping Function
                async_timeout = int(baseData['timeout']) + 2
                create_error_log("total timeout" + str(async_timeout))
                time.sleep(async_timeout)  # Pause the function while the scrapy spider is running
                create_error_log("AWAKE NOW")
                # print(output_data)

            except Exception as e:
                create_error_log_message(e)
        # print(output_data)
        file_path = write_to_excel_scraper(output_data, name)
        output_data.clear()  # clear output list to avoid data of prev runs
        create_error_log(file_path)
        upload_to_dropbox_scrapy(file_path)
        create_error_log("success")

    else:
        return "Login Failed"


@crochet.run_in_reactor
def scrape_with_crochet_(base_data):
    try:

        # This will connect to the dispatcher that will kind of loop the code between these two functions.
        dispatcher.connect(_crawler_result_, signal = signals.item_scraped)
        create_error_log("done")
        # This will connect to the DatabloggerSpider function in our scrapy file and after each yield will pass to
        # the crawler_result function.
        eventual = crawl_runner.crawl(DatabloggerSpiderScraper, category = base_data)
        return eventual
    except Exception as e:
        create_error_log("from scrape with crochet" + str(e))


# This will append the scraped data to the output data list.
def _crawler_result_(item, response, spider):
    if dict(item) not in output_data:
        # print("sucess")
        output_data.append(dict(item))
        # print(output_data)


# wordcount

# from fastapi import FastAPI, Form, Request
#
# app = FastAPI()
global baseData, timeout


@app.post("/gf/scraper/word/count", tags = ['Word Count '])
def word_count(code: str = Form(...), url: UploadFile = File(...), words: str = Form(...), allowed_domains: UploadFile = File(...),
               depth: str = Form(...),
               exclude_urls: str= Form(...)):
    """
            This API takes list of inputs like :
            - **url :** as a value for "url" key.
            Note - url accepts only 1 url at a time.

            - **allowed_domains :** input the domains that will be allowed for a
            compliant url, this feature will minimize the chances of third party
            redirection.In case of multiple domains separate the domains with a
            coma(,).

            - **words :** put in the words that are required to be searched in the
            website.In case of multiple words separate the words with coms (,).

            -  **depth :**  this is the level of scraping to extract the
            url's from a site.In case of no value depth will be considered as level 1.

            - **exclude_urls :** this is a list of endpoints for which the url needs to
            be ignored while fetching the url's.

            - **when a 201 code is returned it indicates that scraping is completed
            successfully and in order to view the results give a GET request to
            the same endpoint.**

            - **when a 500 code is returned it indicates an unknown error has come
            up, reach out to the service provider to resolve the issue.**

            - **when a 400 code is returned it indicates a json syntax error which is usually from the user end
            and generally it is the error in the way urls or words are supplied, re check
            the fields, if they're separated with a coma(,) in case of multiple inputs or not. If the error is
            still there, reach out to the service provider.**

    """
    name = url.filename
    contents = url.file.read()
    byte_to_string = codecs.decode(contents)
    regex = re.compile(r'[\r\t]')
    string = regex.sub(" ", byte_to_string)
    output = string.split(" \n")
    del output[0]
    output.pop()
    url = ','.join(output)
    contents_allowed = allowed_domains.file.read()
    byte_to_string_allowed = codecs.decode(contents_allowed)
    regex = re.compile(r'[\r\t]')
    string_allowed = regex.sub(" ", byte_to_string_allowed)
    output_allowed = string_allowed.split(" \n")
    del output_allowed[0]
    output_allowed.pop()
    allowed_domains = ','.join(output_allowed)
    global time_out
    if code in code_value:
        try:
            # checking depth
            if depth == "":
                depth = 1

            if int(depth) < 2:
                time_out = int(depth) * 15
            elif int(depth) == 2:
                time_out = 57

            create_error_log("this is timeout" + str(time_out))
            params = {'url': url, 'allowed_domains': allowed_domains, 'words': words, 'timeout': time_out,
                      "depth": depth,
                      "exclude": exclude_urls
                      }
            create_error_log("got these params" + str(params))

            # check if all mandatory parameters are given or not
            if url == "" or words == "":
                return JSONResponse((JsonSyntaxError().to_json()))

            base_data = params

            try:
                scrape_with_crochet(base_data = base_data)  # Passing that Data to our Scraping Function
                async_timeout = int(base_data['timeout']) + 2
                create_error_log("will wait for scraper for" + str(async_timeout))
                time.sleep(async_timeout)  # Pause the further execution while the scrapy spider is running
                create_error_log("AWAKE NOW")
                create_error_log(output_data)
                file_path = write_to_excel(output_data,url,words,name)
                create_error_log(file_path)
                output_data.clear()  # clear output list to avoid data of prev runs
                status = upload_to_dropbox_word(file_path)
                create_error_log("sucess")
                # check status to verify that file is successfully uploaded to dropbox
                if status:
                    return JSONResponse((SuccessResponse().to_json()))  # Returns the status after uploading
                else:
                    return JSONResponse((InternalServerError().to_json()))

            except Exception as e:
                create_error_log(e)
                return JSONResponse((InternalServerError().to_json()))

        except Exception as e:
            # print(e)
            create_error_log(e)
            return JSONResponse((InternalServerError().to_json()))
    else:
        return "Login Failed"


@crochet.run_in_reactor
def scrape_with_crochet(base_data):
    try:
        # This will connect to the dispatcher that will kind of loop the code between these two functions.
        dispatcher.connect(_crawler_result, signal = signals.item_scraped)
        _crawler_result
        # This will connect to the DatabloggerSpider function in our scrapy file and after each yield will pass to
        # the crawler_result function.
        eventual = crawl_runner.crawl(DatabloggerSpider, category = base_data)
        print(eventual)
        print("yes")
        return eventual
    except Exception as e:
        create_error_log("from scrape with crochet" + str(e))


# This will append the scraped data to the output data list.
def _crawler_result(item, response, spider):
    print(output_data)
    if dict(item) not in output_data:
        output_data.append(dict(item))