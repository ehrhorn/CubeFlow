import torch
from datetime import datetime
import pandas as pd

from src.modules.utils import get_time
from src.modules.utils import get_project_root
from src.modules.invert_transforms import TransformsInverter


class Saver:
    def __init__(self, config, wandb, files_and_dirs):
        super(Saver, self).__init__()
        self.config = config
        self.wandb = wandb
        self.files_and_dirs = files_and_dirs

        self.train_true_energy = []
        self.train_event_length = []
        self.epoch_val_loss = []
        self.early_stopping_counter = 0

        self.transform_object = TransformsInverter(self.config, self.files_and_dirs)

        self.column_names = [
            'event'
        ]
        self.column_names += ['predicted_' + name.replace('true_', '') for name in self.config.targets]
        self.data = {name: [] for name in self.column_names}

    def train_step(self, train_true_energy, train_event_length):
        if self.config.save_train_dists:
            self.train_true_energy.extend(train_true_energy.tolist())
            self.train_event_length.extend(train_event_length.tolist())

    def on_val_step(
        self,
        x,
        y,
        y_hat,
        comparisons,
        energy,
        event_length,
        file_number
    ):
        values = [
            list(file_number),
            *[y_hat[:, i].tolist() for i in range(y_hat.size(1))],
        ]
        for i, key in enumerate(self.data):
            self.data[key].extend(values[i])

    def on_val_end(self):
        self.data = self.transform_object.transform_inversion(self.data)
        comparison_df = pd.DataFrame().from_dict(self.data)
        file_name = self.files_and_dirs['run_root'].joinpath(
            'prediction_dataframe_parquet.gzip'
        )
        comparison_df.to_parquet(
            str(file_name),
            compression='gzip'
        )
        if self.config.save_train_dists:
            train_dists_dict = {}
            train_dists_dict['train_true_energy'] = self.train_true_energy
            train_dists_dict['train_event_length'] = self.train_event_length
            train_dists_df = pd.DataFrame().from_dict(train_dists_dict)
            train_dists_file_name = self.files_and_dirs['train_dists_path'].joinpath(
                'train_dists_parquet.gzip'
            )
            train_dists_df.to_parquet(
                str(train_dists_file_name),
                compression='gzip'
            )
        self.data = {name: [] for name in self.column_names}

    def early_stopping(self, epoch, epoch_val_loss, model_state_dict, optimizer_state_dict):
        epoch_val_loss = round(epoch_val_loss.item(), 3)
        if epoch == 0 or epoch_val_loss < min(self.epoch_val_loss):
            best_val_loss = epoch_val_loss
            self.save_model_state(epoch, model_state_dict, optimizer_state_dict)
            self.early_stopping_counter = 0
            print('{}: best model yet, saving'.format(get_time()))
        else:
            self.early_stopping_counter += 1
            print('{}: model didn\'t improve for {} epoch(s)'.format(get_time(), self.early_stopping_counter))
        self.epoch_val_loss.append(epoch_val_loss)
        if self.early_stopping_counter >= self.config.patience:
            return True
        else:
            return False
    
    def save_model_state(self, epoch, model_state_dict, optimizer_state_dict):
        model_path = self.files_and_dirs['run_root'].joinpath('model.pt')
        torch.save(
            {
                'epoch': epoch,
                'model_state_dict': model_state_dict,
                'optimizer_state_dict': optimizer_state_dict
            },
            model_path
        )

    def upload_model_files(self):
        file = self.files_and_dirs['python_model_file']
        if self.config.wandb:
            self.wandb.save(str(file))
            self.wandb.save(str(self.files_and_dirs['run_root'].joinpath('model.pt')))
            self.wandb.save(str(get_project_root().joinpath('configs/cnn.json')))
