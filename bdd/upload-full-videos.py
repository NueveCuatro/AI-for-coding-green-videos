import csv
import os
import random
import sys
import time
import json
import glob
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Chemins vers les différents fichiers client_secrets.json pour chaque compte
CLIENT_SECRETS_FILES = glob.glob("bdd/client_secrets*.json") #retourne la liste des chemins vers les fichiers clients


# Emplacement du fichier CSV
CSV_FILE_PATH = "bdd/dataset.csv"

# Emplacement du fichier JSON pour le suivi des uploads
UPLOADED_VIDEOS_JSON = "bdd/uploaded-yt-videos.json"

# Autres constantes
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

# Fonction pour obtenir un service authentifié
def get_authenticated_service(client_secrets_file):
    flow = flow_from_clientsecrets(client_secrets_file, scope=YOUTUBE_UPLOAD_SCOPE)
    storage = Storage(f"{client_secrets_file}-oauth2.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials.authorize(httplib2.Http()))


# Fonction pour lire le fichier CSV
def read_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# Fonction pour vérifier si une vidéo a déjà été uploadée
def is_video_uploaded(video_id, uploaded_videos):
    return video_id in uploaded_videos

# Fonction pour l'upload des vidéos
def upload_videos_from_csv(client_secrets_file):
    uploaded_videos = {}
    if os.path.exists(UPLOADED_VIDEOS_JSON):
        with open(UPLOADED_VIDEOS_JSON, 'r') as json_file:
            uploaded_videos = json.load(json_file)

    videos_to_upload = read_csv(CSV_FILE_PATH)
    youtube = get_authenticated_service(client_secrets_file)

    for video in videos_to_upload:
        video_id = video['uuid']  # Assurez-vous que votre CSV a une colonne uuid
        if is_video_uploaded(video_id, uploaded_videos):
            continue

        # Paramètres de la vidéo à uploader
        # Adaptez ces paramètres en fonction de la structure de votre fichier CSV
        args = {
            'file': video['filepath'],
            'title': video['title'],
            'description': video['description'],
            'category': video['category'],
            'keywords': video['keywords'],
            'privacyStatus': video['privacyStatus']
        }

        try:
            initialize_upload(youtube, args)
            uploaded_videos[video_id] = args['file']
        except HttpError as e:
            print(f"Une erreur HTTP {e.resp.status} s'est produite:\n{e.content}")
            continue

        # Mettre à jour le fichier JSON après chaque upload réussi
        with open(UPLOADED_VIDEOS_JSON, 'w') as json_file:
            json.dump(uploaded_videos, json_file)

# Fonction d'initialisation de l'upload et autres fonctions existantes restent inchangées

# Cette méthode implémente une logique de reprise pour reprendre un
# upload échoué.
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
                return False
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


def upload_video(youtube, video_info):
    try:
        initialize_upload(youtube, video_info)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        if e.resp.status == 403:
            return False
    return True

def process_videos(client_secrets_files):
    videos_to_upload = read_csv(CSV_FILE_PATH)
    uploaded_videos = load_uploaded_videos_json()

    for client_secrets_file in client_secrets_files:
        youtube = get_authenticated_service(client_secrets_file)

        for video in videos_to_upload: #prend les videos du CSV
            video_id = video['uuid'] # prend l'uuid de la video
            if video_id not in uploaded_videos: # si la video n'est pas dans le json
                success = upload_video(youtube, video) 
                if not success:
                    print("Switching to next account due to quota limit.")
                    break  # Sortie de la boucle interne pour passer au compte suivant
                uploaded_videos.add(video_id)
                save_uploaded_videos_json(uploaded_videos)

if __name__ == '__main__':
    process_videos(CLIENT_SECRETS_FILES)




def initialize_upload(youtube, options):
    # ... (la configuration initiale reste inchangée)

    insert_request = youtube.videos().insert(
        # ... (configuration inchangée)
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)  # Retournez le résultat de resumable_upload


def upload_videos_from_csv(client_secrets_file):
    # ... (le début de la fonction reste inchangé)

    for video in videos_to_upload:
        video_id = video['uuid']
        if video_id in uploaded_videos:
            continue

        args = {
            # ... (configuration des arguments inchangée)
        }

        if not initialize_upload(youtube, args):
            print("Quota limit reached. Changing account.")
            return False  # Indiquez qu'il faut changer de compte
        uploaded_videos[video_id] = args['file']
        
        # ... (mise à jour du fichier JSON)

    return True  # Toutes les vidéos de ce compte ont été traitées


def process_videos(client_secrets_files, csv_file_path):
    videos_to_upload = read_csv(csv_file_path)
    uploaded_videos = load_uploaded_videos_json()

    for client_secrets_file in client_secrets_files:
        youtube = get_authenticated_service(client_secrets_file)

        if not upload_video_from_csv(youtube, videos_to_upload, uploaded_videos):
            continue  # Changez de compte si le quota est atteint



def upload_videos_from_csv(client_secrets_file, uploaded_videos):
    videos_to_upload = read_csv(CSV_FILE_PATH)
    youtube = get_authenticated_service(client_secrets_file)

    for video in videos_to_upload:
        video_id = video['uuid']
        if video_id in uploaded_videos:
            continue

        video_file_path = f"bdd/videos-to-upload/{video_id}.mp4"
        
        # Vérifiez si la vidéo a déjà été téléchargée
        if not os.path.exists(video_file_path):
            if not download_video(video['stream_link'], video_file_path):
                continue  # Si le téléchargement échoue, passez à la vidéo suivante

        args = {
            'file': video_file_path,
            'title': video['uuid'],
            'description': video['name'],
            'category': "28",
            'keywords': "",
            'privacyStatus': "private"
        }

        if not initialize_upload(youtube, args):
            print("Quota limit reached. Changing account.")
            return False  # Indiquez qu'il faut changer de compte
        uploaded_videos[video_id] = args['title']
        os.remove(video_file_path)  # Supprimer la vidéo téléchargée après l'upload

        with open(UPLOADED_VIDEOS_JSON, 'w') as json_file:
            json.dump(uploaded_videos, json_file)
    
    return True  # Indiquez qu'il n'est pas nécessaire de changer de compte






if __name__ == '__main__':
    process_videos(CLIENT_SECRETS_FILES, CSV_FILE_PATH)