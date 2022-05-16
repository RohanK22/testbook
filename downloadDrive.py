from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
import io
import os

scopes = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name('service.json', scopes)

http_auth = credentials.authorize(Http())
drive = build('drive', 'v3', http=http_auth)

results = drive.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)').execute()
items = results.get('files')

fileId = None

if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        print(u'{0} ({1})'.format(item['name'], item['id']))
        if (item['name'] == 'data'):
            fileId = item['id']
            break

def retaining_folder_structure(query,filepath):
    results = drive.files().list(fields="nextPageToken, files(id, name, kind, mimeType)",q=query).execute()
    items = results.get('files', [])
    for item in items:
        #print(item['name'])
        if item['mimeType']=='application/vnd.google-apps.folder':
            fold=item['name']
            path=filepath+'/'+fold
            if os.path.isdir(path):
                retaining_folder_structure("'%s' in parents"%(item['id']),path)
            else:
                os.mkdir(path)
                retaining_folder_structure("'%s' in parents"%(item['id']),path)
        else:
            request = drive.files().get_media(fileId=item['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
            path=filepath+'/'+item['name']
            #print(path)
            with io.open(path,'wb') as f:
                fh.seek(0)
                f.write(fh.read())

if not fileId:
    print("No data on drive... nothing to download")
else:
    retaining_folder_structure("mimeType='application/vnd.google-apps.folder'",'./')



