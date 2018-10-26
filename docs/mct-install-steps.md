# MCT Install Steps
### Requirements: 
* [neo-python](https://github.com/CityOfZion/neo-python)
* [cityofzion/neo-privatenet](https://hub.docker.com/r/cityofzion/neo-privatenet/)
* [neo-privnet.wallet](https://s3.amazonaws.com/neo-experiments/neo-privnet.wallet) 

### Open a terminal and type the following: 
```
$ np-prompt -p
neo> open wallet {/path/to/neo-privnet.wallet}
neo> import contract {/path/to/mct-privnet.avm} 0710 05 True True False
neo> import token 0xc186bcb4dc6db8e08be09191c6173456144c4b8d
neo> testinvoke 0xc186bcb4dc6db8e08be09191c6173456144c4b8d deploy []
neo> wallet rebuild
neo> wallet
```
