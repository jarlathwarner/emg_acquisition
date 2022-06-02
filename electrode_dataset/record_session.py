import time
from random import randrange

import pygame
from matplotlib import pyplot as plt

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

title_text_rect = title_text.get_rect()
title_text_rect.center = (screen_x // 2, 50)

changing_text_rect = changing_text.get_rect()
changing_text_rect.center = (screen_x // 2, screen_y // 2)

done = False

start_ticks = pygame.time.get_ticks()
i = 1

num_gesture_recordings = 3
gesture_duration_secs = 3

electrode_sensor = ElectrodeSensors()

while not done:
    # display the elapsed time
    clock.tick(1)
    elapsed_time = int((pygame.time.get_ticks() - start_ticks) / 1000)

    if elapsed_time < gesture_duration_secs:
        changing_text = font.render(f"Relax", True, green)
    else:
        gesture_recorded = False

        # get recording
        changing_text = font.render(f"Perform fist #{i}", True, green)
        electrode_sensor.record_data()
        i += 1

        if i > num_gesture_recordings:
            gesture_recorded = True
            i = 1

        # reset recording state
        if gesture_recorded:
            start_ticks = pygame.time.get_ticks()

            sensor_data_matrix = electrode_sensor.get_numpy_array()

            # plot the data
            plt.plot(sensor_data_matrix)
            plt.xlabel('Time')
            plt.ylabel('Sensor readings')
            plt.title('Sensor readings vs Time')
            plt.show()

    # fill the screen with white colour
    screen.fill(white)

    # copy text to display rectangles
    screen.blit(title_text, title_text_rect)
    screen.blit(changing_text, changing_text_rect)

    # keep checking if quit event has been entered
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # draw surface object to screen
    pygame.display.update()

