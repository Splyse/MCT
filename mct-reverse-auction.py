"""MCT Reverse Dutch Auction Example

More notes:
* Someone should be able to send a non-fungible token to the smart contract (along with some other stuff)
    to be able to sell the NFT. The




Notes for this project:
* This project needs to have a default selling price for tokens (let's say 500 MCT).
* A minimum price should be set, the token price cannot go below that.
* A seller should send their token's symbol, their wallet address, the mct-reverse-auction contract address, and
    the amount of tokens
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

OWNER = b'\x0f\x26\x1f\xe5\xc5\x2c\x6b\x01\xa4\x7b\xbd\x02\xbd\x4d\xd3\x3f\xf1\x88\xc9\xde'

# mainnet
# MCT_SCRIPTHASH = b'?\xbc`|\x12\xc2\x87642$\xa4\xb4\xd8\xf5\x13\xa5\xc2|\xa8'
# privatenet
MCT_SCRIPTHASH = b'\x8d\x4b\x4c\x14\x56\x34\x17\xc6\x91\x91\xe0\x8b\xe0\xb8\x6d\xdc\xb4\xbc\x86\xc1'  # for staking
NFT_SCRIPTHASH = b'\x2a\x96\x47\x2d\x75\x30\xb1\xb6\x96\xb9\xca\xc4\x4e\xa9\xbd\xe0\xcb\x7b\x1e\x9d'  # token being sold/bought

# mainnet
# MCTContract = RegisterAppCall('a87cc2a513f5d8b4a42432343687c2127c60bc3f', 'operation', 'args')
# privatenet
MCTContract = RegisterAppCall('c186bcb4dc6db8e08be09191c6173456144c4b8d', 'operation', 'args')  # for staking
NFTContract = RegisterAppCall('AW6eFemRABDUpWBPgHyVShPmrbtiXcqXsb', 'operation', 'args')  # token being imported

ORIGINAL_SELL_PRICE = 500  # 500 MCT
MIN_SELL_PRICE = 1  # 1 MCT

sell_price = ORIGINAL_SELL_PRICE


def Main(operation, args):
    """

    :param operation: operation to be performed
        buy
        sell
    :type operation: str

    :param args: list of arguments
        args[0] is always sender script hash
        args[1] is
    :type args: list
    :return:
        bytearray: The result of the operation
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
        if operation == 'buyToken':
            """
            1. verify that the amount of mct from the buyer is equal to the current selling price
            2. send the mct tokens to the owner of the sold token and send the sold token to the new owner
            3. print(<token_script_hash> now belongs to <new_owner_script_hash>)
            """
            print('buy() called')

            caller = GetCallingScriptHash()  # get the scripthash of the caller for this smart contract
            if len(caller) != 20:  # make sure it's a valid script hash
                return False
            buy(caller, args)

        if operation == 'sellToken':
            """
            1. verify that that the token script hash being sent is actually owned by the account sending it
            2. ask the user if they would like to set the starting sell price instead of using the current default
            3. store the token using staked storage
            """
            print('sell() called')
            # store_token_to_be_sold(args)
            arglen = len(args)

            if arglen < 3:
                print('arg length incorrect')
                return False

            t_from = args[0]  # the token owner's address
            t_to = args[1]  # this smart contract's address
            tokenid = args[2]  # nft unique id

            if len(t_from) != 20:
                return False
            if len(t_to) != 20:
                return False

            this_contract_hash = GetExecutingScriptHash()
            if t_to != this_contract_hash:
                return False

            if Put('token', tokenid):
                print('Storing token to be sold')
                return True
            print('staked storage call failed')
            return True

        if operation == 'ownerWithdraw':
            """
            This method is used by the owner of the contract to withdraw MCT from the smart contract. 
            This will be particularly useful if the MCT minimum stake amount changes. 
            """
            if not CheckWitness(OWNER):
                print('only the contract owner can withdraw MCT from the contract')
                return False

            if len(args) != 1:
                print('withdraw amount not specified')
                return False

            t_amount = args[0]  # withdrawal amount
            this_contract_hash = GetExecutingScriptHash()  # gets the scripthash of the executing smart contract
            return MCTContract('transfer', [this_contract_hash, OWNER, t_amount])


def buy(caller, args):
    """
    1. verify that the amount of mct from the buyer is equal to the current selling price
    2. send the mct tokens to the owner of the sold token and send the sold token to the new owner
    3. print(<token_script_hash> now belongs to <new_owner_script_hash>)
    :param args: array of arguments passed: should be a 'transfer to address' and 'transfer amount'
    :return:
    """
    arglen = len(args)

    if arglen < 3:
        print('arg length incorrect')
        return False

    t_to = args[0]  # transfer to address
    t_amount = args[1]  # transfer amount

    if arglen == 4:
        extra_arg = args[2]

    if len(t_to) != 20:
        return False

    if t_amount != sell_price:
        return False

    myhash = GetExecutingScriptHash()

    if t_amount > 0:
        print('Transferring token in contract to payee')
        return MCTContract('transfer', [myhash, t_to, t_amount])


def store_token_to_be_sold(args):
    """
    1. verify that that the token script hash being sent is actually owned by the account sending it
    2. ask the user if they would like to set the starting sell price instead of using the current default
    3. store the token using staked storage
    :param args: list of arguments
        :arg 0: seller's wallet address
        :arg 1: mct reverse dutch auction contract address
        :arg 2: token id (Non-Fungible Token)
    :return: boolean value depending on success or failure
    """

    arglen = len(args)

    if arglen < 3:
        print('arg length incorrect')
        return False

    t_from = args[0]  # the token owner's address
    t_to = args[1]  # this smart contract's address
    tokenid = args[2]  # nft unique id

    if len(t_from) != 20:
        return False
    if len(t_to) != 20:
        return False

    this_contract_hash = GetExecutingScriptHash()
    if t_to != this_contract_hash:
        return False

    if Put('token', tokenid):
        print('Storing token to be sold')
        return True
    print('staked storage call failed')
    return True


# Staked storage appcalls

def Get(key):
    return MCTContract('Get', [key])


def Delete(key):
    return MCTContract('Delete', [key])


def Put(key, value):
    return MCTContract('Put', [key, value])
