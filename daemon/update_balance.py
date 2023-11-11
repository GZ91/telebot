from requests import get as get_requests
import sqlite3
from sqlite3 import Error
from time import sleep
from decimal import Decimal
import sys
sys.path.append("..")
from get_price_btc_dollars import RATE_ERROR

#Должна крутиться каждые 7-15 минут:обновление результатов платежей
#Cron */7  * * * * python update_balance.py

class Update_balance:
    def __init__(self):
        self.pathdb = '../data_balance.db'

    def get_balance_wallet(self, address):
        url = f'https://blockchain.info/rawaddr/{address}'
        x = get_requests(url)
        wallet = x.json()
        balance_str = wallet['final_balance']
        if balance_str:
            return Decimal(balance_str)
        else:
            return 0.0

    def execute_query(self, query):
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.pathdb, timeout=30)
            cursor = self.connection.cursor()
            try:
                cursor.execute(query)
                self.connection.commit()
                self.connection.close()
            except Error as e:
                print(f"The error '{e}' occurred")
        except Error as e:
            print(f"The error '{e}' occurred")


    def select_ret(self, select, dict=None):
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.pathdb, timeout=30)
            cursor = self.connection.cursor()
            if dict:
                cursor.execute(select, dict)
            else:
                cursor.execute(select)
            self.connection.commit()
            row = cursor.fetchall()
            self.connection.close()
            return row
        except Error as e:
            print(f"The error '{e}' occurred")
            return []




    def get_wallets_for_update_balance(self):
        return self.select_ret('''SELECT W.Key_Wallet, W.Balance, W.ID, Acc.Balance From AccBalance as Acc
        JOIN Wallets as W ON Acc.WalletID=W.ID ''')


    def conversion_usd(self, receipt):
        bitcoin_api_url = 'https://blockchain.info/ticker'
        response = get_requests(bitcoin_api_url)
        response_json = response.json()
        return float(Decimal(str(response_json['USD']['sell'])) * Decimal(str(receipt)) * Decimal(str(RATE_ERROR)))

    def set_balance_client(self, WalletID, receipt, old_balance_w, old_balance_c):
        receipt_dollars = self.conversion_usd(receipt)
        balance_c = Decimal(str(old_balance_c)) + Decimal(str(receipt_dollars))
        query = '''UPDATE AccBalance set Balance = %(receipt_dollars).2f, WalletID = NULL
                   WHERE WalletID = %(WalletID)d  ''' % {'receipt_dollars': balance_c, 'WalletID': WalletID}
        self.execute_query(query)

        w_balance =  Decimal(str(old_balance_w)) + Decimal(str(receipt))
        query = '''UPDATE Wallets set Balance = %(w_balance).8f
                           WHERE ID = %(WalletID)d''' % {'w_balance': w_balance, 'WalletID': WalletID}
        self.execute_query(query)


    def update(self):
        list_w = self.get_wallets_for_update_balance()
        for val_wallet in list_w:
            address = val_wallet[0]
            old_balance_w = val_wallet[1]
            WalletID = val_wallet[2]
            old_balance_c = val_wallet[3]
            balance = self.get_balance_wallet(address)
            receipt = (Decimal(str(balance))*Decimal('0.00000001')) - Decimal(str(old_balance_w))
            if receipt:
                self.set_balance_client(WalletID, receipt, old_balance_w, old_balance_c)
            sleep(7)#чтобы не приняли за DDoS



update_bal = Update_balance()
update_bal.update()