"""
Safe Remote Purchase Example for the Neo Blockchain
===================================================

Author: Joe Stewart
Email: hal0x2328@splyse.tech

Date: July 19 2019

This code implements Safe Remote Purchase using MCT NEP-5 tokens.

Safe Remote Purchase is a kind of self-escrow contract for a sale 
between two parties who do not necessarily trust each other, and
don't have a trusted third party to act as escrow and confirm that
the deal was completed and both parties are satisfied before release 
of the funds.

In Safe Remote Purchase, a seller deposits 2x the amount of the
price of the item for sale into the smart contract. The buyer then
also deposits 2x the price of the item for sale into the contract.

Once the item is received and the buyer is satisfied with it, they
can call the confirmReceived operation of the contract, which will
refund the buyer's deposit minus the price of the item, and refund
the seller's deposit plus the price of the item.

Since both parties have money staked in the contract, it is in their
best interest to complete the sale. If the seller does not ship the
item that has been paid for, they will lose 2x what the item is worth. 

If the buyer does not fulfill their obligation to confirm receipt of
the item, they will lose 1x what the item is worth.

A seller can only cancel a sale and receive a refund *before* a buyer
has made a deposit on the item. Once this happens they are obligated
to ship, with the seller deposit acting as incentive to complete the
shipment as soon as possible since they will not be able to recover
it until the buyer has confirmed receipt of the item.

This contract allows for an unlimited number of sales by any number
of different sellers. A seller can specify the address of a specific
buyer, or no buyer address (meaning anyone can buy the item).

This contract can be deployed for 90 GAS + 10000 MCT

Contract operations
-------------------

# relayed from the MCT contract transfer() operation
onTokenTransfer::createSale(buyer, price, description)  # creates a new sale
onTokenTransfer::buyerDeposit(sale_id)  # buyer agreement to purchase with deposit

# invoked directly
confirmShipment(sale_id)  # seller invokes to show that shipment has been made
confirmReceived(sale_id)  # buyer invokes to show that item has been received
deleteSale(sale_id)  # delete a sale where no buyer has deposited yet
sale(sale_id)  # sale details and current state

Deployment and usage in neo-python
----------------------------------

# compile
sc build safe-remote-purchase.py

# deploy
sc deploy safe-remote-purchase.avm False False True 0710 05

# stake 10K MCT tokens in order to use MCT contract storage
wallet token send MCT {owner_addr} {contract_addr} 1000000000000

# create a sale of an item for 1000 MCT (depositing 2000 at the same time)
sc invoke {MCT contract hash} transfer ['{seller_addr}','{SRP_contract_addr}',200000000000,
    ['createSale','{buyer_addr}',100000000000,'item description']]

# make a deposit of 2000 MCT on a sale of an item offered for 1000 MCT
sc invoke {MCT contract hash} transfer ['{buyer_addr}','{SRP_contract_addr}',200000000000,
    ['buyerDeposit',1]]

# update the sale state after the shipment has been made
sc invoke {SRP contract hash} confirmShipment [{sale_id}]

# confirm the receipt of the item, releasing all funds and deleting the sale
sc invoke {SRP contract hash} confirmReceived [{sale_id}]

"""

from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash, GetScriptContainer
from boa.interop.Neo.Transaction import GetHash
from boa.interop.Neo.App import RegisterAppCall
from boa.builtins import concat

# address that will stake the tokens for the contract to have storage
OWNER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# TestNet - CTX
MCT_HASH = b'\xe7\xb12\xb9\x95\xf4=\xbb\xdd\xd2\xa3&\x8a\x04\xa2\xae\x08\x1e\xff\x9a'
MCTContract = RegisterAppCall('9aff1e08aea2048a26a3d2ddbb3df495b932b1e7', 'operation', 'args')

# MaiNet - MCT
#MCT_HASH = b'?\xbc`|\x12\xc2\x87642$\xa4\xb4\xd8\xf5\x13\xa5\xc2|\xa8'
#MCTContract = RegisterAppCall('a87cc2a513f5d8b4a42432343687c2127c60bc3f', 'operation', 'args')

OnError = RegisterAction('error', 'message')


def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():
        return False  # no withdrawals allowed, even by contract owner

    elif trigger == Application():

        arglen = len(args)

        if operation == 'onTokenTransfer':
            return handle_token_received(GetCallingScriptHash(), args)

        if operation == 'confirmShipment':  # seller-only
            assert arglen == 1, 'incorrect argument length'
            sale_id = args[0]
            
            sale = loadSale(sale_id)
            assert sale['state'] == 'awaiting shipment', 'sale state incorrect'
            assert CheckWitness(sale['seller']), 'must be seller to confirm shipment'

            sale['state'] = 'shipment confirmed'
            r = Put(concat('sales/', sale_id), Serialize(sale))
        
            return True

        elif operation == 'confirmReceived':  # buyer-only
            assert arglen == 1, 'incorrect argument length'
            sale_id = args[0]
            
            sale = loadSale(sale_id)
            assert sale['state'] == 'shipment confirmed', 'sale state incorrect'
            seller = sale['seller']
            buyer = sale['buyer']
            price = sale['price']

            myhash = GetExecutingScriptHash()
            assert CheckWitness(buyer), 'must be buyer to complete the sale'

            # return the buyer deposit minus the item price
            r = MCTContract('transfer', [myhash, buyer, price])

            # return the seller deposit plus the item price
            r = MCTContract('transfer', [myhash, seller, price * 3])

            # delete the sale
            r = Delete(concat('sales/', sale_id))
            return True

        elif operation == 'deleteSale':  # seller-only, if buyer has not already made deposit
            assert arglen == 1, 'incorrect argument length'
            sale_id = args[0]
            sale = loadSale(sale_id)
            assert sale['state'] == 'new', 'cannot cancel sale post-buyer-deposit'
            seller = sale['seller']
            price = sale['price']

            myhash = GetExecutingScriptHash()
            assert CheckWitness(seller), 'must be seller to cancel the sale'

            # return the seller deposit to them
            return MCTContract('transfer', [myhash, seller, price * 2])

            # delete the sale
            r = Delete(concat('sales/', sale_id))
            return True

        elif operation == 'sale':  # get sale details
            assert arglen == 1, 'incorrect argument length'
            sale_id = args[0]
            return Get(concat('sales/', sale_id))

    AssertionError('unknown operation - code: XxXxXxXx')


def handle_token_received(chash, args):
  
    assert chash == MCT_HASH, 'transactions must use MCT'

    if t_from == OWNER:
        # just staking MCT tokens for storage, nothing else to do here
        return True

    arglen = len(args)
    assert arglen == 4, 'incorrect arg length'

    # parameters of MCT transfer
    t_from = args[0]
    t_to = args[1]
    t_amount = args[2] * 1
    p_args = args[3]  # 4th argument passed by MCT transfer()

    assert len(t_from) == 20, 'invalid address'
    assert len(t_to) == 20, 'invalid address'
    assert t_to == GetExecutingScriptHash(), 'destination error'
    assert t_amount > 0, 'no funds transferred'

    p_len = len(p_args)
    assert p_len > 1, 'incorrect secondary arg length'

    p_operation = p_args[0]
    if p_operation == 'createSale':
        assert p_len == 4, 'incorrect arguments to createSale'
        buyer_addr = p_args[1]
        price = p_args[2] * 1
        description = p_args[3]
      
        assert price > 0, 'must set a price > 0'
        assert t_amount == price * 2, 'seller deposit must be 2x price'

        tx = GetScriptContainer()
        sale = {}

        sale['id'] = tx.Hash
        sale['seller'] = t_from
        sale['buyer'] = buyer_addr  # if empty, any buyer may pay
        sale['description'] = description  # optional
        sale['price'] = price
        sale['state'] = 'new'

        r = Put(concat('sales/', tx.Hash), Serialize(sale))
        return True

    elif p_operation == 'buyerDeposit':
        assert p_len == 2, 'incorrect arguments to buyerDeposit'
        sale_id = p_args[1]
        sale = loadSale(sale_id)

        assert sale['state'] == 'new', 'sale state incorrect'
        assert sale['price'] > 0, 'sale price incorrect'
        assert t_amount == sale['price'] * 2, 'buyer deposit must be 2x price'

        buyer = sale['buyer']
        if len(buyer) == 20:
            assert CheckWitness(buyer), 'must be listed buyer to place deposit'
        else:
            sale['buyer'] = t_from  # any-buyer sale claimed

        sale['state'] = 'awaiting shipment'
        r = Put(concat('sales/', sale_id), Serialize(sale))
        
        return True

def loadSale(sale_id):
    s = Get(concat('sales/', sale_id))
    assert len(s) > 0, 'no such sale exists'
    sale = Deserialize(s)
    assert sale, 'sale deserialization failure'
    assert sale['id'] == sale_id, 'sale data is corrupt'
    return sale

# staked storage

def Get(key):
    return MCTContract('Get', [key])

def Delete(key, value):
    return MCTContract('Delete', [key]) 

def Put(key, value):
    return MCTContract('Put', [key, value])


# required in order to use assert

def AssertionError(msg):
    OnError(msg) # for neo-cli ApplicationLog
    raise Exception(msg)

