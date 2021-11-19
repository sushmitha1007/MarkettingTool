import dropbox
import os
from gmbcontractscraper.utils.logger import create_error_log_message
from gmbcontractscraper.config.constants import DROPBOX_DESTINATION_FOLDERNAME, ACCESS_TOKEN


class TransferData:
    def __init__(self):
        self.access_token = ACCESS_TOKEN

    def upload_file(self, file_from, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)


def upload_to_dropbox_scrapy(filepath):
    try:
        transferData = TransferData()

        file_from = filepath
        base_name = os.path.basename(file_from)
        file_to = '/{}/{}'.format(DROPBOX_DESTINATION_FOLDERNAME,
                                  base_name)  # The full path to upload the file to, including the file name
        create_error_log_message("writing into" + str(file_to))
        # API v2
        transferData.upload_file(file_from, file_to)
        return True
    except Exception as e:
        create_error_log_message(e)
        return False
