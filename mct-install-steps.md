# MCT Install Steps with `cityofzion/neo-privatenet` docker image and neo-python

`np-prompt -p`
```
neo> open wallet {/path/to/neo-privnet.wallet}
neo> import contract {/path/to/mct-privnet.avm} 0710 05 True True
neo> import token 0xc186bcb4dc6db8e08be09191c6173456144c4b8d
neo> testinvoke 0xc186bcb4dc6db8e08be09191c6173456144c4b8d deploy []
neo> wallet rebuild
neo> wallet
```