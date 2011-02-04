###
# BitcoinWallet - supybot plugin for an IRC bitcoin wallet
#
# Based on supybot-bitcoin-marketmonitor, which is:
# Copyright (c) 2010, Daniel Folkinshteyn
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from supybot.test import *

class MockJsonProxy:
    def getaddressesbyaccount(self, account):
        return [ "14ccB2QFEKZnd1gLUtgr7vWg6JrMeXaQXK" ]

    def validateaddress(self, accountOrNick):
        return { "isvalid": True }

    def getaccount(self, accountOrNick):
        return "duck"

    def getaccountaddress(self, account):
        return "14ccB2QFEKZnd1gLUtgr7vWg6JrMeXaQXK"

    def getbalance(self, account, minConf):
        return 1234.12345678

    def move(self, fromAccount, to, amount, minConf):
        return True

    def sendfrom(self, fromAccount, to, amount, minConf):
        return True

class BitcoinWalletTestCase(PluginTestCase):
    plugins = ('BitcoinWallet','User')
    world.mockJsonProxy = MockJsonProxy()

    def testBalance(self):
        try:
            origuser = self.prefix
            self.prefix = 'nanotube!stuff@stuff/somecloak'
            self.assertNotError('balance')

            self.prefix = 'webchat!stuff@gateway/web/freenode'
            self.assertError('balance')
        finally:
            #world.testing = True
            self.prefix = origuser

    def testBitcoinAddress(self):
        try:
            origuser = self.prefix
            self.prefix = 'nanotube!stuff@stuff/somecloak'
            self.assertNotError('bitcoinaddress')

            self.prefix = 'webchat!stuff@gateway/web/freenode'
            self.assertError('bitcoinaddress')
        finally:
            #world.testing = True
            self.prefix = origuser

    def testPay(self):
        try:
            origuser = self.prefix
            self.prefix = 'nanotube!stuff@stuff/somecloak'
            self.assertNotError('pay xyz 0.01')

            self.prefix = 'webchat!stuff@gateway/web/freenode'
            self.assertError('pay xyz 0.01')
        finally:
            #world.testing = True
            self.prefix = origuser


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
