import logging.config
import pathlib
import pickle
from collections import Counter, deque
import struct
import sys
import time
from pathlib import Path

import pandas as pd
import pygame
import sklearn.preprocessing
from pygame.locals import *
import numpy as np

from pyomyo import Myo, emg_mode
from scipy.signal import butter
from scipy.signal import filtfilt
from sklearn import metrics
from sklearn import svm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

LOGGING_CONF_FILEPATH = pathlib.Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(LOGGING_CONF_FILEPATH, disable_existing_loggers=True)
logger = logging.getLogger(__name__)

SUBSAMPLE = 3
K = 15
COLOUR_GREEN = (0, 200, 0)
NUM_GESTURES = 5
NUM_SAMPLES = 3

OVERWRITE_EXISTING = False
USE_EXISTING_DATA = True
SAMPLE_RATE = 200

GESTURE_NAMES = ['REST', 'FIST', 'EXTENDED PALM', 'WRIST FLEXION', 'WRIST EXTENSION']
EMG_MODE = emg_mode.PREPROCESSED

SAMPLE_DURATION = 3

training_data_dir = Path('data')

def normalise_signal(emg_signal):
    scalar = MinMaxScaler(feature_range=(-1, 1))
    normalised_signal = scalar.fit_transform(emg_signal)

    return normalised_signal

def filter_signal(emg_signal):
    # cut-off frequency of the filter
    fc = 5

    # normalize the frequency
    w = fc / (SAMPLE_RATE / 2)
    b, a = butter(4, w, btype='lowpass', analog=False)

    return filtfilt(b, a, emg_signal, padlen=0)

def rectify_signal(emg_signal):
    return abs(emg_signal)

def process_signal(emg_signal):
    normalised_signal = normalise_signal(emg_signal)
    filtered_signal = filter_signal(normalised_signal)
    rectified_signal = rectify_signal(filtered_signal)

    return rectified_signal

def collect_data(gesture, training_data_filepath):
    myo_sensor = Myo(mode=EMG_MODE)
    myo_sensor.connect()

    myo_data = []

    # callable function to save EMG
    def add_to_queue(emg, movement):
        myo_data.append(emg)
    myo_sensor.add_emg_handler(add_to_queue)

    # callable function to display battery level
    def print_battery(bat):
        print("Battery level:", bat)
    myo_sensor.add_battery_handler(print_battery)

    # set MYO LEDs
    myo_sensor.set_leds([0, 128, 0], [0, 128, 0])

    # Vibrate MYO device to know it connected
    myo_sensor.vibrate(1)

    logger.info(f"--- Collecting EMG data for gesture {gesture} ---")

    # Start collecting data.
    start_time = time.time()

    collect_emg = True
    while collect_emg:
        if time.time() - start_time < SAMPLE_DURATION:
            myo_sensor.run()
        else:
            collect_emg = False
            end_time = time.time() - start_time
            logger.info(f"--- Finished collecting EMG data for gesture {gesture} ---")
            logger.info(f"{len(myo_data)} frames collected in {end_time} seconds")

            # create dataframe to store EMG signals
            emg_df = pd.DataFrame(myo_data)
            logger.info(f"EMG: \n{emg_df}")

            emg_df.to_csv(training_data_filepath, index=False, mode='a')
            logger.info(f"Saved EMG sample for gesture {gesture} at {training_data_filepath}")

def get_training_data():
    training_data = []
    training_labels = []

    # read in each gesture file
    for gesture_num in range(NUM_GESTURES):
        # determine filepath of gesture training data
        training_data_filename = Path(f'training_gesture_{gesture_num}.dat')
        gesture_data_filepath = training_data_dir / training_data_filename

        # read training data file for gesture
        emg_df = pd.read_csv(gesture_data_filepath, index_col=0)
        emg_array = emg_df.to_numpy()
        emg_labels = np.full((len(emg_array)), gesture_num)

        training_data.append(emg_array)
        training_labels.append(emg_labels)

    training_data_stacked = np.vstack(training_data)
    training_labels_stacked = np.hstack(training_labels)
    return training_data_stacked, training_labels_stacked

def save_model(model):
    model_filename = "trained_model.pkl"
    with open(model_filename, 'wb') as file:
        pickle.dump(model, file)

def load_model():
    model_filename = "trained_model.pkl"
    with open(model_filename, 'rb') as file:
        model = pickle.load(file)
    return model

class Classifier(object):
    """
    A wrapper for nearest-neighbor classifier that stores training data in vals0, ..., vals9.dat.
    """
    def __init__(self, name="EMG Classifier", color=COLOUR_GREEN):
        # Add some identifiers to the classifier to identify what model was used in different screenshots
        self.name = name
        self.color = color

        # check if training files have been created
        for gesture_num in range(NUM_GESTURES):
            training_data_filename = Path(f'training_gesture_{gesture_num}.dat')
            training_data_filepath = training_data_dir / training_data_filename

            # check if training data for gesture exists
            if training_data_filepath.exists():
                logger.info(f"Training file {training_data_filename} exists")

                # if file exists clear contents
                if OVERWRITE_EXISTING:
                    training_data_filepath.unlink()
                    training_data_filepath.touch()
            else:
                # if no files created, create them for each gesture
                training_data_filepath.touch()
                logger.info(f"Created training file {training_data_filename} exists")

        # determine if we use existing training data or get new training data
        if not USE_EXISTING_DATA:
            # prompt user for signal for each gesture
            logger.info("Perform each gesture 3 times")
            for gesture_num in range(NUM_GESTURES):
                # determine filepath of gesture training data
                training_data_filename = Path(f'training_gesture_{gesture_num}.dat')
                gesture_data_filepath = training_data_dir / training_data_filename

                # determine gesture to perform
                gesture = GESTURE_NAMES[gesture_num]

                # collect EMG samples for gesture
                for sample_num in range(1, NUM_SAMPLES + 1):
                    logger.info(f"Perform gesture: {gesture} - sample {sample_num}")
                    while True:
                        collect_data(gesture, gesture_data_filepath)
                        break
                logger.info(f"Collected samples for gesture: {gesture}\n")

            # process and clean signal
            for gesture_num in range(NUM_GESTURES):
                # determine filepath of gesture training data
                training_data_filename = Path(f'training_gesture_{gesture_num}.dat')
                gesture_data_filepath = training_data_dir / training_data_filename

                # determine gesture to perform
                gesture = GESTURE_NAMES[gesture_num]

                # read training data file for gesture
                emg_df = pd.read_csv(gesture_data_filepath)

                # process signals
                process_signal(emg_df)
                logger.info(f"Processed training data for gesture: {gesture}")

                # save process signal to dat file
                emg_df.to_csv(gesture_data_filepath, index=False)

        # get training data for model
        training_data, training_labels = get_training_data()

        # TODO calculate features?

        # split data into train and test datasets
        x_train, x_test, y_train, y_test = train_test_split(training_data, training_labels, shuffle=True, test_size=0.3, random_state=0)

        # perform dimensionality reduction
        logger.info("Performing dimensionality reduction")
        lda = LinearDiscriminantAnalysis()
        x_train = lda.fit_transform(x_train, y_train)
        x_test = lda.transform(x_test)

        # train SVM model using training data - TODO use my own model if this works ok
        logger.info("Training model")

        # classifier = svm.SVC(kernel='rbf')
        classifier = RandomForestClassifier(n_estimators=3, random_state=0)

        classifier.fit(x_train, y_train)
        save_model(classifier)

        # run baseline predictions
        logger.info("Running predictions with trained model")
        y_pred = classifier.predict(x_test)

        classifier_accuracy = metrics.accuracy_score(y_test, y_pred) * 100
        classifier_precision = metrics.precision_score(y_test, y_pred, average='micro')
        classifier_recall = metrics.recall_score(y_test, y_pred, average='micro')
        classifier_f1 = metrics.f1_score(y_test, y_pred, average='micro')

        logger.info("+======================+")
        logger.info("| SVM baseline metrics |")
        logger.info("+----------------------+")
        logger.info(f"| Accuracy: {classifier_accuracy:.3f}%")
        logger.info(f"| Precision: {classifier_precision:.3f}")
        logger.info(f"| Recall: {classifier_recall:.3f}")
        logger.info(f"| F1 Score: {classifier_f1:.3f}")
        logger.info("+======================+")


    def prompt_training_data(self):
        pass

    def process_data(self):
        pass

    def save_training_data(self):
        pass

    def train_model(self):
        pass

    def save_model(self):
        pass

    def run_predictions(self):
        pass

    """
    old code
    """
    def store_data(self, cls, vals):
        with open('data/vals%d.dat' % cls, 'ab') as f:
            f.write(pack('8H', *vals))

        self.train(np.vstack([self.X, vals]), np.hstack([self.Y, [cls]]))

    def read_data(self):
        X = []
        Y = []
        for i in range(10):
            X.append(np.fromfile('data/vals%d.dat' % i, dtype=np.uint16).reshape((-1, 8)))
            Y.append(i + np.zeros(X[-1].shape[0]))

        self.train(np.vstack(X), np.hstack(Y))

    def delete_data(self):
        for i in range(10):
            with open('data/vals%d.dat' % i, 'wb') as f: pass
        self.read_data()

    def train(self, X, Y):
        self.X = X
        self.Y = Y
        self.model = None

    def nearest(self, d):
        dists = ((self.X - d) ** 2).sum(1)
        ind = dists.argmin()
        return self.Y[ind]

    def classify(self, d):
        if self.X.shape[0] < K * SUBSAMPLE: return 0
        return self.nearest(d)


class MyoClassifier(Myo):
    """
    Adds higher-level pose classification and handling onto Myo.
    """
    def __init__(self, cls, tty=None, mode=emg_mode.PREPROCESSED, hist_len=25):
        Myo.__init__(self, tty, mode=mode)
        # Add a classifier
        self.cls = cls
        self.hist_len = hist_len
        self.history = deque([0] * self.hist_len, self.hist_len)
        self.history_cnt = Counter(self.history)
        self.add_emg_handler(self.emg_handler)
        self.last_pose = None

        self.pose_handlers = []

    def emg_handler(self, emg, moving):
        y = self.cls.classify(emg)
        self.history_cnt[self.history[0]] -= 1
        self.history_cnt[y] += 1
        self.history.append(y)

        r, n = self.history_cnt.most_common(1)[0]
        if self.last_pose is None or (n > self.history_cnt[self.last_pose] + 5 and n > self.hist_len / 2):
            self.on_raw_pose(r)
            self.last_pose = r

    def add_raw_pose_handler(self, h):
        self.pose_handlers.append(h)

    def on_raw_pose(self, pose):
        for h in self.pose_handlers:
            h(pose)

    def run_gui(self, hnd, scr, font, w, h):
        # Handle keypresses
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                raise KeyboardInterrupt()
            elif ev.type == KEYDOWN:
                if K_0 <= ev.key <= K_9:
                    # Labelling using row of numbers
                    hnd.recording = ev.key - K_0
                elif K_KP0 <= ev.key <= K_KP9:
                    # Labelling using Keypad
                    hnd.recording = ev.key - K_KP0
                elif ev.unicode == 'r':
                    hnd.cl.read_data()
                elif ev.unicode == 'e':
                    print("Pressed e, erasing local data")
                    self.cls.delete_data()
            elif ev.type == KEYUP:
                if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
                    # Don't record incoming data
                    hnd.recording = -1

        # Plotting
        scr.fill((0, 0, 0), (0, 0, w, h))
        r = self.history_cnt.most_common(1)[0][0]

        for i in range(10):
            x = 0
            y = 0 + 30 * i

            # Set the barplot color
            clr = self.cls.color if i == r else (255, 255, 255)

            txt = font.render('%5d' % (self.cls.Y == i).sum(), True, (255, 255, 255))
            scr.blit(txt, (x + 20, y))

            txt = font.render('%d' % i, True, clr)
            scr.blit(txt, (x + 110, y))

            # Plot the barchart plot
            scr.fill((0, 0, 0), (x + 130, y + txt.get_height() / 2 - 10, len(self.history) * 20, 20))
            scr.fill(clr, (x + 130, y + txt.get_height() / 2 - 10, self.history_cnt[i] * 20, 20))

        pygame.display.flip()

def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)

def unpack(fmt, *args):
    return struct.unpack('<' + fmt, *args)

def text(scr, font, txt, pos, clr=(255, 255, 255)):
    scr.blit(font.render(txt, True, clr), pos)

class EMGHandler(object):
    def __init__(self, m):
        self.recording = -1
        self.m = m
        self.emg = (0,) * 8

    def __call__(self, emg, moving):
        self.emg = emg
        if self.recording >= 0:
            self.m.cls.store_data(self.recording, emg)

class Live_Classifier(Classifier):
    """
    General class for all Sklearn classifiers

    Expects something you can call .fit and .predict on
    """
    def __init__(self, classifier, name="Live Classifier", color=(0, 55, 175)):
        self.model = classifier
        Classifier.__init__(self, name=name, color=color)

    def train(self, X, Y):
        self.X = X
        self.Y = Y

        if self.X.shape[0] > 0 and self.Y.shape[0] > 0:
            self.model.fit(self.X, self.Y)

    def classify(self, emg):
        if self.X.shape[0] == 0 or self.model == None:
            # We have no data or model, return 0
            return 0

        x = np.array(emg).reshape(1, -1)
        pred = self.model.predict(x)
        return int(pred[0])


if __name__ == '__main__':
    # pygame.init()
    # w, h = 800, 320
    # scr = pygame.display.set_mode((w, h))
    # font = pygame.font.Font(None, 30)
    #
    # m = MyoClassifier(Classifier())
    # hnd = EMGHandler(m)
    # m.add_emg_handler(hnd)
    # m.connect()
    #
    # m.add_raw_pose_handler(print)
    #
    # # Set Myo LED color to model color
    # m.set_leds(m.cls.color, m.cls.color)
    #
    # # Set pygame window name
    # pygame.display.set_caption(m.cls.name)
    #
    # try:
    #     while True:
    #         m.run()
    #         m.run_gui(hnd, scr, font, w, h)
    #
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     m.disconnect()
    #     print()
    #     pygame.quit()
    m = MyoClassifier(Classifier())
