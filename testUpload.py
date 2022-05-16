from dataclasses import field
from genericpath import isdir, isfile
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
import io
import os
import mimetypes

scopes = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('service.json', scopes)

http_auth = credentials.authorize(Http())
drive = build('drive', 'v3', http=http_auth)

# Get file Id

results = drive.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)').execute()
items = results.get('files')

fileId = None
backupFileId = None

# Get fileId of data folder on Google drive
if not items:
    print('No files found.')
else:
    for item in items:
        # print(u'{0} ({1})'.format(item['name'], item['id']))
        if (item['name'] == 'data'):
            fileId = item['id']
        if (item['name'] == 'backup'):
            backupFileId = item['id']

file_metadata = {'name': 'test.js', 'parents': [fileId]}
media = MediaFileUpload('test.js',
                        mimetype=mimetypes.guess_type('./test.js')[0])
file = drive.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
print ('File created with ID: %s' % file.get('id'))