import os
import sys

def annotate_folder(folder_path, output_file, class_mapping):
    files = os.listdir(folder_path)

    with open(output_file, 'w') as out_file:
        for file_name in files:
            if file_name.endswith('.npy'):
                # Extraction du préfixe qui est l'identifiant de la classe
                prefix = file_name.split('_')[0]

                # Obtention du numéro de classe correspondant
                class_id = class_mapping.get(prefix, 'Unknown')

                if class_id != 'Unknown':
                    file_name_without_extension = os.path.splitext(file_name)[0]
                    out_file.write(f"{file_name_without_extension} {class_id}\n")

if len(sys.argv) != 6:
    print("Usage: python annotate.py input_folder output_file.txt vidmizer_id youtube_id tiktok_id")
    sys.exit(1)

input_folder = sys.argv[1]  # (str) Chemin vers le dossier contenant les fichiers .npy
output_file = sys.argv[2]  # (str) Chemin vers le fichier de sortie
class_mapping = {
    'vidmizer': sys.argv[3], 
    'youtube': sys.argv[4],
    'tiktok': sys.argv[5]
}

annotate_folder(input_folder, output_file, class_mapping)
