import numpy as np
import os
import sys
from glob import glob

def concatenate_frames(class_name, luma_dir, cr_dir, cb_dir, output_dir):
    # Assurer que le répertoire de sortie existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Parcourir tous les dossiers de LUMA, qui contiennent des frames pour chaque vidéo
    for video_folder in os.listdir(luma_dir):
        luma_video_dir = os.path.join(luma_dir, video_folder)
        video_number = video_folder.split('_')[0]
        cr_video_dir = os.path.join(cr_dir, f'{video_number}_Cr')
        cb_video_dir = os.path.join(cb_dir, f'{video_number}_Cb')
        
        # Créer un sous-dossier pour la vidéo dans le répertoire de sortie
        video_output_dir = os.path.join(output_dir, f'{video_number}')
        if not os.path.exists(video_output_dir):
            os.makedirs(video_output_dir)
        
        # Obtenir la liste des frames LUMA, et supposer que les frames Cb et Cr correspondent
        luma_frames = sorted(glob(os.path.join(luma_video_dir, '*.npy')))
        for luma_frame_path in luma_frames:
            frame_number = os.path.basename(luma_frame_path).split('_')[-1]  # Obtenir le numéro de la frame
            # Construire le chemin vers les frames Cr et Cb correspondantes
            cr_frame_path = os.path.join(cr_video_dir, f"{class_name}_{video_number}_Cr_frame_{frame_number}")
            cb_frame_path = os.path.join(cb_video_dir, f"{class_name}_{video_number}_Cb_frame_{frame_number}")
            # cb_frame_path = os.path.join(cb_video_dir, f"tiktok_{video_number}_Cb_frame_{frame_number}")
            # cr_frame_path = os.path.join(cr_video_dir, f"tiktok_{video_number}_Cr_frame_{frame_number}")
            
            # Charger les frames
            luma_frame = np.load(luma_frame_path)
            cr_frame = np.load(cr_frame_path)
            cb_frame = np.load(cb_frame_path)
            
            # Vérifier que les dimensions des frames correspondent
            if luma_frame.shape != cr_frame.shape or luma_frame.shape != cb_frame.shape:
                raise ValueError(f"Frame dimensions do not match for frame {frame_number}")
            
            # Concaténer les frames pour créer une frame YCbCr
            ycbcr_frame = np.stack((luma_frame, cb_frame, cr_frame))
            
            # Enregistrer la frame YCbCr dans le sous-dossier correspondant à la vidéo
            output_frame_path = os.path.join(video_output_dir, f"{class_name}_ycbcr_{frame_number}")
            np.save(output_frame_path, ycbcr_frame)
            print(f"Saved concatenated frame to {output_frame_path}")



# Configuration
if len(sys.argv) != 2:
    print("Usage: python3 channels.py 'class_name'")
    sys.exit(1)

class_name = sys.argv[1]  # Classe pour laquelle concaténer les frames

luma_dir = f'{class_name}/bdd_{class_name}_array_LUMA'  # Chemin vers les frames LUMA
cr_dir = f'{class_name}/bdd_{class_name}_array_Cr'  # Chemin vers les frames Cr
cb_dir = f'{class_name}/bdd_{class_name}_array_Cb'  # Chemin vers les frames Cb
output_dir = f'{class_name}/output_array'  # Chemin cible pour les frames concaténées

concatenate_frames(class_name, luma_dir, cr_dir, cb_dir, output_dir)