###
# BitcoinWallet - supybot plugin for an IRC bitcoin wallet
#
# Based on supybot-bitcoin-marketmonitor, which is:
# Copyright (C) 2010, Daniel Folkinshteyn <nanotube@users.sourceforge.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot import conf
from supybot import ircdb

from jsonrpc import JSONRPCException, ServiceProxy

def getPositiveFloat(irc, msg, args, state, type='positive floating point number'):
    try:
        v = float(args[0])
        if v <= 0:
            raise ValueError, "only positive numbers allowed."
        state.args.append(v)
        del args[0]
    except ValueError:
        state.errorInvalid(type, args[0])

addConverter('positiveFloat', getPositiveFloat)

class BitcoinWallet(callbacks.Plugin):
    """This plugin offers a Bitcoin wallet for IRC users.
    Use command 'bitcoinaddress' to obtain your associated bitcoin address.
    Use commands 'pay' and 'balance' for making payments and checking your
    account balance.
    """
    threaded = True

    def __init__(self, irc):
        self.__parent = super(BitcoinWallet, self)
        self.__parent.__init__(irc)
        self.proxy = self._getServiceProxy()

    def die(self):
        self.__parent.die()

    def _checkHost(self, host):
        if self.registryValue('requireCloak'):
            if "/" not in host or host.startswith('gateway/web/freenode'):
                return False
        return True

    def _checkRegisteredUser(self, prefix):
        try:
            _ = ircdb.users.getUser(prefix)
            return True
        except KeyError:
            return False

    def _getServiceProxy(self):
        # TODO prevent interactive authentication in case of invalid
        # username/password
        return ServiceProxy(self.registryValue("jsonRpcUrl"))

    def _getWalletAccountName(self, network, nick):
        return '-'.join([self.registryValue('accountNamePrefix'),
            network, nick])

    def _getWalletAccountAddress(self, account):
        accounts = self.proxy.getaddressesbyaccount(account)
        if len(accounts) > 0:
            return accounts[0]
        else:
            return None

    def _payToType(self, network, accountOrNick):
        internal = True
        status = self.proxy.validateaddress(accountOrNick)
        if status['isvalid']:
            toAccount = self.proxy.getaccount(accountOrNick)
            if toAccount:
                to = toAccount
            else:
                internal = False
                to = accountOrNick
        else:
            toAccount = self._getWalletAccountName(network,
                    accountOrNick)
            to = self._getWalletAccountAddress(toAccount)
        return (internal, to)


    def bitcoinaddress(self, irc, msg, args):
        """takes no arguments

        Returns the bitcoin address associated with your nick. This will
        create an address if none exists.
        """
        if not self._checkHost(msg.host) and not self._checkRegisteredUser(msg.prefix):
            irc.error("For identification purposes, you must have a freenode cloak "
                      "to use the wallet.")
            return
        account = self._getWalletAccountName(irc.network, msg.nick)
        address = self._getWalletAccountAddress(account)
        if address is None:
            address = self.proxy.getaccountaddress(account)
        irc.reply("Your bitcoin address is %s" % address)
    bitcoinaddress = wrap(bitcoinaddress)

    def balance(self, irc, msg, args):
        """takes no arguments

        Returns the balance for the the bitcoin address associated with your nick.
        """
        if not self._checkHost(msg.host) and not self._checkRegisteredUser(msg.prefix):
            irc.error("For identification purposes, you must have a freenode cloak "
                      "to use the wallet.")
            return
        account = self._getWalletAccountName(irc.network, msg.nick)
        address = self._getWalletAccountAddress(account)
        if address is None:
            irc.error("You don't yet have a bitcoin address associated with "
                      "your nick. Use 'bitcoinaddress' to create one.")
            return

        balance = self.proxy.getbalance(account, self.registryValue('minConf'))
        irc.reply("Your balance is %.8g BTC." % balance)
    balance = wrap(balance)

    def pay(self, irc, msg, args, accountOrNick, amount):
        """<account|nick> <amount>

        Pays the specified <address> or <nick> <amount> bitcoin.
        """
        if not self._checkHost(msg.host) and not self._checkRegisteredUser(msg.prefix):
            irc.error("For identification purposes, you must have a freenode cloak "
                      "to use the wallet.")
            return
        fromAccount = self._getWalletAccountName(irc.network, msg.nick)
        fromAddress = self._getWalletAccountAddress(fromAccount)
        if fromAddress is None:
            irc.error("You don't yet have a bitcoin address associated with "
                      "your nick. Use 'bitcoinaddress' to create one.")
            return
        minAmount = self.registryValue('minAmount')
        if amount < minAmount:
            irc.error("The specified amount is below the minimum of %.8g BTC." %
                    minAmount)
            return

        (internal, to) = self._payToType(irc.network, accountOrNick)
        if internal and to is None:
            irc.error("The specified nick doesn't yet have a bitcoin "
                        "address. Tell them to use 'bitcoinaddress' to "
                        "create one.")
            return

        try:
            if internal:
                self.log.debug("Bitcoin MOVE %s %s %.8g", fromAccount, to, amount)
                self.proxy.move(fromAccount, to, amount,
                        self.registryValue('minConf'))
            else:
                self.log.debug("Bitcoin SENDFROM %s %s %.8g", fromAccount, to, amount)
                self.proxy.sendfrom(fromAccount, to,
                        amount,self.registryValue('minConf'))
        except JSONRPCException, e:
            message = e.error['message']
            irc.error("Payment failed. %s" % message)
            return

        irc.reply("Payment successful.")
    pay = wrap(pay, ['something', 'positiveFloat'])

Class = BitcoinWallet

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
