"""MCT Reverse Auction Example

Notes for this project:
* This project needs to have a default selling price for tokens (let's say 500 MCT).
* A minimum price should be set, the token price cannot go below that.
* This price needs to decrease over time (every x number of blocks) until the token sells.
* Create an algorithm that decreases the selling price of tokens based on past transactions. Algorithm:
    1. reset the counter, the sum, and the average selling price to 0
    2. add up the selling price from each of the transactions that this contract has done over the last
        25,000 blocks (about a week) and increment a counter each time
        * at init, add 25000 to current block and set that equal to future_block
        * perform the process described in '2' until current_block == future_block
    3. divide the sum of these transactions by the counter (number of transactions) to get the average selling price
    4. set the selling price to the average selling price
    5. restart the loop
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

ORIGINAL_SELL_PRICE = 500  # 500 MCT
MIN_SELL_PRICE = 1  # 1 MCT

sell_price = 0


def Main(operation, args):
    """

    :param operation:
        * 'buy'
        * 'sell'

    :param args:
    :return:
    """
    trigger = GetTrigger()

    if trigger == Verification():
        # This should never be necessary but just in case someone
        # accidentally sends non-MCT assets to the contract they
        # can be recovered instead of being burned forever
        if CheckWitness(OWNER):
            return True
        return False

    elif trigger == Application():
        if operation == 'buy':
            """
            1. verify that the amount of mct from the buyer is equal to the current selling price
            2. send the mct tokens to the owner of the sold token and send the sold token to the new owner
            3. print(<token_script_hash> now belongs to <new_owner_script_hash>)
            """
            print('buy() called')
            return handle_token_received()

        if operation == 'sell':
            """
            1. verify that that the token script hash being sent is actually owned by the account sending it
            2. ask the user if they would like to set the starting sell price instead of using the current default
            """
            print('sell this token')


def handle_token_received(chash, args):
    arglen = len(args)

    # there must be at least a 'transfer from' address, 'transfer to' address, and 'transfer amount' passed as args
    if arglen < 3:
        print('arg length incorrect')
        return False

    t_from = args[0]
    t_to = args[1]
    t_amount = args[2]
    extra_arg = None

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


def Delete(key):
    return MCTContract('Delete', [key])


def Put(key, value):
    return MCTContract('Put', [key, value])
