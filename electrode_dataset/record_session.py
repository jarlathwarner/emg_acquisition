import numpy as np
import pygame
from matplotlib import pyplot as plt

from constants import DATA_FILEPATH
from constants import NUM_GESTURE_RECORDINGS
from electrode_sensor import ElectrodeSensors

pygame.init()

# colour variables
white = (255, 255, 255)
grey = (184, 184, 184)
blue = (0, 0, 128)
green = (13, 175, 19)
red = (219, 26, 46)

# window variables
screen_x = 1000
screen_y = 600
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption('Recording')

screen_rect = screen.get_rect()
font = pygame.font.Font(None, 45)

clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

# text variables
title_text = font.render('EMG recording session', True, blue)
changing_text = font.render(f"Seconds: ---", True, green)
gesture_text = font.render(f"Gestures to perform: []", True, red)

# position variables
title_text_rect = title_text.get_rect()
title_text_rect.center = (screen_x // 2, 50)

changing_text_rect = changing_text.get_rect()
changing_text_rect.topleft = ((screen_x // 2) - (screen_x / 2) + 25, screen_y // 2)

gesture_text_rect = gesture_text.get_rect()
gesture_text_rect.topleft = ((screen_x // 2) - (screen_x / 2) + 25, (screen_y // 2) - 50)

# recording variables
done = False
all_gestures_recorded = False
record_rest = False

gesture_idx = 0
gesture_recording_num = 1
gestures_to_perform = ['Fist', 'Extended Palm']
gestures_remaining = gestures_to_perform.copy()
num_gestures = len(gestures_to_perform)

# electrode sensor variables
electrode_sensor = ElectrodeSensors()

while not done:
    # display the elapsed time
    clock.tick(1)
    elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)

    # update the text for which gestures are remaining
    gesture_text = font.render(f"Gestures remaining to perform: {gestures_remaining}", True, red)

    ###
    # recording code
    ###
    # check whether to record gesture or relax
    if record_rest:
        changing_text = font.render(f"Relax your arm", True, green)

        electrode_sensor.record_data(0)
        record_rest = False
    else:
        # get name of the gesture to perform
        gesture = gestures_to_perform[gesture_idx]
        text_string = f"Recording #{gesture_recording_num}/{NUM_GESTURE_RECORDINGS} - Perform {gesture} and hold"
        changing_text = font.render(text_string, True, green)

        # get recording
        electrode_sensor.record_data(gesture_idx + 1)

        # update recording number counter
        gesture_recording_num += 1
        record_rest = True

    # check if we have got all recordings for a gesture
    if gesture_recording_num > NUM_GESTURE_RECORDINGS and not record_rest:
        gestures_remaining.pop(0)
        gesture_recording_num = 1
        gesture_idx += 1

    # check if we have got all recordings for all gestures
    if len(gestures_remaining) == 0:
        all_gestures_recorded = True

        # reset starting time
        elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)

        # get numpy array of recorded data
        sensor_data_matrix = electrode_sensor.get_sensor_data_array()
        dataset_matrix = electrode_sensor.get_dataset_array()
        electrode_sensor.reset_data()

        # plot the data
        plt.plot(sensor_data_matrix)
        plt.xlabel(f'Time - {elapsed_time}seconds')
        plt.ylabel('Sensor readings')
        plt.title('Sensor readings vs Time')
        plt.show()

        # save data to file
        matrix_filepath = DATA_FILEPATH.absolute() / f'dataset_{num_gestures}_gestures.npy'
        np.save(matrix_filepath, dataset_matrix)

    # fill the screen with white colour
    screen.fill(grey)

    # copy text to display rectangles
    screen.blit(title_text, title_text_rect)
    screen.blit(changing_text, changing_text_rect)
    screen.blit(gesture_text, gesture_text_rect)

    # check if all gestures have been recorded
    if all_gestures_recorded:
        done = True

    # keep checking if quit event has been entered
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # draw surface object to screen
    pygame.display.update()
    pygame.display.flip()

