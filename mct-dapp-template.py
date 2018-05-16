"""
Master Contract Token dApp Template Contract
============================================

Author: Joe Stewart
Email: hal0x2328@splyse.tech

Date: May 8 2018

This code demonstrates use of MCT receive/send and staked storage functions

Deployment in neo-python:

import contract mct-dapp-template.py 0710 05 False False
wallet tkn_send MCT {from address} {dApp contract address} {minimum stake}

"""
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from boa.interop.Neo.App import RegisterAppCall

OWNER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# mainnet
#MCT_SCRIPTHASH = b'?\xbc`|\x12\xc2\x87642$\xa4\xb4\xd8\xf5\x13\xa5\xc2|\xa8'
# privatenet
MCT_SCRIPTHASH = b'\x8dKL\x14V4\x17\xc6\x91\x91\xe0\x8b\xe0\xb8m\xdc\xb4\xbc\x86\xc1'

# mainnet
#MCTContract = RegisterAppCall('a87cc2a513f5d8b4a42432343687c2127c60bc3f', 'operation', 'args')
# privatenet
MCTContract = RegisterAppCall('c186bcb4dc6db8e08be09191c6173456144c4b8d', 'operation', 'args')

def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        if CheckWitness(OWNER):
            return True

        return False

    elif trigger == Application():

        if operation == 'hello':
            print('hello world!')
            totalcalls = Get('totalCalls')
            totalcalls = totalcalls + 1
            print(totalcalls)
            if Put('totalCalls', totalcalls):
                return True
            print('staked storage call failed')
            return False

            return True
         
        if operation == 'ownerWithdraw':
            if not CheckWitness(OWNER):
                print('only the contract owner can withdraw MCT from the contract')
                return False

            if len(args) != 1:
                print('withdraw amount not specified')
                return False
         
            t_amount = args[0]
            myhash = GetExecutingScriptHash()

            return MCTContract('transfer', [myhash, OWNER, t_amount])

        # end of normal invocations, reject any non-MCT invocations

        caller = GetCallingScriptHash()

        if caller != MCT_SCRIPTHASH:
            print('token type not accepted by this contract')
            return False

        if operation == 'onTokenTransfer':
            print('onTokenTransfer() called')
            return handle_token_received(caller, args)

    return False


def handle_token_received(chash, args):

    arglen = len(args)

    if arglen < 3:
        print('arg length incorrect')
        return False

    t_from = args[0]
    t_to = args[1]
    t_amount = args[2]

    if arglen == 4:
        extra_arg = args[3]  # extra argument passed by transfer()

    if len(t_from) != 20:
        return False

    if len(t_to) != 20:
        return False

    myhash = GetExecutingScriptHash()

    if t_to != myhash:
        return False

    if t_from == OWNER:
        # topping up contract token balance, just return True to allow
        return True

    if extra_arg == 'reject-me':
        print('rejecting transfer') 
        Delete(t_from)
        return False
    else:
        print('received MCT tokens!')
        totalsent = Get(t_from)
        totalsent = totalsent + t_amount
        if Put(t_from, totalsent):
            return True
        print('staked storage call failed')
        return False


# Staked storage appcalls

def Get(key):
    return MCTContract('Get', [key])

def Delete(key, value):
    return MCTContract('Delete', [key]) 

def Put(key, value):
    return MCTContract('Put', [key, value])

