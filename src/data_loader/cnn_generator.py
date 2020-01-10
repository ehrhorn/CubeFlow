from torch.utils.data import Dataset
import numpy as np
import h5py as h5
import pandas as pd


class CnnGenerator(Dataset):
    def __init__(self, config, ids, test):
        self.config = config
        self.ids = ids
        self.test = test
        if self.config.dev_run == True:
            self.config.batch_size = 2
        self.on_epoch_end()


    def __len__(self):
        return int(np.floor(len(self.ids)))


    def __getitem__(self, index):
        X, y = self.__data_generation(index)
        return X, y


    def on_epoch_end(self):
        self.indices = np.arange(len(self.ids))
        if self.config.shuffle == True and self.test == False:
            np.random.shuffle(self.indices)


    def __data_generation(self, index):
        X = np.zeros(
            (
                self.config.batch_size,
                self.config.max_doms,
                len(self.config.features)
            )
        )
        y = np.zeros((self.config.batch_size, len(self.config.targets)))
        file = list(self.ids[index].keys())[0]
        idx = list(self.ids[index].values())[0]
        idx = sorted(idx)
        features_dict = {
            feature: [] for feature in self.config.features

        }
        targets_dict = {
            target: [] for target in self.config.targets
        }
        with h5.File(file, 'r') as f:
            for feature in self.config.features:
                features_dict[feature] = f[
                    self.config.transform + '/' + feature
                ][idx]
            for target in self.config.targets:
                dataset_name = self.config.transform + '/' + target
                if dataset_name in f:
                    targets_dict[target] = f[dataset_name][idx]
                else:
                    targets_dict[target] = f['raw/' + target][idx]
        for i, feature in enumerate(features_dict):
            no_of_events = len(features_dict[feature])
            for j in range(no_of_events):
                event_length = len(features_dict[feature][j])
                X[j, 0:event_length, i] = features_dict[feature][j]
        for i, target in enumerate(targets_dict):
            no_of_events = len(targets_dict[target])
            for j in range(no_of_events):
                y[j, i] = targets_dict[target][j]
        X = np.transpose(X, (0, 2, 1))
        return X, y
