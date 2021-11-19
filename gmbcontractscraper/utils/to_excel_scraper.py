import pandas as pd
import os
from datetime import datetime
from gmbcontractscraper.utils.logger import create_error_log_message
from gmbcontractscraper.config.constants import OUTPUT_FOLDERNAME


def write_to_excel_scraper(output_list, name):
    try:
        master = []
        # loop through list of dicts and group together dicts with same url
        for loc, dic in enumerate(output_list):
            child_pair = []
            # match current dict with other proceeding dicts
            for child_dic in output_list[(loc + 1):]:
                # print("matching this", dic,child_dic)
                if dic['site_url'] == child_dic['site_url']:
                    # if dict is already present, dont append(minimize duplicates)
                    if dic not in child_pair:
                        child_pair.append(dic)
                    if child_dic not in child_pair:
                        child_pair.append(child_dic)
                    # print("removing", child_dic)
                    # remove the matched proceeding dicts
                    output_list.remove(child_dic)

            master.append(child_pair)

        # print("master list after grouping dicts", master)
        final = []
        compare_with = []
        # merge the dicts with same site_url
        for lists in master:
            d = {}
            if lists != []:
                compare_with.extend(lists)
                for k in lists[0].keys():
                    d[k] = list(d[k] for d in lists)
                final.append(d)

        # check for missing dicts if any
        for dic in output_list:
            if dic not in compare_with:
                final.append(dic)

        # remove duplicates and brackets
        for dics in final:
            for key, val in dics.items():
                if isinstance(val, list) and ('error in scraping' in val):
                    val = list(dict.fromkeys(val))
                    if val.count('error in scraping') < len(val):
                        val.remove('error in scraping')
                        val = ",".join(val)
                        val = val.split(',')
                        val = list(dict.fromkeys(val))
                    dics[key] = ",".join(val)
                elif isinstance(val, list):
                    val = ",".join(val)
                    val = val.split(',')
                    val = list(dict.fromkeys(val))
                    dics[key] = ",".join(val)

        # convert resultant output list to dataframe and write to excel
        df = pd.DataFrame(final)
        filepath = os.path.join(os.getcwd(), OUTPUT_FOLDERNAME,
                                name+'_contact_scraper_output_{}.xlsx'.format(datetime.now().strftime('%d%m%y-%H%M%S')))
        df.to_excel(filepath, index = False)
        return filepath
    except Exception as e:
        create_error_log_message(e)


# write_to_excel_scraper()


def read_excel(filepath):
    try:
        urls = []
        if filepath.endswith("xlsx") or filepath.endswith("xls"):
            data = pd.read_excel(filepath, sheet_name = "urls", engine = 'openpyxl').values.tolist()
        elif filepath.endswith("csv"):
            data = pd.read_csv(filepath).values.tolist()
        for lists in data:
            urls.extend(lists)
        all_urls_string = ",".join(urls)
        all_urls_string = all_urls_string.replace("http", "https")
        return all_urls_string
    except Exception as e:
        create_error_log_message(e)
