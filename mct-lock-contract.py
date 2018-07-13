"""
MCT Lock Contract Example
============================================

Author: Joe Stewart
Email: hal0x2328@splyse.tech

Date: July 13, 2018

This contract locks an amount of MCT for a period of time, with the option
to change the payee address if the payer and payee both agree. One could use
this feature to comply with regulatory requirements, for example, allowing
the original payee to sell their interest in the locked tokens, while
still allowing the depositor to do KYC checks on the new payee before 
approving the change.

The amount of tokens locked in the contract must be greater than the
minimum MCT contract storage stake in order for the storage functions 
to work that permit the payee address to be changed.

-----
Deployment in neo-python:

build mct-lock-contract.py
import contract mct-lock-contract.avm 0710 05 False False
wallet tkn_send MCT {from address} {lock contract address} {amount}

"""

from boa.interop.Neo.Blockchain import GetHeader, GetHeight
from boa.interop.Neo.Runtime import CheckWitness
from boa.interop.Neo.Block import Timestamp
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from boa.interop.Neo.App import RegisterAppCall

# Party1 is the depositor, who is sending funds to be locked in the contract
PARTY1=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# Party2 is the payee, who can withdraw the funds after the unlock period
PARTY2=b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01'

unlockTime = 1563148800  # July 15, 2019 00:00:00 UTC

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
        # This should never be necessary but just in case someone
        # accidentally sends non-MCT assets to the contract they 
        # can be recovered instead of being burned forever

        if CheckWitness(PARTY1):
            return True

        return False

    elif trigger == Application():

        # setNewPayee(newPayee) - if the current payee wants to assign
        # the tokens to another party, the contract payee can be changed
        # but only if both the depositor and current payee agree
        
        if operation == 'setNewPayee':
            if len(args) != 1:
                print('New payee scripthash not specified')
                return False
         
            new_payee = args[0]

            if len(new_payee) != 20:
                print('Incorrect new payee scripthash length')
                return False

            current_payee = Get('payee')

            if len(current_payee) != 20:
                current_payee = PARTY2

            if CheckWitness(PARTY1):  # depositor approval
                party2_payee = Get('Party2_Payee_Change_Approval')
                if new_payee == party2_payee:
                    Put('payee', new_payee) 
                    Delete('Party1_Payee_Change_Approval')
                    Delete('Party2_Payee_Change_Approval')
                else:  
                    Put('Party1_Payee_Change_Approval', new_payee)

            if CheckWitness(current_payee):  # current payee approval
                party1_payee = Get('Party1_Payee_Change_Approval')
                if new_payee == party1_payee:
                    Put('payee', new_payee) 
                    Delete('Party1_Payee_Change_Approval')
                    Delete('Party2_Payee_Change_Approval')
                else:  
                    Put('Party1_Payee_Change_Approval', new_payee)

        # getCurrentPayee() - return currently set payee value
        
        if operation == 'getCurrentPayee':
            current_payee = Get('payee')

            if len(current_payee) != 20:
                current_payee = PARTY2

            return current_payee

            
        # getUnlockTime() - return hard-coded unlock timestamp

        if operation == 'getUnlockTime':
            return unlockTime


        # withdraw() - if this operation is called after the unlock
        # period, the entire contract balance will be automatically
        # transferred to the current payee 

        if operation == 'withdraw':
            header = GetHeader(GetHeight())
            if header.Timestamp < unlockTime:
                return False

            # This contract's script hash, owner of the locked MCT tokens
            myhash = GetExecutingScriptHash()
            
            # Payout to current payee address
            payee = Get('payee')

            if len(current_payee) != 20:
                current_payee = PARTY2

            t_amount = MCTContract('balanceOf', [myhash])

            if t_amount > 0:
                return MCTContract('transfer', [myhash, payee, t_amount])
            else:
                print('No funds in contract')
            return False
    
        # end of normal invocations, reject any non-MCT invocations

        caller = GetCallingScriptHash()

        if caller != MCT_SCRIPTHASH:
            print('token type not accepted by this contract')
            return False

        if operation == 'onTokenTransfer':
            if CheckWitness(PARTY1):
                return True  # this is how party 1 deposits stake+locked tokens

            print('onTokenTransfer() called from address other than party 1')

    return False

# Staked storage appcalls

def Get(key):
    return MCTContract('Get', [key])

def Delete(key):
    return MCTContract('Delete', [key]) 

def Put(key, value):
    return MCTContract('Put', [key, value])

