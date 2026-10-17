from pathlib import Path

# filepath constants
DATA_FILEPATH = Path('data')
DATA_FILEPATH.mkdir(exist_ok=True)

CONFIG_FILEPATH = Path('config.json')

# EMG signal constants
SAMPLE_RATE = 1000

# gesture constants
GESTURES_TO_PERFORM = ['Fist', 'Extended Palm', 'Peace', 'Thumbs up']
# add 1 to number for rest gesture
NUM_GESTURES = len(GESTURES_TO_PERFORM) + 1

# recording constants
NUM_GESTURE_RECORDINGS = 3
GESTURE_DURATION_SECONDS = 3
NUM_RECORDING_REPETITIONS = 3
