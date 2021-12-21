"""
Can plot EMG data in 2 different ways
change DRAW_LINES to try each.
Press Ctrl + C in the terminal to exit
"""

import multiprocessing
import logging.config
import pathlib
import pygame
from pyomyo import Myo
from pyomyo import emg_mode

LOGGING_CONF_FILEPATH = pathlib.Path(__file__).parent / 'logging.conf'
logging.config.fileConfig(LOGGING_CONF_FILEPATH, disable_existing_loggers=True)
logger = logging.getLogger(__name__)

# ------------ Myo Setup ---------------
thread_queue = multiprocessing.Queue()
PLOT_WIDTH = 800
PLOT_HEIGHT = 600

# -------- Plotting variables ----------
last_vals = None
DRAW_LINES = True

def worker(q):
    """
    Function for the worker process to perform
    :param q: multiprocessing queue for the thread to add captured EMG data to
    """
    # connect to MYO device
    m = Myo(mode=emg_mode.PREPROCESSED)
    m.connect()

    def add_to_queue(emg):
        q.put(emg)

    m.add_emg_handler(add_to_queue)

    def print_battery(bat):
        logger.debug("Battery level:", bat)

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
    global last_vals
    if last_vals is None:
        last_vals = vals
        return

    D = 5
    scr.scroll(-D)
    scr.fill((0, 0, 0), (PLOT_WIDTH - D, 0, PLOT_WIDTH, PLOT_HEIGHT))
    for i, (u, v) in enumerate(zip(last_vals, vals)):
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
    last_vals = vals


# -------- Main program code -----------
if __name__ == "__main__":
    thread_process = multiprocessing.Process(target=worker, args=(thread_queue,))
    thread_process.start()

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
        quit()
