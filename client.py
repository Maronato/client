from time import sleep
from base64 import urlsafe_b64encode
import logging
import requests


logger = logging.getLogger('Client')


class BaseClient(object):
    def __init__(self):
        logger.info('Client Created')

    def get_balance(self, RA):
        """Get Balance

        Receives a RA and returns the user's balance.
        Returns None if the user is not registered
        """
        raise NotImplementedError('get_balance has to be implemented')

    def buy(self, RA, price):
        """Buy

        Receives a RA and a price and processes the purchase.
        Returns True if successful. Error string otherwise
        """
        raise NotImplementedError('buy has to be implemented')


class OnlineClient(BaseClient):
    def __init__(self, token='308aaa205f81deafedfe802f3c44229562621dc6'):
        self.url = 'https://vendingmachine075.herokuapp.com'
        self.token = token

        logger.debug('Creating API session to server\n%s\nWith token\n%s', self.url, self.token)
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Token ' + token})
        logger.info('Created API session')
        super().__init__()

    def get_balance(self, RA):
        """Get Balance

        Receives a RA and returns the user's balance.
        Returns None if the user is not registered
        """
        encoded_RA = urlsafe_b64encode(RA.encode()).decode()
        url = self.url + '/balance/' + encoded_RA
        logger.debug('Getting balance for RA: %s', RA)
        r = self.session.get(url)

        if r.status_code == requests.codes.ok:
            balance = r.json()['balance']
            logger.debug('Got balance: %s', balance)
            # Retorna valor na conta
            return round(balance, 2)

        logger.error('Unable to get balance. Code: %s', r.status_code)
        return None

    def buy(self, RA, price):
        """Buy

        Receives a RA and a price and processes the purchase.
        Returns True if successful. Error string otherwise
        """
        data = {
            'account': RA,
            'transaction': 'withdraw',
            'amount': price
        }
        logger.debug('Making purchase with parameters %s', data)
        url = self.url + '/transactions/'
        r = self.session.post(url, data=data)

        if r.status_code == requests.codes.created:
            logger.info('Purchase complete')
            return True

        error = r.json()
        logger.error('Unable to complete purchase. Code: %s Error: %s', r.status_code, error)

        if error.get('account', ['false'])[0] == 'account inválida':
            return 'Usuário não registrado'
        return list(error.values())[0][0]


class OfflineClient(BaseClient):
    """Offline client
    Offline version of the client. For demo only
    """
    base_balance = 9.80

    def __init__(self):
        self.balance_dict = {}
        logger.info('Created offline session')
        super().__init__()

    def get_balance(self, RA):
        """Get Balance

        Receives a RA and returns the user's balance.
        Returns None if the user is not registered
        """
        logger.debug('Getting offline balance for RA: %s', RA)
        if RA not in self.balance_dict:
            logger.debug('New RA')
            self.balance_dict[RA] = self.base_balance
        sleep(2)
        logger.debug('Got balance: %s', self.balance_dict[RA])
        return round(self.balance_dict[RA], 2)

    def buy(self, RA, price):
        """Buy

        Receives a RA and a price and processes the purchase.
        Returns True if successful. Error string otherwise
        """
        logger.debug('Making offline purchase of %s for RA: %s', price, RA)
        balance = self.get_balance(RA)

        if price > balance:
            # Not enough money
            logger.error('Insufficient balance')
            return False
        self.balance_dict[RA] -= price
        sleep(2)
        logger.info('Purchase complete')
        return True
