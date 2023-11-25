import csv
import os
import random
import sys
import time
import json
import glob
import httplib2
import requests

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


####################### SET UP AND AUTENTIFICATION ############################

# Chemins vers les différents fichiers client_secrets.json pour chaque compte
CLIENT_SECRETS_FILES = glob.glob("bdd/json-client/client_secrets*.json") #retourne la liste des chemins vers les fichiers clients

# Emplacement du fichier CSV
CSV_FILE_PATH = "bdd/dataset.csv"

# Emplacement du fichier JSON pour le suivi des uploads
UPLOADED_VIDEOS_JSON = "bdd/uploaded-yt-videos.json"


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# CLIENT_SECRETS_FILE = "bdd/client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" 

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


# def get_authenticated_service(args):
#     flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
#                                    scope=YOUTUBE_UPLOAD_SCOPE,
#                                    message=MISSING_CLIENT_SECRETS_MESSAGE)

#     storage = Storage("%s-oauth2.json" % sys.argv[0])
#     credentials = storage.get()

#     if credentials is None or credentials.invalid:
#         credentials = run_flow(flow, storage, args)

#     return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
#                  http=credentials.authorize(httplib2.Http()))

def get_authenticated_service(client_secrets_file):
    flow = flow_from_clientsecrets(client_secrets_file, 
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)
    
    storage = Storage(f"{client_secrets_file}-oauth2.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                 http=credentials.authorize(httplib2.Http()))


########### LECTURE ET UPLOAD DES VIDEOS A PARTIR DU CSV ############


# Fonction pour lire le fichier CSV
def read_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        next(reader)  # Ignorer la première ligne
        return [row for row in reader]

def download_video(stream_link, file_path):
    try:
        response = requests.get(stream_link)
        response.raise_for_status()  # Vérifier que le téléchargement a réussi
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement de la vidéo: {e}")
        return False


# Fonction pour vérifier si une vidéo a déjà été uploadée
def upload_videos_from_csv(client_secrets_file, uploaded_videos):
    videos_to_upload = read_csv(CSV_FILE_PATH)
    youtube = get_authenticated_service(client_secrets_file)

    for video in videos_to_upload:
        video_id = video['\ufeffuuid']
        if video_id in uploaded_videos:
            continue

        video_file_path = f"bdd/videos-to-upload/{video_id}.mp4"
        
        # Vérifiez si la vidéo a déjà été téléchargée
        if not os.path.exists(video_file_path):
            if not download_video(video['stream_link'], video_file_path):
                continue  # Si le téléchargement échoue, passez à la vidéo suivante

        args = {
            'file': video_file_path,
            'title': video['\ufeffuuid'],
            'description': video['name'],
            'category': "28",
            'keywords': "",
            'privacyStatus': "private"
        }

        if not initialize_upload(youtube, args):
            print("Quota limit reached. Changing account.")
            return False  # Indiquez qu'il faut changer de compte
        uploaded_videos[video_id] = args['title']
        print(f"Video {video_id} uploaded successfully.")
        os.remove(video_file_path)  # Supprimer la vidéo téléchargée après l'upload

        with open(UPLOADED_VIDEOS_JSON, 'w') as json_file:
            json.dump(uploaded_videos, json_file)
    
    return True  # Indiquez qu'il n'est pas nécessaire de changer de compte



# Fonction d'initialisation de l'upload et autres fonctions existantes restent inchangées


################## GESTION DE L'UPLOAD D'UNE VIDEO #####################



# Fonction pour charger le fichier JSON des vidéos uploadées
def load_uploaded_videos(json_file_path):
    # Vérifiez si le fichier existe et qu'il n'est pas vide
    if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
        with open(json_file_path, 'r') as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError as e:
                print(f"Erreur lors de la lecture du fichier JSON : {e}")
                return {}  # Retourne un dictionnaire vide en cas d'erreur
    else:
        return {}  # Retourne un dictionnaire vide si le fichier n'existe pas ou est vide


# Fonction pour initialiser l'upload
def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    return(resumable_upload(insert_request))

# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if 'id' in response:
                print("Video id '%s' was successfully uploaded." % response['id'])
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            elif e.resp.status == 403:
                # Détection spécifique d'une erreur de quota
                print("Quota limit reached. Changing account.")
                return False # return False pour savoir qu'il faut changer de compte
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

    return True


def process_videos(client_secrets_files):
    print(len(client_secrets_files))
    uploaded_videos = load_uploaded_videos(UPLOADED_VIDEOS_JSON)

    for client_secrets_file in client_secrets_files: #parcours les fichier secrets json
        if not upload_videos_from_csv(client_secrets_file, uploaded_videos):
            continue #changer de compte si le quota est atteint


####################### MAIN ############################


if __name__ == '__main__':
    process_videos(CLIENT_SECRETS_FILES)