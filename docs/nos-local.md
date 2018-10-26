# Deploying the Master Contract Token (MCT) in nos-local

## Install

These instructions assume you are already running the nos-local Docker container. To install and deploy MCT in your nos-local privatenet, first copy the compiled MCT smart contract AVM to the container.
```
git clone https://github.com/Splyse/MCT
cd MCT
docker cp mct-privnet.avm {docker container}:/smart-contracts
```

## Deploy (inside nos-local neo-python session)
```
import contract /smart-contracts/mct-privnet.avm 0710 05 True True False
```
Type the wallet owner password (coz) at the prompt and wait for the tx to be persisted.

## Import the token
There is a bug in neo-python which forces you to restart neo-python after importing the contract before the token can be imported. 
If you exit neo-python in nos-local, it will end your docker session. *Do not* run the `make run` command again as this will 
create a new privatenet chain and restart from scratch.

Instead, exit neo-python, returning to the host shell prompt, and run:
```
docker exec -it neo-python /bin/bash
cd /neo-python
np-prompt -p
```
At this point you should be back in the neo-python prompt, where you can import the token with:
```
open wallet ./neo-privnet.wallet
import token c186bcb4dc6db8e08be09191c6173456144c4b8d
```
which should result in:
```
added token {
    "name": "Master Contract Token",
    "symbol": "MCT",
    "decimals": 8,
    "script_hash": "0xc186bcb4dc6db8e08be09191c6173456144c4b8d",
    "contract_address": "AUey8HaH4p29YXXE85iJYM6TuzmWZodrsj"
} 
```

At this point you can run
```
testinvoke c186bcb4dc6db8e08be09191c6173456144c4b8d deploy []
```
to receive the owner's allocation of MCT (12,558,000 tokens) in your wallet. See https://github.com/Splyse/MCT for details on implementing MCT support in your contract.

## Development support
Please join the #support channel in the MCT Discord for additional assistance in developing smart contracts to work with MCT.

https://discord.gg/vrA8tcq
```
