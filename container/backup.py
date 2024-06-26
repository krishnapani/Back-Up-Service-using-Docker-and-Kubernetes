import pickle
import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

# Set up logging
logging.basicConfig(filename='back.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MyDrive:
    def __init__(self):
        creds = None
        token_file = 'credentials/token.pickle'
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        if not creds:
            raise Exception("Credentials not found.")

        self.service = build('drive', 'v3', credentials=creds)

    def upload_file(self, filename, path):
        folder_id = "1J_6ssMlwGDGvK0ioUABH9W5bc2-Ki9sd"
        media = MediaFileUpload(os.path.join(path, filename))

        logging.info(f"Checking if file '{filename}' exists in Google Drive folder...")
        response = self.service.files().list(
                                        q=f"name='{filename}' and parents='{folder_id}' and trashed=false",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=None).execute()
        if not response['files']:
            logging.info(f"File '{filename}' not found. Uploading new file...")
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            logging.info(f"New file '{filename}' created with ID {file.get('id')}")
        else:
            for file in response.get('files', []):
                logging.info(f"File '{filename}' found. Updating existing file...")
                update_file = self.service.files().update(
                    fileId=file.get('id'),
                    media_body=media,
                ).execute()
                logging.info(f"File '{filename}' updated.")

def main():
    path = "folder/"
    my_drive = MyDrive()

    for item in os.listdir(path):
        logging.info(f"Processing file '{item}'...")
        try:
            my_drive.upload_file(item, path)
        except Exception as e:
            logging.error(f"Error occurred while uploading file '{item}': {str(e)}")
    logging.info("Backup process completed.")
    time.sleep(300)

if __name__ == '__main__':
    main()
