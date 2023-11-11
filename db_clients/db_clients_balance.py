import sqlite3
from sqlite3 import Error
from .btc_wallet import WorkingWithAWallet
from datetime import datetime



class  DB_Client:
    def __init__(self):
        self.pathdb = 'data_balance.db'
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.pathdb, timeout=30)
        except Error as e:
            print(f"The error '{e}' occurred")
            return None

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")


    def insert_Client(self, TelId, username):
        sql = ''' INSERT INTO AccBalance(TelID, Username, Balance)
                      VALUES(%(TelID)s, "%(val_name)s", %(Value)f) ''' \
              % {'TelID': TelId, 'val_name': username, 'Value': 0.0}
        self.execute_query(sql)

    def select_ret(self, select, dict=None):
        cursor = self.connection.cursor()
        cursor.execute(select, dict)
        self.connection.commit()
        return cursor.fetchall()

    def new_value_and_get_id(self, select):
        cursor = self.connection.cursor()
        cursor.execute(select)
        cursor.execute("SELECT last_insert_rowid()")
        self.connection.commit()
        return cursor.fetchall()

    def welcome_client(self, TelId, username):
        rows = self.select_ret("SELECT ID FROM AccBalance WHERE TelID=:TelID", {"TelID": TelId})
        if not rows:
            self.insert_Client(TelId, username)
            return self.welcome_client(TelId, username)
        return rows[0][0]

    def get_balance(self, TelId):
        rows = self.select_ret("SELECT Balance FROM AccBalance WHERE TelID=:TelID", {"TelID": TelId})
        return rows[0][0]

    def add_wallet_in_client(self, TelId, Wallet_ID):
        self.execute_query('''update AccBalance set WalletID = "%(Wallet_ID)s" where TelID="%(TelID)s"'''\
                           %{'Wallet_ID': Wallet_ID, 'TelID': TelId})
        self.execute_query('''update Wallets set Busy = 1 where ID = %(Wallet_ID)d'''% {'Wallet_ID': Wallet_ID})

    def add_new_wallet_in_client(self, TelId, Wallet_Key, OldBalance, index):
        query = ''' INSERT INTO Wallets(Balance, Time, Busy, Key_Wallet, Wallet_index) VALUES(%(OldBalance)f, "%(TimeData)s", 1, "%(Key_Wallet)s", %(index)d)'''% {'OldBalance': OldBalance, 'TimeData': str(datetime.now()), 'Key_Wallet': Wallet_Key, 'index': index}
        rows = self.new_value_and_get_id(query)
        self.add_wallet_in_client(TelId, rows[0][0])

    def update_time_wallet(self, Key_Wallet):
        self.execute_query('''update Wallets set Time = "%(Time)s" where Key_Wallet = %(Key_Wallet)s'''% \
                           {'Key_Wallet': Key_Wallet, 'Time': str(datetime.now())})

    def get_wallet(self, TelId):
        rows = self.select_ret('''select Wal.ID, Wal.Key_Wallet
                                from AccBalance as Acc
                                left join Wallets as Wal on Acc.WalletID = Wal.ID
                                where Acc.TelID = :TelID
                                limit 1''', {"TelID": TelId})
        if not rows[0][0]:
            rows = self.select_ret('''select w.ID, w.Key_Wallet
                                    from Wallets as W
                                    where W.Busy = :Busy
                                    limit 1''', {"Busy": 0})
            if not len(rows):
                while True:
                    wallet = WorkingWithAWallet.MyWallet()
                    rows = self.select_ret('''select ID
                                    from Wallets as W
                                    where W.Key_Wallet = :Key_Wallet
                                    limit 1''', {"Key_Wallet": wallet.get_string_wallet_index()})
                    if not len(rows):
                        wallet.update_balance()
                        self.add_new_wallet_in_client(TelId,
                                                      wallet.get_string_wallet_index(),
                                                      wallet.balance,
                                                      wallet.index_address)
                        return wallet.address
                    del wallet
            else:
                self.add_wallet_in_client(TelId, rows[0][0])
                self.update_time_wallet(rows[0][1])
                return rows[0][1]
        else:
            self.update_time_wallet(rows[0][1])
            return rows[0][1]



    def __del__(self):
        self.connection.close()





