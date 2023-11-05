#!/bin/bash

# Vérification du nombre d'arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_video>"
    exit 1
fi

# Récupération de la vidéo d'entrée
input_video=$1
# Dossier où seront enregistrées les vidéos encodées
output_folder="encoded_videos_crf"
# Fichier CSV pour stocker les résultats
results_file="ffmpeg_tests_results_crf.csv"

# Création du dossier pour les vidéos encodées
mkdir -p $output_folder

# Initialisation du fichier CSV avec les noms de colonnes
echo "Constante rate factor,preset,psnr,ssim,file_size,output_file" > $results_file

# Boucles pour tester différentes valeurs de CRF et de préréglages
for crf in 0 10 18 27 40 50; do
    for preset in ultrafast medium slow; do
        # Nom du fichier de sortie basé sur les paramètres CRF et preset
        output_video="${output_folder}/output_${crf}_${preset}.mp4"

        # Encodage de la vidéo avec les paramètres spécifiés
        ffmpeg -i $input_video -c:v libx264 -crf $crf -preset $preset $output_video -y

        # Récupération de la taille du fichier encodé en kilo-octets (kB)
        file_size=$(du -k "$output_video" | cut -f1)

        # Calcul des métriques PSNR et SSIM pour la vidéo encodée
        metrics=$(ffmpeg -i $input_video -i $output_video -lavfi "ssim;[0:v][1:v]psnr" -f null - 2>&1 | grep -E 'PSNR|SSIM' | awk -F: '/SSIM/ {print $3} /PSNR/ {print $2}' | tr '\n' ',' | sed 's/,$//')

        # Ajout des résultats dans le fichier CSV
        echo "$crf,$preset,$metrics,$file_size,$output_video" >> $results_file
    done
done

# Affichage d'un message indiquant que les tests sont terminés
echo "Test terminé. Les résultats ont été enregistrés dans $results_file."

