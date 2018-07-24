"""
MCT reverse auction example

Notes for this project:
* This project needs to have a default selling price.
* This price needs to decrease over time.
"""

from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash
from boa.interop.Neo.App import RegisterAppCall

OWNER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# mainnet
# MCT_SCRIPTHASH = b'?\xbc`|\x12\xc2\x87642$\xa4\xb4\xd8\xf5\x13\xa5\xc2|\xa8'
# privatenet
MCT_SCRIPTHASH = b'\x8dKL\x14V4\x17\xc6\x91\x91\xe0\x8b\xe0\xb8m\xdc\xb4\xbc\x86\xc1'

# mainnet
# MCTContract = RegisterAppCall('a87cc2a513f5d8b4a42432343687c2127c60bc3f', 'operation', 'args')
# privatenet
MCTContract = RegisterAppCall('c186bcb4dc6db8e08be09191c6173456144c4b8d', 'operation', 'args')


def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        if CheckWitness(OWNER):
            return True
        return False
    elif trigger == Application():
        if operation ==







