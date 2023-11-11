from bipwallet.utils import *
from requests import get as get_requests
import random
from bit import PrivateKey
import requests
from decimal import Decimal
from bipwallet import wallet
import sys
sys.path.append("../..")
from constants import SEED


class MyWallet:

    def __init__(self, adress=None, index=None):
        self.seed = SEED
        self.address_accum = '17ya3bCpPioyPH8kAyFkEDBUqdjF6wwPxo'
        self.address = None
        self.index_address = None
        self.wif = None
        self.balance = 0.0
        if adress and index:
            self.address = adress
            self.index_address = index
            self.wif = self.get_wif(self.index_address)
        else:
            self.address, self.index_address = self.get_random_adress()

    def update_balance(self):
        self.balance = self.get_balance_wallet(self.address)

    def get_random_adress(self):
        random.seed(version=2)
        index = random.randint(1, 30000)
        return self.gen_address(index), index

    def get_wif(self, index):
        master_key = HDPrivateKey.master_key_from_mnemonic(self.seed)
        rootkeys_wif = HDKey.from_path(master_key, f"m/44'/0'/0'/0/{index}")[-1]
        xprivatekey = str(rootkeys_wif.to_b58check())
        wif = Wallet.deserialize(xprivatekey, network='BTC').export_to_wif()
        return str(wif)

    def gen_address(self, index):
        master_key = HDPrivateKey.master_key_from_mnemonic(self.seed)
        root_keys = HDKey.from_path(master_key, "m/44'/0'/0'/0")[-1].public_key.to_b58check()
        xpublic_key = str(root_keys)
        address = Wallet.deserialize(xpublic_key, network='BTC').get_child(index, is_prime=False).to_address()
        return address

    def get_balance_wallet(self, address):
        url = f'https://blockchain.info/rawaddr/{address}'
        x = get_requests(url)
        if x.status_code == 429:
            return 0.0
        wallet = x.json()
        balance_str = wallet['final_balance']
        if balance_str:
            return Decimal(balance_str)
        else:
            return 0.0

    def transfer_money_wallet(self, wif_private, sum):
        """return true - Transaction Submitted"""

        my_key = PrivateKey(wif=wif_private)  # 'L46ixenNSu8Bqk899ZrH8Y96t8DHqJ1ZyxzQBGFTbh38rLHLaPoY')
        money = sum
        wallet = self.address_accum
        fee = 0.0
        tx_hash = my_key.create_transaction([(wallet, money - fee, 'btc')], fee=fee, absolute_fee=True)
        url = 'https://blockchain.info/pushtx'
        x = requests.post(url, data={'tx': tx_hash})
        return 'Transaction Submitted' in x.text

    def get_string_wallet_index(self):
        return str(self.address)

