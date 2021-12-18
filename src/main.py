import multiprocessing
import time

import pandas as pd
import pygame

from src.modes import EMGMode
from src.myo import Myo

SECONDS = 10
w, h = 800, 600
q = multiprocessing.Queue()

last_vals = None
def plot(scr, vals):
    DRAW_LINES = True

    global last_vals
    if last_vals is None:
        last_vals = vals
        return

    D = 5
    scr.scroll(-D)
    scr.fill((0, 0, 0), (w - D, 0, w, h))
    for i, (u, v) in enumerate(zip(last_vals, vals)):
        if DRAW_LINES:
            pygame.draw.line(scr, (0, 255, 0),
                             (w - D, int(h / 9 * (i + 1 - u))),
                             (w, int(h / 9 * (i + 1 - v))))
            pygame.draw.line(scr, (255, 255, 255),
                             (w - D, int(h / 9 * (i + 1))),
                             (w, int(h / 9 * (i + 1))))
        else:
            c = int(255 * max(0, min(1, v)))
            scr.fill((c, c, c), (w - D, i * h / 8, D, (i + 1) * h / 8 - i * h / 8))

    pygame.display.flip()
    last_vals = vals

def plot_emg():
    scr = pygame.display.set_mode((w, h))
    try:
        while True:
            # Handle pygame events to keep the window responding
            pygame.event.pump()
            # Get the emg data and plot it
            while not (q.empty()):
                emg = list(q.get())
                plot(scr, [e / 500. for e in emg])
                print(emg)
    except KeyboardInterrupt:
        print("Quitting")
        pygame.quit()
        quit()


if __name__ == '__main__':
    """
    From the data collector example
    """
    myo = Myo(mode=EMGMode.PREPROCESSED)
    myo.connect()

    myo_data = []

    def add_to_queue(emg, movement):
        myo_data.append(emg)

    myo.add_emg_handler(add_to_queue)

    def print_battery(bat):
        print("Battery level:", bat)

    myo.add_battery_handler(print_battery)

    # Its go time
    myo.set_leds([0, 128, 0], [0, 128, 0])
    # Vibrate to know we connected okay
    myo.vibrate(1)

    print("Data Worker started to collect")
    # Start collecing data.
    start_time = time.time()

    while True:
        if time.time() - start_time < SECONDS:
            myo.run()
        else:
            collect = False
            collection_time = time.time() - start_time
            print("Finished collecting.")
            print(f"Collection time: {collection_time}")
            print(len(myo_data), "frames collected")

            # Add columns and save to df
            myo_cols = ["Channel_1", "Channel_2", "Channel_3", "Channel_4", "Channel_5", "Channel_6", "Channel_7",
                        "Channel_8"]
            myo_df = pd.DataFrame(myo_data, columns=myo_cols)
            plot_emg()

            # myo_df.to_csv(filepath, index=False)
            # print("CSV Saved at: ", filepath)
