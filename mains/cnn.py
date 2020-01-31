import os
import torch
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping
import wandb as wandb
import numpy as np
# import matplotlib.pyplot as plt
import matplotlib.cbook
import warnings
import joblib
from warmup_scheduler import GradualWarmupScheduler
# from torch_lr_finder import LRFinder
from sklearn.model_selection import train_test_split
import pickle

from src.lightning_systems.cnn import CnnSystem
from preprocessing.cnn_preprocessing import CnnPreprocess
from utils.config import process_config
from utils.utils import get_args
from utils.utils import get_project_root
from utils.utils import get_time
from utils.utils import print_data_set_sizes
from utils.utils import create_experiment_name
from utils.utils import set_random_seed
from utils.math_funcs import angle_between
from plots.plot_functions import histogram

warnings.filterwarnings(
    'ignore',
    category=matplotlib.cbook.mplDeprecation
)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# print('Using device', device)


# @profile
def main():
    # capture the config path from the run arguments
    # then process the json configuration file
    try:
        args = get_args()
        config = process_config(args.config)

    except:
        print('missing or invalid arguments')
        exit(0)

    experiment_name = create_experiment_name(config, slug_length=2)

    if config.wandb == True and config.exp_name != 'lr_finder':
        wandb.init(
                project='cubeflow',
                name=experiment_name
            )

    # sets = joblib.load(
    #     get_project_root().joinpath(
    #         'sets/' + str(config.particle_type) + '.joblib'
    #     )
    # )
    # print('Starting preprocessing at {}'.format(get_time()))
    # data = CnnPreprocess(sets, config)
    # sets = data.return_indices()
    # print('Ended preprocessing at {}'.format(get_time()))

    pickle_file = Path.home().joinpath('data/CubeData/' + config.data_type + '/masks/muon_neutrino.pickle')
    with open(pickle_file, 'rb') as f:
        file_indices_particle = pickle.load(f)
    
    pickle_file = Path.home().joinpath('data/CubeData/' + config.data_type + '/masks/dom_interval_min0_max200.pickle')
    with open(pickle_file, 'rb') as f:
        file_indices_max_doms = pickle.load(f)

    file_indices = list(set(file_indices_particle) & set(file_indices_max_doms))
    sets = {}
    sets['train'], sets['test'] = train_test_split(
        file_indices,
        test_size=config.test_fraction,
        random_state=config.random_state
    )
    sets['train'], sets['validate'] = train_test_split(
        sets['train'],
        test_size=config.validation_fraction,
        random_state=config.random_state
    )

    set_random_seed()

    # summary(model, input_size=(len(config.features), config.max_doms))

    model = CnnSystem(sets, config, wandb)

    if config.wandb == True:
        wandb.watch(model)

    early_stop_callback = EarlyStopping(
        monitor='val_loss',
        min_delta=0.00,
        patience=config.patience,
        verbose=False,
        mode='min'
    )

    trainer = Trainer(
        gpus=config.gpus,
        max_epochs=config.num_epochs,
        fast_dev_run=config.dev_run,
        early_stop_callback=None if config.patience == 0 else early_stop_callback
    )
    # trainer = Trainer(
    #     max_epochs=1,
    #     early_stop_callback=None
    # )
    trainer.fit(model)
    trainer.test()

    #     resolution = np.empty((0, len(config.targets)))
    #     direction = np.empty((0, 1))
    #     for inputs, targets in test_generator:
    #         inputs = inputs.to(device)
    #         targets = targets.to(device)
    #         predictions = prediction_step(model, inputs)
    #         resolution = np.vstack(
    #             [resolution, (targets.cpu() - predictions.cpu())]
    #         )
    #         for i in range(predictions.shape[0]):
    #             angle = angle_between(
    #                 targets.cpu()[i, :],
    #                 predictions.cpu()[i, :]
    #             )
    #             direction = np.vstack([direction, angle])

    #     if config.wandb == True:
    #         fig, ax = histogram(
    #             data=direction,
    #             title='arccos[y_truth . y_pred / (||y_truth|| ||y_pred||)]',
    #             xlabel='Angle (radians)',
    #             ylabel='Frequency',
    #             width_scale=1,
    #             bins='fd'
    #         )
    #         wandb.log({'Angle error': fig})

if __name__ == '__main__':
    main()
