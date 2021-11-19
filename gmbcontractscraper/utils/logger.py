import os
from datetime import datetime
from gmbcontractscraper.config.constants import LOG_FILENAME, LOG_FOLDERNAME


def create_error_log_message(message):
    current_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_list = [current_datetime, " " + str(message), "\n"]
    with open((os.path.join(os.getcwd(), LOG_FOLDERNAME, LOG_FILENAME)), "a+") as f:
        for data_to_write in log_list:
            f.write(data_to_write)
