"""
Can plot EMG data in 2 different ways
change DRAW_LINES to try each.
Press Ctrl + C in the terminal to exit
"""

import logging.config
import multiprocessing
import pathlib

import pygame
# from pyomyo import Myo
# from pyomyo import emg_mode
from myo_interface import Myo
from myo_interface import emg_mode
# from myo import Myo
# from modes import EMGMode

LOGGING_CONF_FILEPATH = pathlib.Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(LOGGING_CONF_FILEPATH, disable_existing_loggers=True)
logger = logging.getLogger(__name__)

# ------------ Myo Setup ---------------
thread_queue = multiprocessing.Queue()
PLOT_WIDTH = 1500
PLOT_HEIGHT = 1200

# -------- Plotting variables ----------
previous_emg_data = None
DRAW_LINES = True

def power_off_myo():
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.power_off()
    logger.info("MYO device powered off")

def worker(q):
    """
    Function for the worker process to perform
    :param q: multiprocessing queue for the thread to add captured EMG data to
    """
    # connect to MYO device
    m = Myo(mode=emg_mode.PREPROCESSED)
    # m = Myo(mode=EMGMode.PREPROCESSED)
    m.connect()

    def add_to_queue(emg, movement):
        q.put(emg)

    m.add_emg_handler(add_to_queue)

    def print_battery(bat):
        logger.debug(f"Battery level: {bat}")

    m.add_battery_handler(print_battery)

    # Orange logo and bar LEDs
    m.set_leds([128, 0, 0], [128, 0, 0])

    # Vibrate to know we connected okay
    m.vibrate(1)

    # retrieve data from MYO device
    while True:
        m.run()


def plot(scr, vals):
    """
    Code for plotting EMG data
    :param scr: display to plot to
    :param vals: values to plot
    """
    global previous_emg_data
    if previous_emg_data is None:
        previous_emg_data = vals
        return

    D = 5
    scr.scroll(-D)
    scr.fill((0, 0, 0), (PLOT_WIDTH - D, 0, PLOT_WIDTH, PLOT_HEIGHT))
    for i, (u, v) in enumerate(zip(previous_emg_data, vals)):
        if DRAW_LINES:
            pygame.draw.line(scr, (0, 255, 0),
                             (PLOT_WIDTH - D, int(PLOT_HEIGHT / 9 * (i + 1 - u))),
                             (PLOT_WIDTH, int(PLOT_HEIGHT / 9 * (i + 1 - v))))
            pygame.draw.line(scr, (255, 255, 255),
                             (PLOT_WIDTH - D, int(PLOT_HEIGHT / 9 * (i + 1))),
                             (PLOT_WIDTH, int(PLOT_HEIGHT / 9 * (i + 1))))
        else:
            c = int(255 * max(0, min(1, v)))
            scr.fill((c, c, c), (PLOT_WIDTH - D, i * PLOT_HEIGHT / 8, D, (i + 1) * PLOT_HEIGHT / 8 - i * PLOT_HEIGHT / 8))

    pygame.display.flip()
    previous_emg_data = vals

def display_live_emg():
    scr = pygame.display.set_mode((PLOT_WIDTH, PLOT_HEIGHT))

    try:
        while True:
            # Handle pygame events to keep the window responding
            pygame.event.pump()

            # Get the emg data and plot it
            while not (thread_queue.empty()):
                emg_data = list(thread_queue.get())
                plot(scr, [e / 500. for e in emg_data])
                logger.debug(f"EMG Data: {emg_data}")
    except KeyboardInterrupt:
        logger.info("Exiting")
        pygame.quit()


# -------- Main program code -----------
if __name__ == "__main__":
    thread_process = multiprocessing.Process(target=worker, args=(thread_queue,))
    thread_process.start()

    display_live_emg()

    power_off_myo()
    logger.debug("Exit")
