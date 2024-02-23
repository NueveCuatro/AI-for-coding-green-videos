import os
import random
import shutil
from glob import glob
import sys


def balance_classes(base_dir, target_dir, major_class, minor_classes, minor_proportion):
    # Définir la graine pour la reproductibilité
    random.seed(42)

    # Créer le répertoire cible s'il n'existe pas
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Calculer le nombre total de frames pour la classe majoritaire
    major_class_dir = os.path.join(base_dir, major_class, 'output_array_test')
    total_frames_major = sum(len(os.listdir(os.path.join(major_class_dir, video_dir))) for video_dir in os.listdir(major_class_dir))
    
    # Copier toutes les frames de la classe majoritaire
    all_major_frames = [f for video_folder in os.listdir(major_class_dir) for f in glob(os.path.join(major_class_dir, video_folder, '*.npy'))]
    all_major_frames.sort()
    for frame_path in all_major_frames:
        target_path = os.path.join(target_dir, os.path.basename(frame_path))
        shutil.copy(frame_path, target_path)

    # Équilibrer chaque classe mineure
    for minor_class in minor_classes:
        minor_class_dir = os.path.join(base_dir, minor_class, 'output_array_test')
        # Calculer le nombre de frames à sélectionner pour chaque classe mineure pour atteindre 25%
        desired_minor_count = int(total_frames_major * minor_proportion)
        
        all_minor_frames = [f for video_folder in os.listdir(minor_class_dir) for f in glob(os.path.join(minor_class_dir, video_folder, '*.npy'))]
        all_minor_frames.sort() #trier les frames pour la reproductibilité puisqu'on est pas sur que glob ou os les prennent dans l'ordre
        selected_minor_frames = random.sample(all_minor_frames, min(desired_minor_count, len(all_minor_frames)))

        # Copier les frames sélectionnées dans le répertoire cible
        for frame_path in selected_minor_frames:
            target_path = os.path.join(target_dir, os.path.basename(frame_path))
            shutil.copy(frame_path, target_path)

# Configuration
if len(sys.argv) != 4:
    print("Usage: python3 balance.py 'class_name'")
    sys.exit(1)

base_dir = sys.argv[1]  # Chemin de base vers vos données
target_dir = sys.argv[2]  # Chemin cible pour le dataset équilibré
major_class = sys.argv[3]

if major_class == 'vidmizer':
    minor_classes = ['tiktok', 'youtube']
elif major_class == 'tiktok':
    minor_classes = ['vidmizer', 'youtube']
elif major_class == 'youtube':
    minor_classes = ['vidmizer', 'tiktok']
else:
    raise ValueError("Invalid major class")

#major_proportion = 0.5  # Non utilisé dans ce script, toutes les frames de la classe majoritaire sont prises
minor_proportion = 0.5

balance_classes(base_dir, target_dir, major_class, minor_classes, minor_proportion)

#python3 balance_3_channel.py 'source bdd' 'target folder'  'major_class'  # Chemin de base vers vos données