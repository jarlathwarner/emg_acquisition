import json

import numpy as np

from electrode_dataset.constants import CONFIG_FILEPATH
from electrode_dataset.constants import DATA_FILEPATH
from electrode_dataset.constants import NUM_GESTURES
from electrode_dataset.constants import SAMPLE_RATE

default_recording_id = 0

class DatasetManager:
    def __init__(self):
        # check if config file exists, create if it doesn't
        if not CONFIG_FILEPATH.is_file():
            CONFIG_FILEPATH.touch()

            # create default entry
            with open(CONFIG_FILEPATH, "w") as cfg:
                json.dump({'recording_id': default_recording_id}, cfg, indent=2)

        # open config file
        with open(CONFIG_FILEPATH, "r") as cfg:
            self.config = json.load(cfg)

    def get_next_recording_id(self):
        return self.config['recording_id'] + 1

    def save_data(self, dataset):
        next_id = self.get_next_recording_id() + 1
        filepath = DATA_FILEPATH.absolute() / f'#{next_id}_{SAMPLE_RATE}sample_{NUM_GESTURES}gestures.npy'

        np.save(filepath, dataset)
        print(f"Saved recording to --> {filepath}")

        # update recording id in config file
        self.config['recording_id'] = next_id
        with open(CONFIG_FILEPATH, "w") as cfg:
            json.dump(self.config, cfg)
