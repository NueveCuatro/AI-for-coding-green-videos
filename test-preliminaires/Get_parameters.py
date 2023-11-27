import subprocess
import json

def get_video_encoding_parameters(video_path):
    try:
        # Utilisez la commande ffprobe pour obtenir des informations sur la vidéo
        command = [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,codec_name",
              "-of", "json", video_path
        ]

        # Exécutez la commande ffprobe et capturez la sortie
        result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, _ = result.communicate()

        # Analysez la sortie JSON
        video_info = json.loads(output)

        return video_info

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    video_path = "../totoro_vf.mp4"
    encoding_parameters = get_video_encoding_parameters(video_path)
    if encoding_parameters:
        print("Paramètres de codage vidéo :")
        print(json.dumps(encoding_parameters, indent=4))
    else:
        print("Impossible de récupérer les paramètres de codage vidéo.")
