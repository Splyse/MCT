"""
NEO Non-Fungible Token Smart Contract Template

Authors: Joe Stewart, Jonathan Winter
Email: hal0x2328@splyse.tech, jonathan@splyse.tech
Version: 0.2
Date: 06 August 2018
License: MIT

Based on NEP5 template by Tom Saunders

Compile and deploy with neo-python:
neo> build nft_template.py
neo> import contract nft_template.avm 0710 05 True False

"""

from boa.interop.Neo.Storage import GetContext, Get, Put, Delete
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.App import RegisterAppCall, DynamicAppCall
from boa.builtins import concat, range
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness, Notify
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.Neo.Blockchain import GetContract

TOKEN_NAME = 'Non-Fungible Token'
TOKEN_SYMBOL = 'NFT'
TOKEN_DECIMALS = 8
TOKEN_CIRC_KEY = b'in_circulation'

# This is the script hash of the address for the owner of the contract
# This can be found in ``neo-python`` with the wallet open, use ``wallet`` command
# owner = b'+z\x15\xd2\xc6e\xa9\xc3B\xf0jI\x8fW\x13\xa4\x93\x14\xc1\x04'
TOKEN_CONTRACT_OWNER = b'\x0f\x26\x1f\xe5\xc5\x2c\x6b\x01\xa4\x7b\xbd\x02\xbd\x4d\xd3\x3f\xf1\x88\xc9\xde'

OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnNFTTransfer = RegisterAction('NFTtransfer', 'addr_from', 'addr_to', 'tokenid')
OnApprove = RegisterAction('approve', 'addr_from', 'addr_to', 'amount')
OnNFTApprove = RegisterAction('NFTapprove', 'addr_from', 'addr_to', 'tokenid')


def Main(operation, args):
    """

    :param operation: str The name of the operation to perform
    :param args: list A list of arguments along with the operation
    :return:
        bytearray: The result of the operation

    Token operations:

    - allowance(tokenid): returns approved third-party spender of a token
    - approve(spender, tokenid, revoke): approve third party to spend a token
    - balanceOf(owner): returns owner's current total tokens owned
    - circulation(): returns current number of tokens in circulation
    - decimals(): returns number of decimals of token
    - mintToken(owner, ROData): create a new NFT token
    - modifyRWData(tokenid, RWData): modify a token's RW data
    - name(): returns name of token
    - ownerOf(tokenid): returns owner of a token
    - symbol(): returns token symbol
    - tokenOfOwnerByIndex(owner, idx): returns one token from owner's collection
    - properties(tokenid): returns a token's RO data
    - transfer(to, tokenid): transfers a token
    - transferFrom(from, to, tokenid): transfers a token by authorized spender
    """

    trigger = GetTrigger()

    if trigger == Verification():

        # check if the invoker is the owner of this contract
        is_owner = CheckWitness(owner)

        # If owner, proceed
        if is_owner:
            return True

    elif trigger == Application():

        if operation == 'name':
            return name

        elif operation == 'decimals':
            # NFT tokens will always be non-divisible by nature
            return 0

        elif operation == 'symbol':
            return symbol

        ctx = GetContext()

        if operation == 'circulation' or operation == 'totalSupply':
            return Get(ctx, in_circulation_key)

        arg_error = 'Incorrect Arg Length'

        if operation == 'tokenOfOwnerByIndex':
            if len(args) == 2:
                t_owner = args[0]
                t_idx = args[1]
                if len(t_idx) == 0:
                    t_idx = 0
                ownerkey = concat(t_owner, t_idx)
                return Get(ctx, ownerkey)
            return arg_error

        elif operation == 'ownerOf':
            if len(args) == 1:
                t_id = args[0]
                if len(t_id) == 0:
                    t_id = 0
                t_owner = Get(ctx, t_id)
                if len(t_owner) > 0:
                    return t_owner
                else:
                    return 'token does not exist'
            return arg_error

        elif operation == 'tokenROData':
            if len(args) == 1:
                t_id = args[0]
                if len(t_id) == 0:
                    t_id = 0
                rokey = concat('ro/', t_id)
                return Get(ctx, rokey)
            return arg_error

        elif operation == 'tokenRWData':
            if len(args) == 1:
                t_id = args[0]
                if len(t_id) == 0:
                    t_id = 0
                rwkey = concat('rw/', t_id)
                return Get(ctx, rwkey)
            return arg_error

        elif operation == 'tokenURI':
            if len(args) == 1:
                t_id = args[0]
                if len(t_id) == 0:
                    t_id = 0
                urikey = concat('uri/', t_id)
                return Get(ctx, urikey)
            return arg_error

        elif operation == 'modifyRWData':
            if len(args) == 2:
                t_id = args[0]
                t_rw = args[1]
                return do_modify_token(ctx, 'rw/', t_id, t_rw)
            return arg_error

        elif operation == 'modifyURI':
            if len(args) == 2:
                t_id = args[0]
                t_uri = args[1]
                return do_modify_token(ctx, 'uri/', t_id, t_uri)
            return arg_error

        elif operation == 'mintToken':
            if len(args) == 4:
                t_owner = args[0]
                t_ro = args[1]
                t_rw = args[2]
                t_uri = args[3]
                return do_mint_nft(ctx, t_owner, t_ro, t_rw, t_uri)
            return arg_error

        elif operation == 'balanceOf':
            if len(args) == 1:
                account = args[0]
                return Get(ctx, account)
            return arg_error

        elif operation == 'transfer':
            if len(args) == 3:
                t_from = args[0]
                t_to = args[1]
                t_id = args[2]
                return do_transfer(ctx, t_from, t_to, t_id)
            return arg_error

        elif operation == 'transferFrom':
            if len(args) == 3:
                t_from = args[0]
                t_to = args[1]
                t_id = args[2]
                return do_transfer_from(ctx, t_from, t_to, t_id)
            return arg_error

        elif operation == 'approve':
            if len(args) == 3:
                t_spender = args[0]
                t_id = args[1]
                revoke = args[2]  # set to 1 to revoke previous approval
                return do_approve(ctx, t_spender, t_id, revoke)
            return arg_error

        elif operation == 'allowance':
            if len(args) == 1:
                t_id = args[0]
                if len(t_id) == 0:
                    t_id = 0
                allowance_key = concat("approved/", t_id)
                return Get(ctx, allowance_key)
            return arg_error

        print('unknown operation')

    return False


def do_transfer(ctx, t_from, t_to, t_id):
    """

    :param ctx:
    :param t_from:
    :param t_to:
    :param t_id:
    :return:
    """
    if len(t_id) == 0:
        t_id = 0

    if len(t_to) != 20:
        return False

    if len(t_from) != 20:
        return False

    # Verifies that the calling contract has verified the required script hashes of the transaction/block
    if CheckWitness(t_from):

        if t_from == t_to:
            print("transfer to self!")
            return True

        ownedBy = Get(ctx, t_id)

        if t_from != ownedBy:
            print("token is not owned by tx sender")
            return False

        res = removeTokenFromOwnersList(ctx, t_from, t_id)
        if res == False:
            print("unable to transfer token")
            return False

        addTokenToOwnersList(ctx, t_to, t_id)

        Put(ctx, t_id, t_to)

        # remove any existing approvals for this token
        approval_key = concat("approved/", t_id)
        Delete(ctx, approval_key)

        # For backward compatibility with blockchain trackers
        OnTransfer(t_from, t_to, 1)

        OnNFTTransfer(t_from, t_to, t_id)

        return True
    else:
        print("from address is not the tx sender")

    return False


def do_transfer_from(ctx, t_from, t_to, t_id):
    """

    :param ctx:
    :param t_from:
    :param t_to:
    :param t_id:
    :return:
    """
    if len(t_id) == 0:
        t_id = 0

    if len(t_from) != 20:
        return False

    if len(t_to) != 20:
        return False

    if t_from == t_to:
        print("transfer to self!")
        return True

    t_owner = Get(ctx, t_id)

    if len(t_owner) != 20:
        print("token does not exist")
        return False

    if t_from != t_owner:
        print("from address is not the owner of this token")
        return False

    approval_key = concat("approved/", t_id)
    authorized_spender = Get(ctx, approval_key)

    if len(authorized_spender) == 0:
        print("no approval exists for this token")
        return False

    if CheckWitness(authorized_spender):

        res = removeTokenFromOwnersList(ctx, t_from, t_id)
        if res == False:
            print("unable to transfer token")
            return False

        addTokenToOwnersList(ctx, t_to, t_id)

        Put(ctx, t_id, t_to)

        # remove the approval for this token
        Delete(ctx, approval_key)

        print("transfer complete")

        OnTransfer(t_from, t_to, 1)
        OnNFTTransfer(t_from, t_to, t_id)

        return True

    print("transfer by tx sender not approved by token owner")
    return False


def do_approve(ctx, t_spender, t_id, revoke):
    """

    :param ctx:
    :param t_spender:
    :param t_id:
    :param revoke:
    :return:
    """
    if len(t_spender) != 20:
        return False

    if len(t_id) == 0:
        t_id = 0

    if len(revoke) == 0:
        revoke = 0

    t_owner = Get(ctx, t_id)

    if len(t_owner) != 20:
        print("token does not exist")
        return False

    if CheckWitness(t_owner):

        approval_key = concat("approved/", t_id)

        if revoke != 0:
            Delete(ctx, approval_key)
            OnApprove(t_owner, t_spender, 0)
            OnNFTApprove(t_owner, '', t_id)
            return True

        # only one third-party spender can be approved
        # at any given time for a specific token

        Put(ctx, approval_key, t_spender)
        OnApprove(t_owner, t_spender, 1)
        OnNFTApprove(t_owner, t_spender, t_id)

        return True

    print("Incorrect permission")
    return False


def do_modify_token(ctx, prefix, t_id, t_data):
    """

    :param ctx:
    :param prefix:
    :param t_id:
    :param t_data:
    :return:
    """
    if len(t_id) == 0:
        t_id = 0

    if CheckWitness(owner):

        exists = Get(ctx, t_id)
        if len(exists) != 20:
            print("token does not exist")
            return False

        urikey = concat(prefix, t_id)
        Put(ctx, urikey, t_data)
        return True

    else:
        print("tx sender lacks permission to modify tokens")
        return False


def do_mint_nft(ctx, t_owner, t_ro, t_rw, t_uri):
    """

    :param ctx:
    :param t_owner:
    :param t_ro:
    :param t_rw:
    :param t_uri:
    :return:
    """
    if CheckWitness(owner):
        t_id = Get(ctx, in_circulation_key)

        if len(t_id) == 0:
            t_id = 0

        exists = Get(ctx, t_id)

        if len(exists) == 20:
            print("token already exists")
            return False

        if len(t_ro) == 0:
            print("missing read-only data string")
            return False

        rokey = concat('ro/', t_id)
        rwkey = concat('rw/', t_id)
        urikey = concat('uri/', t_id)

        Put(ctx, t_id, t_owner)
        Put(ctx, rokey, t_ro)
        Put(ctx, rwkey, t_rw)
        Put(ctx, urikey, t_uri)

        addTokenToOwnersList(ctx, t_owner, t_id)

        new_circulation = t_id + 1
        Put(ctx, in_circulation_key, new_circulation)

        if SafeGetContract(ctx, t_owner):
            auction_contract = DynamicAppCall(t_owner, 'onTokenTransfer')

        return True

    else:
        print("only the contract owner may mint new tokens")
        return False


def removeTokenFromOwnersList(ctx, t_owner, t_id):
    """
    use find instead, rewrite whole template, take away rw method (call ro method properties or something)
    look at machoman nft
    look at nel gladiator nft
    :param ctx:
    :param t_owner:
    :param t_id:
    :return:
    """
    length = Get(ctx, t_owner)
    if len(length) == 0:
        length = 0

    for t_idx in range(0, length):
        tokkey = concat(t_owner, t_idx)
        id = Get(ctx, tokkey)
        if id == t_id:
            lasttoken_idx = length - 1
            swapkey = concat(t_owner, lasttoken_idx)
            swapToken = Get(ctx, t_owner, lasttoken_idx)
            Put(ctx, tokkey, swapToken)
            Delete(ctx, swapkey)
            Put(ctx, lasttoken_idx)
            Put()
            print("removed token from owners list")
            newbalance = length - 1
            if newbalance > 0:
                Put(ctx, t_owner, newbalance)
            else:
                Delete(ctx, t_owner)
            return True
    print("token not found in owners list")
    return False


def addTokenToOwnersList(ctx, t_owner, t_id):
    """

    :param ctx:
    :param t_owner:
    :param t_id:
    :return:
    """
    length = Get(ctx, t_owner)
    if len(length) == 0:
        length = 0
    addkey = concat(t_owner, length)
    Put(ctx, addkey, t_id)
    print("added token to owners list")
    newbalance = length + 1
    Put(ctx, t_owner, newbalance)
