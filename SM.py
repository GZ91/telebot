#State Menu
# finite automaton
from get_price_btc_dollars import get_course_in_dollars
from db_clients.db_clients_balance import DB_Client
from db_clients import wrap as wrapdbc
import constants



SUPPORT = constants.TEXT_SUPPORT

def binary_search_smenu(array, element):
    mid = 0
    start = 0
    end = len(array)
    while (start <= end):
        mid = (start + end) // 2
        if element == array[mid-1].tel_id:
            return array[mid-1]
        if element < array[mid-1].tel_id:
            end = mid - 1
        else:
            start = mid + 1
    return None


class StateMenu:
    ZERO = 0
    GMENU = 1
    BALANCE = 2
    PRODUCT_CATALOG = 3
    PRE_PAY = 6
    PAY = 7
    EXIT = 8

    def __init__(self, TelID, username):
        self.STATE = self.ZERO
        self.dataTimePauseUpdateBalance = None
        self.tel_id = TelID
        wrapdbc.welcome_client(TelID, username)

    def __lt__(self, other):
        return self.tel_id < other.tel_id

    def get_button_balance(self, types, markup):
        markup.add(types.KeyboardButton(constants.TEXT_REFRESH))
        markup.add(types.KeyboardButton(constants.TEXT_BACK))
        return None

    def get_button_menu(self, types, markup):
        markup.add(types.KeyboardButton(constants.TEXT_BALANCE))
        markup.add(types.KeyboardButton(constants.TEXT_AP_BALANCE))
        markup.add(types.KeyboardButton(constants.TEXT_CATALOG))
        markup.add(types.KeyboardButton(constants.TEXT_HELP))
        markup.add(types.KeyboardButton(constants.TEXT_EXIT))
        return constants.TEXT_MENU

    def get_button_zero(self, types, markup):
        markup.add(types.KeyboardButton("/start"))
        return constants.TEXT_STRING_EXIT

    def get_state(self, command, types, markup, TelID):
        match self.STATE:
            case self.ZERO:
                self.STATE = self.GMENU
                return self.get_button_menu(types, markup)
            case self.GMENU:
                match command:
                    case constants.TEXT_BALANCE:
                        self.STATE = self.BALANCE
                        balance = wrapdbc.get_balance(TelID)
                        self.get_button_balance(types, markup)
                        course = get_course_in_dollars()
                        return constants.TEXT_COURSE + " = %(course)f\n"% {'course': course} + constants.TEXT_BALANCE + " = %(balance).2f$" % {'balance': balance}
                    case constants.TEXT_AP_BALANCE:
                        key_wallet = wrapdbc.get_key_wallet(TelID)
                        text = '%(key_wallet)s' % {'key_wallet': key_wallet}
                        return text
                    case constants.TEXT_HELP:
                        global SUPPORT
                        return SUPPORT
                    case constants.TEXT_CATALOG:
                        self.STATE = self.PRODUCT_CATALOG
                        return self.STATE
                    case constants.TEXT_EXIT:
                        self.STATE = self.ZERO
                        return self.get_button_zero(types, markup)
            case self.BALANCE:
                if command == constants.TEXT_REFRESH:
                    balance = wrapdbc.get_balance(TelID)
                    return constants.TEXT_BALANCE + " = %(balance).2f$" % {'balance': balance}
                if command == constants.TEXT_BACK:
                    self.STATE = self.GMENU
                    return self.get_button_menu(types, markup)
            case self.PRODUCT_CATALOG:
                if command == "PRE_PAY":
                    self.STATE = self.PRE_PAY
                    return self.STATE
                if command == "BACK":
                    self.STATE = self.GMENU
                    return self.STATE




