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

results = drive.files().list(q = "'" + fileId + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])
cinputFileID = None
coutputFileId = None
cprocessedFileId = None
for item in items:
    if (item['name'] == 'input'):
        cinputFileID = item['id']
    if (item['name'] == 'output'):
        coutputFileId = item['id']
    if (item['name'] == 'processed'):
        cprocessedFileId = item['id']

# # Copy all files in 'input', 'processed', 'output' into 'backup/input' ...
# if (backupFileId == None):
#     # Create a new folder for backup and sub folders
#     file_metadata = {
#         'name': 'backup',
#         'mimeType': 'application/vnd.google-apps.folder'
#     }
#     file = drive.files().create(body=file_metadata, fields='id').execute()
#     print ('Folder ID: %s' % file.get('id'))
#     backupFileId = file.get('id')
#     backupFile = drive.files().get(fileId=backupFileId)
#     backupFile.create(body={
#         'name': 'input',
#         'mimeType': 'application/vnd.google-apps.folder'
#     }, fields="id").execute()
#     backupFile.create(body={
#         'name': 'output',
#         'mimeType': 'application/vnd.google-apps.folder'
#     }, fields="id").execute()
#     backupFile.create(body={
#         'name': 'processed',
#         'mimeType': 'application/vnd.google-apps.folder'
#     }, fields="id").execute()

# results = drive.files().list(q = "'" + backupFileId + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
# items = results.get('files', [])
# inputFileID = None
# outputFileId = None
# processedFileId = None
# for item in items:
#     if (item['name'] == 'input'):
#         inputFileID = item['id']
#     if (item['name'] == 'output'):
#         outputFileId = item['id']
#     if (item['name'] == 'processed'):
#         processedFileId = item['id']

# print(cinputFileID)
# results = drive.files().list(q = "'" + cinputFileID + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
# inputFiles = results.get('files', [])
# for file in inputFiles:
#     drive.files().update(fileId=file['id'],
#                                     addParents=inputFileID,
#                                     removeParents=cinputFileID,
#                                     fields='id, parents').execute()
#     # drive.files().copy(fileId=file['id'], body={"parents": [inputFileID], 'name': file['name']} ).execute()
#     # drive.files().delete(fileid=file['id']).execute()

# results = drive.files().list(q = "'" + coutputFileId + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
# outputFiles = results.get('files', [])
# print(outputFiles)
# for file in outputFiles:
#     drive.files().update(fileId=file['id'],
#                                     addParents=outputFileId,
#                                     removeParents=coutputFileId,
#                                     fields='id, parents').execute()
#     # drive.files().copy(fileId=file['id'], body={"parents": [outputFileId], 'name': file['name']} ).execute()
#     # drive.files().delete(fileid=file['id']).execute()

# results = drive.files().list(q = "'" + cprocessedFileId + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
# processedFiles = results.get('files', [])
# for file in processedFiles:
#     drive.files().update(fileId=file['id'],
#                                     addParents=processedFileId,
#                                     removeParents=cprocessedFileId,
#                                     fields='id, parents').execute()
#     # drive.files().copy(fileId=file['id'], body={"parents": [processedFileId], 'name': file['name']} ).execute()
#     # drive.files().delete(fileid=file['id']).execute()

# Upload files in 'input', 'processed', 'output' to google drive
def upload(folderName, fId):
    items = os.listdir(folderName)   
    for item in items:
        file_metadata = {'name': item, 'parents': [fId]}
        media = MediaFileUpload(folderName + item,
                                mimetype=mimetypes.guess_type(folderName + item)[0])
        file = drive.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        print ('File created with ID: %s' % file.get('id'))

upload('data/input/', cinputFileID)
upload('data/output/', coutputFileId)
upload('data/processed/', cprocessedFileId)


# file_metadata = {'name': 'test.js'}
# media = MediaFileUpload('data' + '/test.js',
#                         mimetype=mimetypes.guess_type('./test.js')[0])
# file = drive.files().create(body=file_metadata,
#                                     media_body=media,
#                                     fields='id').execute()
# print ('File created with ID: %s' % file.get('id'))