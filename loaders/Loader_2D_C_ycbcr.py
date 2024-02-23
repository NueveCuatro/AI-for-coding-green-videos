
import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from torchvision import transforms

############ Custom Dataset #############
class CustomImageDataset(Dataset):
    def __init__(self, annotations_file, npy_dir, transform=None, target_transform=None):
        self.npy_labels = pd.read_csv(annotations_file, header=None, sep=' ')
        self.npy_dir = npy_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.npy_labels)

    def __getitem__(self, idx):
        # Ici nos indices de lignes étaient confondus avec notre nom d'image
        # Ce n'est plus le cas dans la version binaire ce qui impose la modification suivante :
        #npy_path = self.npy_dir + '/' + str(idx) +'.png'
        # print(idx)
        npy_path = self.npy_dir + '/' + str(self.npy_labels.iloc[idx,0]) +'.npy'
        # print(npy_path)
        array = np.load(npy_path)
        x = torch.from_numpy(array).float()
        # array3ch = np.stack((array,)*3, axis=-1)
        label = self.npy_labels.iloc[idx, 1]
        if self.transform:
            x = self.transform(x)
        if self.target_transform:
            label = self.target_transform(label)
        return x, label

##################################################