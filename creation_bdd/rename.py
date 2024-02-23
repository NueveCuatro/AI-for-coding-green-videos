import os
import sys
def rename_frames(base_dir, class_name):
    # Parcourir chaque sous-dossier dans le dossier de base (chaque sous-dossier représente une vidéo)
    for video_folder in os.listdir(base_dir):
        video_folder_path = os.path.join(base_dir, video_folder)
        if os.path.isdir(video_folder_path):
            # Parcourir chaque fichier .npy dans le sous-dossier (chaque fichier représente une frame)
            for frame_file in os.listdir(video_folder_path):
                if frame_file.endswith(".npy"):
                    # Construire le nouveau nom de fichier en ajoutant le nom de la classe
                    new_frame_file = f"{class_name}_{frame_file}"
                    # Construire le chemin complet vers l'ancien et le nouveau fichier
                    old_frame_path = os.path.join(video_folder_path, frame_file)
                    new_frame_path = os.path.join(video_folder_path, new_frame_file)
                    # Renommer le fichier
                    os.rename(old_frame_path, new_frame_path)
                    print(f"Renamed {old_frame_path} to {new_frame_path}")

# Utilisation de la fonction
if len(sys.argv) != 3:
    print("Usage: python3 rename.py 'base_directory' 'class_name'")
    sys.exit(1)

base_dir = sys.argv[1]  # ici, base_dir est le chemin vers le dossier contenant les sous-dossiers représentant les vidéos
class_name = sys.argv[2] # ici, class_name est le nom de la classe à ajouter aux noms de fichiers

rename_frames(base_dir, class_name)
