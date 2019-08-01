"""
MCT Atomic Swap Example
===================================

Author: Joe Stewart
Email: hal0x2328@splyse.tech

Date: May 8 2018

This code demonstrates atomic NEP-5 token swap using contract-tradable tokens
This contract is deployed on the Neo TestNet at the address
ATom1c3QN46UCbpELUyJBCwF2Q7HLhxDjjtx

"""
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from boa.interop.Neo.App import RegisterAppCall
from boa.builtins import concat

OWNER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
minimum_hold = 10000 * 100000000  # contract must maintain this amount of tokens for staked storage

# TestNet CTX
TOKEN1 = b'\xe7\xb12\xb9\x95\xf4=\xbb\xdd\xd2\xa3&\x8a\x04\xa2\xae\x08\x1e\xff\x9a'

# TestNet CTY
TOKEN2 = b'\xe7\xb2\x06\xc4\xc6#\xebGKQ\x03>M\x10\xdd\x94\xc9\xcb\xd9\x81'

Token1Contract = RegisterAppCall('9aff1e08aea2048a26a3d2ddbb3df495b932b1e7', 'operation', 'args')
Token2Contract = RegisterAppCall('81d9cbc994dd104d3e03514b47eb23c6c406b2e7', 'operation', 'args')

def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        if CheckWitness(OWNER):
            return True

        return False

    elif trigger == Application():
        if operation == 'setExchangeRate':
            if not CheckWitness(OWNER):
                return False

            if len(args) != 3:
                return False

            fromtoken = args[0]
            totoken = args[1]
            rate = args[2]
            
            tokenkey = concat(fromtoken, totoken)

            if len(tokenkey) != 40:
                return False

            return Put(tokenkey, rate)
 
        if operation == 'exchangeRate':
            if len(args) != 2:
                return False

            fromtoken = args[0]
            totoken = args[1]

            tokenkey = concat(fromtoken, totoken)

            if len(tokenkey) != 40:
                return False

            return Get(tokenkey)

        if operation == 'ownerWithdraw':
            if not CheckWitness(OWNER):
                return False

            if len(args) != 2:
                return False
         
            t_scripthash = args[0]
            t_amount = args[1]

            myhash = GetExecutingScriptHash()

            if t_scripthash == TOKEN1: 
                return Token1Contract('transfer', [myhash, OWNER, t_amount])
            elif t_scripthash == TOKEN2: 
                return Token2Contract('transfer', [myhash, OWNER, t_amount])

        chash = GetCallingScriptHash()

        if chash != TOKEN1:
            if chash != TOKEN2:  # for some reason comparing these with "and"
                                 # returns an extra value on evaluation stack
                print('Token type not accepted by this contract')
                return False

        if operation == 'onTokenTransfer':
            print('onTokenTransfer() called')
            return handle_token_received(chash, args)

    return False


def handle_token_received(chash, args):
  
    swap_rate = 0
    desired_rate = 0
    current_balance = 0

    arglen = len(args)

    if arglen < 3:
        print('arg length incorrect')
        return False

    t_from = args[0]
    t_to = args[1]
    t_amount = args[2]

    if arglen == 4:
        desired_rate = args[3]  # optional 4th argument passed by transfer()

    if len(t_from) != 20:
        return False

    if len(t_to) != 20:
        return False

    myhash = GetExecutingScriptHash()

    if t_to != myhash:
        return False

    if t_from == OWNER:
        # topping up contract token balance
        return True

    if chash == TOKEN1:
        swap_rate = Get(concat(TOKEN1, TOKEN2)) 
        current_balance = Token2Contract('balanceOf', [myhash])
    elif chash == TOKEN2:
        swap_rate = Get(concat(TOKEN2, TOKEN1))
        current_balance = Token1Contract('balanceOf', [myhash])

    if swap_rate == 0:
        print('swap rate has not been set for this token pair')
        return False

    if desired_rate > 0:
        if swap_rate != desired_rate:
            print('could not meet desired swap_rate, invoke exchangeRate again')
            return False

    tokens_out = swap_rate * t_amount / 100000000

    print('check balance')
    if tokens_out > current_balance - minimum_hold:
        print('cannot fulfill order, insufficient balance in contract')
        return False

    print('Executing transfer')
    if chash == TOKEN1: 
        return Token2Contract('transfer', [myhash, t_from, tokens_out])
    elif chash == TOKEN2: 
        return Token1Contract('transfer', [myhash, t_from, tokens_out])

    return False


def Get(key):
   return Token1Contract('Get', [key])

def Delete(key):
    return Token1Contract('Delete', [key]) 

def Put(key, value):
   return Token1Contract('Put', [key, value])
