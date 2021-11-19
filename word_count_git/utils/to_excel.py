import pandas as pd
import os
from word_count_git.utils.logger import create_error_log
from datetime import datetime
from word_count_git.config.constants import OUTPUT_FOLDERNAME


def write_to_excel(output_data,url,words,name):
    try:
        # convert resultant output list to dataframe and write to excel
        create_error_log(url)
        list_str = list(url.split(",")) 
        words_list = list(words.split(","))  
        count={}          
        word_count=0
        url_word_count = []
        
        filepath = os.path.join(os.getcwd(),OUTPUT_FOLDERNAME,
                                   name +"-"+' wordcount_scraper_output_{}.xlsx'.format(datetime.now().strftime('%d%m%y-%H%M%S')))
        for url in list_str:
            for word in words_list:
                for output in output_data:
                    if output['url'].startswith(url):
                        word_count += output['keywords'][word]
                        print(word_count)
                count[word]=word_count
                word_count = 0
            url_word_count.append({"url":url,"keywords":count})  
            count = {}    
        print(url_word_count)        
        df = pd.DataFrame(url_word_count)   
        df.to_excel(filepath, index = False)
        return filepath    
    except Exception as e:
        create_error_log(e)
