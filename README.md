# balancer-pool-verification

## Usage
- Edit `./env/networks.config` to add Infura API keys, Etherscan API keys, and a (throwaway) private key.
- Run `verifyAllPools.sh` to do one pass of pool verification, or run `keepRunning.sh` to continuously verify pools as they're created

## Note
Etherscan limits you to 100 pool verifications per day (per API key) so if you have a ton of pools to verify, you might want to either swap out API keys or set it up to iterate through a few keys. 
