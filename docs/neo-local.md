# Deploying the Master Contract Token (MCT) in neo-local
## Requirements: 
* [neo-local](https://github.com/CityOfZion/neo-local)
* [mct-privnet.avm](https://github.com/Splyse/MCT/raw/master/mct-privnet.avm)

## Follow neo-local installation and usage instructions located [here](https://github.com/CityOfZion/neo-local/wiki)
### After your neo-python prompt appears, do the following:
1. Open another terminal window and move mct-privnet.avm to {/path/to/neo-local/smart-contracts/}. Then `exit` the terminal window.
1. In your neo-python prompt, type the following:
```
neo> open wallet ./neo-privnet.wallet
neo> import contract /smart-contracts/mct-privnet.avm 0710 05 True True False
neo> import token 0xc186bcb4dc6db8e08be09191c6173456144c4b8d
neo> testinvoke 0xc186bcb4dc6db8e08be09191c6173456144c4b8d deploy []
neo> wallet rebuild
neo> wallet
```
