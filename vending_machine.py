import logging
from logging import config as log_config
import csv
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from arduino import Arduino
from client import OfflineClient as Client

log_config.fileConfig("logging.ini")

logger = logging.getLogger('Main')


class PrintObserver(CardObserver):
    def __init__(self):
        logger.debug('Initializing Arduino')
        self.arduino = Arduino()

        logger.debug('Initializing API')
        self.client = Client()

        reader = csv.reader(open('prices.csv', 'r'))
        logger.debug('Loading price table')
        self.price_table = {}
        for row in reader:
            k, v = row
            self.price_table[k] = float(v)
        logger.debug('Price table loaded: %s', self.price_table)
        super().__init__()

    def update(self, observable, actions):
        logger.debug('Received card update\nobservable: %s\nactions:%s', observable, actions)
        addedcards, removedcards = actions

        for card in addedcards:  # Detectou cartão inserido
            self.arduino.send('E')
            hash_RA = toHexString(card.atr)
            logger.info("Card inserted: %s", hash_RA)
            balance = self.client.get_balance(hash_RA)
            logger.info("Balance: %s", balance)

            if balance is None:
                logger.debug('User is not registered')
                self.arduino.send('A')
            else:
                self.arduino.send(balance)
                logger.debug('Waiting for user selection')
                selection = self.arduino.get()
                logger.debug('User selected %s', selection)

                if selection in self.price_table:
                    self.arduino.send('F')
                    price = self.price_table[selection]
                    logger.debug('Selection priced at %s', price)
                    purchase = self.client.buy(hash_RA, price)

                    if purchase is True:
                        self.arduino.send('B')
                    else:
                        logger.debug('Purchase failed: %s', purchase)
                        self.arduino.send('C')  # Erro na compra
                else:
                    logger.debug('Invalid selection')
                    self.arduino.send('D')
        for card in removedcards:
            hash_RA = toHexString(card.atr)
            logger.info('Card removed: %s', hash_RA)
            self.arduino.send('D')


if __name__ == '__main__':
    logger.debug('Initializing card monitor')
    cardmonitor = CardMonitor()

    logger.debug('Initializing card observer')
    cardobserver = PrintObserver()

    logger.debug('Adding card observer as listener')
    cardmonitor.addObserver(cardobserver)
    logger.info('Card listener initialized. Waiting for input')

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.debug('Removing card listener')
        cardmonitor.deleteObserver(cardobserver)
        logger.info('Exiting. Bye!')
        exit()
