import pygame
from matplotlib import pyplot as plt

from constants import NUM_GESTURE_RECORDINGS
from electrode_dataset.constants import GESTURES_TO_PERFORM
from electrode_dataset.constants import NUM_GESTURES
from electrode_dataset.constants import NUM_RECORDING_REPETITIONS
from electrode_dataset.constants import SAMPLE_RATE
from electrode_dataset.dataset_config import DatasetManager
from electrode_sensor import ElectrodeSensors

pygame.init()

# colour variables
white = (255, 255, 255)
grey = (184, 184, 184)
blue = (0, 0, 128)
green = (13, 175, 19)
red = (219, 26, 46)
orange = (235, 125, 15)

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
gesture_changing_text = font.render(f"---", True, green)
gesture_text = font.render(f"Gestures to perform: []", True, red)
repetition_text = font.render(f"---", True, orange)

# position variables
title_text_rect = title_text.get_rect()
title_text_rect.center = (screen_x // 2, 50)

repetition_text_rect = repetition_text.get_rect()
repetition_text_rect.topleft = ((screen_x // 2) - (screen_x / 2) + 25, (screen_y // 2) - 100)

gesture_changing_text_rect = gesture_changing_text.get_rect()
gesture_changing_text_rect.topleft = ((screen_x // 2) - (screen_x / 2) + 25, screen_y // 2)

gesture_text_rect = gesture_text.get_rect()
gesture_text_rect.topleft = ((screen_x // 2) - (screen_x / 2) + 25, (screen_y // 2) - 50)

# recording variables
record_rest = True
recording_finished = False
done = False

gesture_idx = 0
gesture_recording_num = 1
repetition_id = 0
gestures_remaining = GESTURES_TO_PERFORM.copy()

# electrode sensor variables
electrode_sensor = ElectrodeSensors()
dataset_manager = DatasetManager()

while not done:
    # display the elapsed time
    clock.tick(1)
    elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)

    # update the text for which gestures are remaining
    gesture_text = font.render(f"Gestures remaining to perform: {gestures_remaining}", True, red)
    repetition_text = font.render(f"Recording repetition: {repetition_id + 1}", True, orange)

    ###
    # recording code
    ###
    if repetition_id < NUM_RECORDING_REPETITIONS:
        # check whether to record gesture or relax
        if record_rest:
            gesture_changing_text = font.render(f"Relax your arm", True, green)

            electrode_sensor.record_data(0)
            record_rest = False
        else:
            # get name of the next gesture to perform
            gesture = GESTURES_TO_PERFORM[gesture_idx]

            # print text on screen
            gesture_text_string = f"Recording #{gesture_recording_num}/{NUM_GESTURE_RECORDINGS} - Perform {gesture} and hold"
            gesture_changing_text = font.render(gesture_text_string, True, green)

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
            gesture_idx = 0
            repetition_id += 1
            if repetition_id < NUM_RECORDING_REPETITIONS:
                gestures_remaining = GESTURES_TO_PERFORM.copy()
                record_rest = True

            # reset starting time
            elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)
    else:
        # get numpy array of recorded data
        sensor_data_matrix = electrode_sensor.get_sensor_data_array()
        dataset_matrix = electrode_sensor.get_dataset_array()
        electrode_sensor.reset_data()

        # plot the data
        fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True)
        plt.subplot(3, 1, 1)
        plt.plot(sensor_data_matrix[:, 0])

        plt.subplot(3, 1, 2)
        plt.plot(sensor_data_matrix[:, 1])

        plt.subplot(3, 1, 3)
        plt.plot(sensor_data_matrix[:, 2])

        plt.ylabel('Sensor readings')
        plt.suptitle(f'Sensor readings - {NUM_GESTURES} gestures - {SAMPLE_RATE} sample rate')
        plt.show()

        # save data to file
        dataset_manager.save_data(dataset_matrix)
        recording_finished = True

    # fill the screen with white colour
    screen.fill(grey)

    # copy text to display rectangles
    screen.blit(title_text, title_text_rect)
    screen.blit(gesture_changing_text, gesture_changing_text_rect)
    screen.blit(repetition_text, repetition_text_rect)
    screen.blit(gesture_text, gesture_text_rect)

    # check if recording is done
    if recording_finished:
        done = True

    # keep checking if quit event has been entered
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # draw surface object to screen
    pygame.display.update()
    pygame.display.flip()
print("Quitting recording")
pygame.display.quit()
