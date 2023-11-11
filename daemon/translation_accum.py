from bit import PrivateKey as PRIVATEKEY

import sqlite3
from sqlite3 import Error
from bipwallet.utils import *
import sys
from decimal import Decimal
sys.path.append("..")
from constants import SEED, WALLET_ACCUM, FEE
import requests
from time import sleep

def select_ret(select, dict=None):
    connection = None
    try:
        connection = sqlite3.connect('../data_balance.db', timeout=30)
        cursor = connection.cursor()
        if dict:
            cursor.execute(select, dict)
        else:
            cursor.execute(select)
        connection.commit()
        row = cursor.fetchall()
        connection.close()
        return row
    except Error as e:
        print(f"The error '{e}' occurred")
        return []

def execute_query(self, query):
    connection = None
    try:
        connection = sqlite3.connect('../data_balance.db', timeout=30)
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            self.connection.close()
        except Error as e:
            print(f"The error '{e}' occurred")
    except Error as e:
        print(f"The error '{e}' occurred")

def get_list_index():
    query = '''SELECT W.Wallet_index, W.Balance, W.ID, W.Key_Wallet From Wallets as W
        LEFT JOIN AccBalance as Acc ON Acc.WalletID=W.ID
        WHERE Busy = 1 and Acc.ID is NULL and W.Balance != 0.0'''
    return select_ret(query)

def get_wif(index):
    master_key = HDPrivateKey.master_key_from_mnemonic(SEED)
    rootkeys_wif = HDKey.from_path(master_key, f"m/44'/0'/0'/0/{index}")[-1]
    xprivatekey = str(rootkeys_wif.to_b58check())
    wif = Wallet.deserialize(xprivatekey, network='BTC').export_to_wif()
    return str(wif)

def get_list_wifs_balance():
    row = get_list_index()
    r_list = []
    for val in row:
        r_list.append([get_wif(val[0]), val[1], val[2], val[3]])
    return r_list

def update_wallet(id, balance):
    query = '''UPDATE Wallets set Balance = %(balance)f, Busy = 0 WHERE ID = %(ID)d''' % {'ID': id, 'balance': balance}
    select_ret(query)

def get_balance_wallet(address):
    url = f'https://blockchain.info/rawaddr/{address}'
    x = requests.get(url)
    wallet = x.json()
    balance_str = wallet['final_balance']
    if balance_str:
        return float(balance_str)
    else:
        return 0.0

def transactions():
    row = get_list_wifs_balance()
    for val in row:
        wif = str(val[0])
        my_key = PRIVATEKEY(wif=wif)
        sum = Decimal(str(val[1]))-(Decimal(FEE)*Decimal('0.00000001'))
        tx_hash = my_key.create_transaction([(WALLET_ACCUM, float(sum), 'btc')], fee=FEE, absolute_fee=True)
        url = 'https://blockchain.info/pushtx'
        x = requests.post(url, data={'tx': tx_hash})
        result = x.text
        if 'Transaction Submitted' in x.text:
            balance = get_balance_wallet(val[3])
            update_wallet(val[2], balance)
            sleep(7)#anti-check_ddos

transactions()

