import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from linkedinscraper.config.config import LINKEDIN_USERNAME, LINKEDIN_PASSWORD

email = ""
password = ""
HOMEPAGE_URL = 'https://www.linkedin.com'
LOGIN_URL = 'https://www.linkedin.com/uas/login-submit'
pd.set_option('display.max_colwidth', None)

def get_industry_type(only_included_list, about_include):
    industryType = ""
    for d in only_included_list:
        for items in d:
            try:
                type = items["localizedName"] if (items['entityUrn'] == about_include["*companyIndustries"][0]) else ""
                if (type != ""): industryType = type
            except KeyError:
                pass
    return industryType


def get_dataframe_with_filtered_values(dict_value_list):
    final_df = pd.DataFrame(columns={'about_key', 'about_value'})

    new_list = ['staffCount', 'staffCountRange', 'name', 'specialities', 'headquarter', 'foundedOn', 'description',
                'companyType',
                'companyPageUrl', 'backgroundCoverImage', 'confirmedLocations']
    for dict_value in dict_value_list:
        dfObj = pd.DataFrame(list(dict_value.items()))
        dfObj.columns = dfObj.columns.astype(str)
        dfObj.rename(columns={'0': 'about_key', '1': 'about_value'}, inplace=True)
        drop_indices = []
        for index in dfObj.index:
            if dfObj.iloc[index]['about_key'] not in new_list:
                drop_indices.append(index)
        dfObj.drop(drop_indices, inplace=True)
        if (not dfObj.empty):
            final_df = final_df.append(dfObj)
    return final_df


def scrapelinkedin(lnurl):
    client = requests.Session()
    html = client.get(HOMEPAGE_URL).content
    soup = BeautifulSoup(html, "html.parser")
    csrf = soup.find('input', {'name': 'loginCsrfParam'}).get('value')

    login_information = {
        'session_key': LINKEDIN_USERNAME,
        'session_password': LINKEDIN_PASSWORD,
        'loginCsrfParam': csrf,
        'trk': 'guest_homepage-basic_sign-in-submit'
    }

    client.post(LOGIN_URL, data=login_information)
    response = client.get(lnurl)
    content = response.text.encode('UTF-8')
    soup = BeautifulSoup(content, "html.parser")

    [x.extract() for x in soup.find_all('script')]
    [x.extract() for x in soup.find_all('style')]
    [x.extract() for x in soup.find_all('meta')]
    [x.extract() for x in soup.find_all('noscript')]
    [x.extract() for x in soup.find_all(text=lambda text: isinstance(text, Comment))]

    count = 0
    only_included_list = []
    codes = soup.find_all("code")


    max_len = 0
    about_include = []

    for code in codes:
        try:
            json_object = json.loads(code.text)
            if (json_object['included'] != []):
                for included in json_object['included']:
                    if (len(included) > max_len):
                        about_include = included
                        max_len = len(included)
                only_included_list.append(json_object['included'])
        except KeyError:
            pass
        except ValueError:
            pass
            count = count + 1

    output_df = pd.DataFrame(columns=['about_key', 'about_value'])
    for included_list in only_included_list:
        df_r = get_dataframe_with_filtered_values(included_list)
        output_df = output_df.append(df_r, ignore_index=True)
    data_df = output_df.query('about_key == "staffCount"')
    industryType = get_industry_type(only_included_list, about_include)

    for row in data_df.index:
        start_value = row
        end_value = start_value + 8
        output_df = output_df.loc[start_value:end_value, :]
        output_df = output_df.reset_index(drop=True)

    output_df = output_df.append({'about_key': 'industry_type', 'about_value': industryType}, ignore_index=True)
    return output_df


# def main():
#     df = scrapelinkedin('https://www.linkedin.com/in/lutz-tabeling-4710098b/?originalSubdomain=de')
#     print(df.values.tolist())
#     for val in df.values.tolist():
#         if len(val)>1 and (None not in val):
#             print("checking in", val)
#             if val[1]!="" or str(val[1])!= "None":
#                 print(str(val[1]))
#                 if "thyssenkrupp" in (val[1].lower()):
#                     print("company found")
#                     break


# if __name__ == '__main__':
#     main()
