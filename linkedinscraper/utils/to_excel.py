import pandas as pd
import os
from datetime import datetime
from linkedinscraper.utils.logger import create_error_log
from linkedinscraper.config.constants import OUTPUT_FOLDERNAME
from linkedinscraper.config.config import KEYWORDS as keyword_list
import xlsxwriter
from linkedinscraper.core.LinkedInGoogleSearcher_Gen import containsInclusionWord
from linkedinscraper.utils.linkedin_scraper import scrapelinkedin


def createFileWithDetaillList(results, name):
    print("in")
    try:
        # not being used currently
        #     def parse_linkedin():
        #         try:
        #             status = False
        #             df = scrapelinkedin(result['link'])
        #             for val in df.values.tolist():
        #                 if len(val) > 1 and (None not in val):
        #                     if val[1] != "" or str(val[1]) != "None":
        #                         if result['Company'] in (val[1].lower()):
        #                             # print("company found in linkedin scraped data")
        #                             status = True
        #                             break
        #             return status
        #         except Exception as e:
        #             create_error_log("error when parsing linkedin: " + str(e))

        def check_name():
            try:
                # changing given input name to linkedin equivalent
                if str(result['Name']) != "nan":
                    name = result['Name'].replace(" ", "-")
                    print("checking for {} in {}".format(name.lower(), result['link']))
                    if name.lower() in result['link']:
                        return True
                    else:
                        return False
                else:
                    print("name is nan")
                    return False
            except Exception as e:
                create_error_log("error when checking name: " + str(e))

        def get_score():
            try:
                if title and description and name_flag:
                    score = 10
                elif name_flag and description:
                    score = 9
                elif name_flag:
                    score = 7
                else:
                    score = 5
                return score
            except Exception as e:
                create_error_log("error when calculating score: " + str(e))

        def check_attributes():
            try:
                title = False
                description = False
                # print("checking for {} in {}".format(company.lower(),result['title']))
                if (company.lower()).strip() in result['title'].lower():
                    # print("company:"+company+"and title is :"+result['title'])
                    # print("title matched")
                    title = True

                # print("checking for {} in {}".format(company.lower(),result['description'].lower()))
                if (company.lower()).strip() in result['description'].lower():
                    # print("company:"+company+"and desc is :"+result['description'])
                    # print("desc matched")
                    description = True

                return title, description
            except Exception as e:
                create_error_log("error when checking attributes: " + str(e))

        filepath = os.path.join(os.getcwd(), OUTPUT_FOLDERNAME,
                                name + 'linkedin_scraper_output_{}.xlsx'.format(
                                    datetime.now().strftime('%d%m%y-%H%M%S')))
        print(filepath)
        workbook = xlsxwriter.Workbook(filepath)
        print(workbook)
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0

        worksheet.write(0, 0, 'Name')
        worksheet.write(0, 1, 'Designation')
        worksheet.write(0, 2, 'Company')
        worksheet.write(0, 3, 'SearchURL')
        worksheet.write(0, 4, 'Confidence Score')
        row += 1
        print("********************************")
        # print(results)
        for result in results:
            company = result['Company']
            print("company:" + company + " and title is :" + result['title'])
            if any(keyword in result['title'] for keyword in keyword_list) or any(
                    keyword in result['description'] for keyword in keyword_list):
                title, description = check_attributes()
                name_flag = check_name()

                score = get_score()

                # print("getting linked in results")
                # linkedin_status = parse_linkedin()
                # if linkedin_status!= True:
                # 	score = 5

                print("value of title,description, name, linkedin_status", title, description, name_flag)
                if (title or description or name_flag):
                    print("Row number:{}".format(row))
                    worksheet.write(row, col, str(result['Name']))
                    worksheet.write(row, col + 1, result['Designation'])
                    worksheet.write(row, col + 2, result['Company'])
                    worksheet.write(row, col + 3, result['link'])
                    worksheet.write(row, col + 4, score)
                    row += 1

            else:
                score = 3
                print("Row number:{}".format(row))
                worksheet.write(row, col, str(result['Name']))
                worksheet.write(row, col + 1, result['Designation'])
                worksheet.write(row, col + 2, result['Company'])
                worksheet.write(row, col + 3, result['link'])
                worksheet.write(row, col + 4, score)
                row += 1

        workbook.close()
        return filepath
    except:
        pass


def read_excel_linked(filepath):
    global data
    try:
        print('in')
        print(filepath)
        if filepath.endswith("xlsx") or filepath.endswith("xls"):
            data = pd.read_excel(filepath, skiprows=0, engine="openpyxl", sep=";", encoding='cp1252')
        elif filepath.endswith("csv"):
            data = pd.read_csv(filepath)
            # print(data)
        # filter empty rows from dataframe
        # print(filepath)
        return data.dropna(axis=0, how='all', thresh=None, subset=None, inplace=False)
    except Exception as e:
        print(e)
        # create_error_log(e)

# s = read_excel('linkedin.csv')
# print(s)
