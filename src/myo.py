import re
from utilities import unpack

from serial.tools.list_ports_linux import comports

from Bt import BT
from packet import multiord
from utilities import pack

class Myo(object):
    def __init__(self, mode=1):
        myo_mode = 1

        # find myo dongle
        tty = self.detect_tty()

        # check if we have found the myo dongle
        if tty is None:
            raise ValueError('Myo dongle not found!')

        self.bt = BT(tty)
        self.conn = None
        self.emg_handlers = []

        # inertial measurement unit - measures and reports a body's specific force, angular rate
        self.imu_handlers = []
        self.arm_handlers = []
        self.pose_handlers = []
        self.battery_handlers = []
        self.mode = myo_mode

    def run(self):
        self.bt.recv_packet()

    def vibrate(self, length):
        if length in range(1, 4):
            # first byte tells it to vibrate; purpose of second byte is unknown (payload size?)
            self.write_attr(0x19, pack('3B', 3, 1, length))

    def set_leds(self, logo, line):
        self.write_attr(0x19, pack('8B', 6, 6, *(logo + line)))

    def add_emg_handler(self, h):
        self.emg_handlers.append(h)

    def add_battery_handler(self, h):
        self.battery_handlers.append(h)

    def read_attr(self, attr):
        if self.conn is not None:
            return self.bt.read_attr(self.conn, attr)
        return None

    def write_attr(self, attr, val):
        if self.conn is not None:
            self.bt.write_attr(self.conn, attr, val)

    def detect_tty(self):
        # /dev/ttyACM0 is a USB communication device
        for p in comports():
            if re.search(r'PID=2458:0*1', p[2]):
                print('using device:', p[0])
                return p[0]
        return None

    def connect(self, addr=None):
        # stop everything from before
        self.bt.end_scan()
        self.bt.disconnect(0)
        self.bt.disconnect(1)
        self.bt.disconnect(2)

        # start new scan
        if addr is None:
            print("Scanning")
            self.bt.discover()
            while True:
                packet = self.bt.recv_packet()
                print("scan response: ", packet)

                if packet.payload.endswith(b'\x06\x42\x48\x12\x4A\x7F\x2C\x48\x47\xB9\xDE\x04\xA9\x01\x00\x06\xD5'):
                    addr = list(multiord(packet.payload[2:8]))
                    break
            self.bt.end_scan()

        # connect and wait for status event
        conn_pkt = self.bt.connect(addr)
        self.conn = multiord(conn_pkt.payload)[-1]
        self.bt.wait_event(3, 0)

        # get firmware version
        firmware = self.read_attr(0x17)
        _, _, _, _, v0, v1, v2, v3 = unpack('BHBBHHHH', firmware.payload)
        print('firmware version: %d.%d.%d.%d' % (v0, v1, v2, v3))


    def disconnect(self):
        if self.conn is not None:
            self.bt.disconnect(self.conn)

    def power_off(self):
        '''
        function to power off the Myo Armband (actually, according to the official BLE specification,
        the 0x04 command puts the Myo into deep sleep, there is no way to completely turn the device off).
        '''
        self.write_attr(0x19, b'\x04\x00')
