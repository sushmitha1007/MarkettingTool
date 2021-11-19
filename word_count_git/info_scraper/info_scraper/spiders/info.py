# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
import re
from w3lib.html import remove_tags, remove_tags_with_content
import os
from word_count_git.utils.logger import create_error_log


class DatabloggerSpider(CrawlSpider):

    def __init__(self, category='', **kwargs):  # The category variable will have the input data.
        print("this is category dict", category)
        self.url = category['url'].split(",")
        self.allowed_domains = str(category['allowed_domains']).split(",")
        self.words_to_find = str(category['words']).split(",")
        self.depth = int(category['depth'])
        self.exclude_urls = category['exclude'].split(",")
        super().__init__(**kwargs)

    # The name of the spider
    name = "datascraper"
    depth = ''
    exclude_urls = ''
    start_urls = []
    words_to_find = []

    # Method which starts the requests by visiting all URLs specified in start_urls
    def start_requests(self):
        try:
            for website in self.url:
                yield scrapy.Request(website, callback = self.get_links, dont_filter = True)
        except Exception as e:
            create_error_log(e)
            # print("exception from start req", e)

    # function to generate links from a seed url
    def get_links(self, response):
        try:
            # depth = 0
            # print("checking depth")
            if self.depth == 0:
                yield scrapy.Request(response.url, callback = self.get_data, dont_filter = True)

            # depth > 0
            elif self.depth == 1:
                links = LinkExtractor(canonicalize = True, unique = True).extract_links(response)
                # check if generated links are compliant or not
                for link in links:
                    is_allowed_domain = False
                    is_allowed_link = False
                    # print("success")
                    # if excluded url's are present
                    if len(self.exclude_urls) > 0:
                        # print("in if part of exclude urls")
                        for exclude in self.exclude_urls:
                            # print("checking for this", exclude)
                            if not str(exclude).lower() in str(link.url).lower():
                                # print("setting allowed link to True")
                                is_allowed_link = True
                    else:
                        is_allowed_link = True

                    # if allowed domains are present
                    if len(self.allowed_domains) > 0:
                        for domain in self.allowed_domains:
                            if domain in link.url:
                                is_allowed_domain = True
                    else:
                        is_allowed_domain = True

                    # if link has allowed domain and is without excluded urls
                    if is_allowed_link and is_allowed_domain:
                        # print(" verified link", link.url)
                        yield scrapy.Request(link.url, callback = self.get_data, dont_filter = True)
                create_error_log("sucesss")

            elif self.depth == 2:
                # generate the links for depth=1
                links = LinkExtractor(canonicalize = True, unique = True).extract_links(response)

                # check if links are compliant or not
                for link in links:
                    is_allowed_domain = False
                    is_allowed_link = False

                    # if excluded url's are present
                    if len(self.exclude_urls) > 0:
                        for exclude in self.exclude_urls:
                            if not str(exclude).lower() in str(link.url).lower():
                                is_allowed_link = True
                    else:
                        is_allowed_link = True

                    # if allowed domains are present
                    if len(self.allowed_domains) > 0:
                        for domain in self.allowed_domains:
                            if domain in link.url:
                                is_allowed_domain = True

                    else:
                        is_allowed_domain = True

                    # if link has allowed domain and is without excluded urls
                    if is_allowed_link and is_allowed_domain:
                        # print(" verified link", link.url)
                        yield scrapy.Request(link.url, callback = self.get_child_links, dont_filter = True)

        except Exception as e:
            create_error_log(e)
            # print("get links exception", e)

    # get child links for links generated at depth = 1, and extract data for them
    def get_child_links(self, response):
        # get links for depth = 2
        links = LinkExtractor(canonicalize = True, unique = True).extract_links(response)

        # check if generated links are compliant
        for link in links:
            is_allowed_domain = False
            is_allowed_link = False

            # if excluded url's are present
            if len(self.exclude_urls) > 0:
                for exclude in self.exclude_urls:
                    if not str(exclude).lower() in str(link.url).lower():
                        is_allowed_link = True
            else:
                is_allowed_link = True

            # if allowed domains are present
            if len(self.allowed_domains) > 0:
                for domain in self.allowed_domains:
                    if domain in link.url:
                        is_allowed_domain = True
            else:
                is_allowed_domain = True

            # if link has allowed domain and is without excluded urls
            if is_allowed_link and is_allowed_domain:
                # print(" verified link", link.url, is_allowed_link, is_allowed_domain)
                yield scrapy.Request(link.url, callback = self.get_data, dont_filter = True)

    # get data for the url response passed
    def get_data(self, response):
        try:
            # print("in get data for ")
            response_text = response.text
            keywords_dict = {}
            for word in self.words_to_find:
                count = str(remove_tags(remove_tags_with_content(response_text, ('script', 'style',)))).count(word)
                keywords_dict[word] = count
            my_dic = {"url": response.url, "keywords": keywords_dict}
            yield my_dic
            # print("done")
        except Exception as e:
            create_error_log(e)
            # print("get data exception", e)
