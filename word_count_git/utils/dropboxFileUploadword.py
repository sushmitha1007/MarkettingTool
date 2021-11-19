import dropbox
import os
from word_count_git.utils.logger import create_error_log
from word_count_git.config.constants import ACCESS_TOKEN,DROPBOX_DESTINATION_FOLDERNAME

class TransferData:
    def __init__(self):
        self.access_token = ACCESS_TOKEN

    def upload_file(self, file_from, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)


def upload_to_dropbox_word(filepath):
    try:
        transferData = TransferData()

        file_from = filepath
        base_name = os.path.basename(file_from)
        file_to = '/{}/{}'.format(DROPBOX_DESTINATION_FOLDERNAME, base_name)  # The full path to upload the file to, including the file name
        print("writing into", file_to)
        # API v2
        transferData.upload_file(file_from, file_to)
        return True
    except Exception as e:
        create_error_log(e)
        return False
        
