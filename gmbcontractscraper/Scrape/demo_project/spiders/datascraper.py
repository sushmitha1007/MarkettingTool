# -*- coding: utf-8 -*-
import phonenumbers
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
import re
from w3lib.html import remove_tags, remove_tags_with_content
import os
from gmbcontractscraper.utils.logger import create_error_log_message
from gmbcontractscraper.utils.htmlutil import is_home_page, get_home_page


class DatabloggerSpiderScraper(CrawlSpider):

    def __init__(self, category='', **kwargs):  # The category variable will have the input URL.
        # print("this is category dict", category)
        self.myUrl = category['url']
        self.urls = self.myUrl.split(",")
        super().__init__(**kwargs)

    # The name of the spider
    name = "datascraper"

    myUrl = ''

    # default scrapy method which starts the requests by visiting all URLs specified in start_urls
    def start_requests(self):
        try:
            # global homepage_url
            for url in self.urls:

                if is_home_page(url):
                    homepage_url = url
                    create_error_log_message("already a homepage url" + str(homepage_url))
                    yield scrapy.Request(homepage_url, callback = self.get_links, dont_filter = True)
                else:
                    homepage_url = get_home_page(url)
                    # append homepage url to urls list
                    self.urls.append(homepage_url)
                    # remove specific site page url that was given as an input from urls list
                    self.urls.remove(url)
                    create_error_log_message("this is homepage url" + str(homepage_url))
                    yield scrapy.Request(homepage_url, callback = self.get_links, dont_filter = True)
        except Exception as e:
            # print("exception from start req", e)
            create_error_log_message("exception from start req" + str(e))

    def get_links(self, response):
        try:
            create_error_log_message("in get links for" + str(response.url))
            # yield response for seedurl as well if not generated in link extractor
            yield scrapy.Request(response.url, callback = self.get_data, dont_filter = True)

            # extract links from seed url
            links = LinkExtractor(canonicalize = True, unique = True).extract_links(response)
            for link in links:
                # print("generated links", link.url)
                yield scrapy.Request(link.url, callback = self.get_data, dont_filter = True)
        except Exception as e:
            # print("get links exception", e)
            create_error_log_message("get links exception" + str(e))

    def get_data(self, response):
        try:
            url_list = ",".join(self.urls)
            url_list = url_list.replace("www.", "").replace("https://", "").replace("http://", "")
            # url_list = url_list.replace("https://", "")
            # url_list = url_list.replace("http://", "")
            link = get_home_page(response.url)

            # if not str(link).endswith("/"):
            #     link = str(link) + "/"
            # if "www." in str(link):
            #     link = str(link).replace("www.","")

            # check if allowed site
            # print("checking for {} in {}".format(link, url_list))
            link = str(link).replace("https://", "").replace("http://", "")
            if str(link).replace("www.", "") in url_list:
                # check if required page is there
                if "contact" in str(response.url).lower() or "location" in str(response.url).lower() or (
                        response.url in self.urls) or ("index.html" in str(response.url).lower()):

                    # print("in get data for", response.url)
                    response_text = response.text
                    # link = get_home_page(response.url)

                    email_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z-]+\.[a-zA-Z-.]+)"

                    # usa numbers
                    contact_regex_usa = r'[\+\(]?[1-9][0-9 .\-\(\)]{10,}[0-9]'
                    # regex to look for tel; in href of the page
                    contact_regex = r'(?:href=\")(?:tel:|phone:)([+]?[0-9\-\s]*)'
                    # regex to match continous 10 digit number with or without +91 at beginning
                    contact_regex_first_alternate = r'(?:91)?[\-\s]?([789][\d]{9})'
                    # regex to match 10 digit number with space or - after 5 digits with or without +91 at beginning
                    contact_regex_second_alternate = r'(?:91)?[\-\s]?([789][\d]{4}[\s\-][\d]{5})'

                    linked_regex = r'(?<!\w)(?:http(?:s)?://)?((?:[a-z]+\.)?linkedin.com/)([a-z0â€“9\-_%/]{2,60})([\w|=|%|&|;|-]*)'
                    twitter_regex = r'(?<!\w)(http(?:s)?:\/\/)?(?:www.)?(twitter.com)(/)(?!(?:oauth|account|tos|privacy|signup|home|hashtag|search|login|widgets|i|settings|start|share|intent|oct)(?:[\'\"\?\.\/]|$))([A-Za-z0-9_]{1,15})(?![A-Za-z0-9_])(?:/)?'
                    facebook_regex = r'(?<!\\w)(?:http(?:s)?:\\/\\/)?(www.)?(facebook.com|fb.com)(/|/pages/)(?!(rsrc\.php|apps|groups|events|l\.php|friends|images|photo.php|chat|ajax|dyi|common|policies|login|recover|reg|help|security|messages|marketplace|pages|live|bookmarks|games|fundraisers|saved|gaming|salesgroups|jobs|people|ads|ad_campaign|weather|offers|recommendations|crisisresponse|onthisday|developers|settings|connect|business|plugins|intern|sharer)([\'\"\?\.\/]|$))(profile\.php\?id\=[0-9]{3,20}|(?!profile\.php)[A-Za-z0-9\.\-\/]{2,100})'

                    # get emails and filter junk
                    personal_email = []
                    company_email = []
                    emails = re.findall(email_regex, str(response_text).strip())
                    emails = list(dict.fromkeys(emails))  # remove duplicates
                    emails_to_del = []
                    for mail in emails:
                        if str(mail).endswith("png") or str(mail).endswith("svg") or str(mail).endswith("jpg"):
                            emails_to_del.append(mail)

                    for mail in emails_to_del:
                        emails.remove(mail)
                    for i in emails:

                        if str(i).lower().endswith("wix.com") or str(i).lower().endswith("gmail.com") or str(
                                i).lower().endswith("yahoo.com") or str(i).lower().endswith("rediff.com") or str(
                                i).lower().endswith("hotmail.com") or str(i).lower().endswith("google.com") or str(
                                i).lower().endswith("email.com") or str(i).lower().endswith("wixpress.com") or str(
                                i).lower().endswith("address.com") or str(i).lower().endswith("yourwebsite.com"):
                            personal_email.append(i)
                        else:

                            company_email.append(i)
                    contact_no = [phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164) for
                                  match in phonenumbers.PhoneNumberMatcher(str(response_text).strip(), "US")]
                    contact_no = list(dict.fromkeys(contact_no))  # remove duplicates
                    valid_number = []
                    for i in contact_no:
                        # print(i)
                        parsing = phonenumbers.parse(i)
                        validnumber = phonenumbers.is_valid_number(parsing)
                        if validnumber:
                            valid_number.append(i)
                        else:
                            valid_number.remove(i)

                    # get contact number and filter junk
                    # contact_no = re.findall(contact_regex, str(response_text).strip())
                    # contact_no.extend(re.findall(contact_regex_usa, str(
                    #     remove_tags(remove_tags_with_content(response_text, ('script', 'style',)))).strip()))
                    # contact_no.extend(re.findall(contact_regex_first_alternate, str(
                    #     remove_tags(remove_tags_with_content(response_text, ('script', 'style',)))).strip()))
                    # contact_no.extend(re.findall(contact_regex_second_alternate, str(
                    #     remove_tags(remove_tags_with_content(response_text, ('script', 'style',)))).strip()))
                    # contact_no = list(dict.fromkeys(contact_no))  # remove duplicates

                    # get social links and filter junk
                    linkedin_url = re.findall(linked_regex, str(response_text).strip())
                    twitter_url = re.findall(twitter_regex, str(response_text).strip())
                    facebook_url = re.findall(facebook_regex, str(response_text).strip())

                    linkedin_url_to_del = []
                    for tup in linkedin_url:
                        if "www.linkedin" not in ''.join(tup):
                            linkedin_url_to_del.append(tup)

                    for tup in linkedin_url_to_del:
                        linkedin_url.remove(tup)

                    # convert the resultant sliced list of tuples(regex groups) into a single url
                    sites = []
                    sites.extend([''.join(tups) for tups in linkedin_url])
                    sites.extend([''.join(tups) for tups in twitter_url])
                    sites.extend([''.join(tups) for tups in facebook_url])
                    sites = list(dict.fromkeys(sites))  # remove duplicates

                    # print("found these social sites and numbers", sites, valid_number)
                    # if len(emails)>0 or len(contact_no)>0 or len(sites)>0:
                    info_dic = {"site_url": link, "email": ",".join(emails), "number": ",".join(valid_number),
                                "social_accounts": ",".join(sites), "personal_email": ",".join(personal_email),
                                "company_email": ",".join(company_email)
                                }
                    yield info_dic

                else:
                    if link in self.urls:
                        info_dic = {"site_url": link, "email": "error in scraping", "number": "error in scraping",
                                    "social_accounts": "error in scraping", "personal_email": "error in scraping",
                                    "company_email": "error in scraping "
                                    }
                        yield info_dic
        except Exception as e:
            # print("get data exception", e)
            create_error_log_message("get data exception" + str(e))
