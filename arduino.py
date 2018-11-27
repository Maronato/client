from time import sleep
from serial.serialutil import SerialException
import serial
import logging
import json


logger = logging.getLogger('Arduino')


class Arduino(object):
    def __init__(self, port='/dev/cu.usbmodem14201', baud_rate=9600, timeout=120):
        self.connected = False
        logger.debug('Opening connection')

        try:
            self.conn = serial.Serial(port, baud_rate, timeout=timeout)
            self.conn.open
            logger.debug('Waiting for connection')
            sleep(2)
            logger.info('Arduino connected')
            self.connected = True
        except SerialException:
            logger.exception('Failed to connect')

    def send(self, message):
        if not self.connected:
            logger.error('Not connected. Failed to send: %s', message)
            return

        if isinstance(message, str):
            message = message.encode()
        else:
            message = json.dumps(message).encode()

        logger.debug('Writing message: %s', message)
        self.conn.write(message)
        logger.debug('Message sent')

    def get(self):
        if not self.connected:
            logger.error('Not connected. Failed to read')
            return

        logger.debug('Reading message')
        try:
            message = self.conn.read().decode()
        except SerialException:
            logger.debug('Arduino returned no data')
            return
        logger.debug('Message read: %s', message)
        return message
