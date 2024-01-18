# %% [markdown]
# # Generation de la database 2D
# 

# %%
### Useful Path ###
dataset_3D = '../Database_3D/dataset_train'
dataset_test_3D = '../Database_3D/dataset_test'

# %%
dataset_2D = '../Database_2D/dataset_train'
dataset_test_2D = '../Database_2D/dataset_test'

# %%
##### Librairies #####
import os
import cv2
import subprocess
import shutil

# %%
### Nettoyer la base de donnée ######
# remove all the folder of the database
shutil.rmtree(dataset_2D)
shutil.rmtree(dataset_test_2D)

# %%
####### Database creation ########
os.makedirs(dataset_2D)
os.makedirs(dataset_test_2D)

# %%
id_frame = 0

# %%
labels_map = {
    "tiktok": 0 ,
    "vimizer":1,
    "youtube": 2 , 
}
########### Train ###################
for folder in os.listdir(dataset_3D):
    if not folder.endswith('.txt'):
        print(folder)
        for frame in os.listdir(dataset_3D + '/' + folder):
            print(frame)
            command = "cp " + dataset_3D + '/' + folder + '/' + frame + " " + dataset_2D + '/' + str(frame)+'.png'
            subprocess.run(command, shell=True)
            with open(dataset_2D +'/annotation.txt', 'a') as file:
                    
                file.write(str(id_frame) + " " + str(labels_map[folder])+"\n")
            


# %%
############ Test ################
for folder in os.listdir(dataset_test_3D):
    if not folder.endswith('.txt'):
        print(folder)
        for frame in os.listdir(dataset_test_3D + '/' + folder):
            print(frame)
            command = "cp " + dataset_test_3D + '/' + folder + '/' + frame + " " + dataset_test_2D + '/' + str(frame)+'.png'
            subprocess.run(command, shell=True)
            with open(dataset_test_2D +'/annotation.txt', 'a') as file:
                    
                file.write(str(id_frame) + " " + str(labels_map[folder])+"\n")


