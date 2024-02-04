
import os
import numpy as np
import pandas as pd
from torch.utils.data import Dataset

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
        array = np.load(npy_path).astype(np.float32)
        array3ch = np.stack((array,)*3, axis=-1)
        label = self.npy_labels.iloc[idx, 1]
        if self.transform:
            array3ch = self.transform(array3ch)
        if self.target_transform:
            label = self.target_transform(label)
        return array3ch, label
##################################################