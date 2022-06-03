import time
from random import randrange

import numpy as np
import pygame
from matplotlib import pyplot as plt

from constants import DATA_FILEPATH
from constants import NUM_GESTURE_RECORDINGS
from electrode_sensor import ElectrodeSensors

pygame.init()
white = (255, 255, 255)
blue = (0, 0, 128)
green = (0, 255, 0)

screen_x = 500
screen_y = 500
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption('Recording')

screen_rect = screen.get_rect()

font = pygame.font.Font(None, 45)
clock = pygame.time.Clock()

title_text = font.render('EMG recording session', True, blue)
changing_text = font.render(f"Seconds: ---", True, green)
counter_text = font.render(f"0 seconds", True, green)

title_text_rect = title_text.get_rect()
title_text_rect.center = (screen_x // 2, 50)

changing_text_rect = changing_text.get_rect()
changing_text_rect.center = (screen_x // 2, screen_y // 2)

counter_text_rect = counter_text.get_rect()
counter_text_rect.center = ((screen_x // 3) + 10, screen_y // 2)

done = False

start_ticks = pygame.time.get_ticks()
gesture_recording_num = 1


gestures = ['Fist']
gesture_idx = 0
counter = 3

electrode_sensor = ElectrodeSensors()
all_gestures_recorded = False
record_rest = False

while not done:
    # display the elapsed time
    clock.tick(1)
    elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)

    # check whether to record gesture or relax
    if record_rest:
        changing_text = font.render(f"Relax your arm", True, green)
        electrode_sensor.record_data(0)
        record_rest = False
    else:
        # get recording of gesture
        gesture = gestures[gesture_idx]
        changing_text = font.render(f"#{gesture_recording_num} - Perform {gesture} and hold", True, green)
        electrode_sensor.record_data(gesture_idx + 1)

        gesture_recording_num += 1
        record_rest = True

    # check if we have got all recordings for a gesture
    if gesture_recording_num > NUM_GESTURE_RECORDINGS and not record_rest:
        gesture_recording_num = 1
        gesture_idx += 1

    # check if we have got all recordings for all gestures
    if gesture_idx >= len(gestures):
        all_gestures_recorded = True

        # reset starting time
        start_ticks = pygame.time.get_ticks()

        # get numpy array of recorded data
        sensor_data_matrix = electrode_sensor.get_sensor_data_array()
        dataset_matrix = electrode_sensor.get_dataset_array()
        electrode_sensor.reset_data()

        # plot the data
        plt.plot(sensor_data_matrix)
        plt.xlabel('Time')
        plt.ylabel('Sensor readings')
        plt.title('Sensor readings vs Time')
        plt.show()

        # save data to file
        matrix_filepath = DATA_FILEPATH.absolute() / 'sensor_data.npy'
        np.save(matrix_filepath, dataset_matrix)

    # fill the screen with white colour
    screen.fill(white)

    # copy text to display rectangles
    screen.blit(title_text, title_text_rect)
    screen.blit(changing_text, changing_text_rect)

    # check if all gestures have been recorded
    if all_gestures_recorded:
        done = True

    # keep checking if quit event has been entered
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # draw surface object to screen
    pygame.display.update()

