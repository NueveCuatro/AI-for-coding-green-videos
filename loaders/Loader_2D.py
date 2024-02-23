
import os
import pandas as pd
import torch
from torchvision.io import read_image
from torch.utils.data import Dataset
from PIL import Image

############ Custom Dataset #############
class CustomImageDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform, target_transform=None):
        self.img_labels = pd.read_csv(annotations_file, header=None, sep=' ')
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        # Ici nos indices de lignes étaient confondus avec notre nom d'image
        # Ce n'est plus le cas dans la version binaire ce qui impose la modification suivante :
        #img_path = self.img_dir + '/' + str(idx) +'.png'
        # print(idx)
        img_path = self.img_dir + '/' + str(self.img_labels.iloc[idx,0]) +'.png'
        # print(img_path)
        # image = read_image(img_path)
        # image = torch.from_numpy(image).float()
        image = Image.open(img_path)


        label = self.img_labels.iloc[idx, 1]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label
##################################################