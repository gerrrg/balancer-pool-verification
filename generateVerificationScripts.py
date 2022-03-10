import balpy
import os
import requests
from pathlib import Path
import json
import sys

import balpy.graph.graph as balGraph

def writeToJson(data, filename, maxRetries = 5):
	retries = 0;
	while retries < maxRetries:
		try:
			with open(filename, 'w') as outfile:
				json.dump(data, outfile);
				break;
		except:
			print("Write attempt", retries, "of", maxRetries, "failed!")
			retries += 1;
def main():

	networks = ["mainnet", "kovan", "polygon", "fantom", "goerli", "rinkeby"];
	verbose = False;

	if len(sys.argv) < 2:
		print("Usage: python", sys.argv[0], "<network>");
		quit();
	network = sys.argv[1];
	if not network in networks:
		print("Network", network, "is not supported! Please use a supported network:");
		for n in networks:
			print("\t" + n);
			quit();

	savePath = "./scripts"
	cachePath = "./cache"
	Path(savePath).mkdir(parents=True, exist_ok=True)
	Path(cachePath).mkdir(parents=True, exist_ok=True)

	# for network in networks:
	bal = balpy.balpy.balpy(network);

	verifiedPools = set();
	cachedVerifiedPools = os.path.join(cachePath, network + ".json");
	if os.path.exists(cachedVerifiedPools):
		try:
			with open(cachedVerifiedPools, 'r') as f:
				verifiedPoolsList = json.load(f);
				verifiedPools = set(verifiedPoolsList);
		except json.decoder.JSONDecodeError:
			print("JSONDecodeError! Running without cache...")

	unableToVerifyPools = set();
	cachedUnverifiedPools = os.path.join(cachePath, network + "_failed.json");
	if os.path.exists(cachedUnverifiedPools):
		try:
			with open(cachedUnverifiedPools, 'r') as f:
				unableToVerifyPoolsList = json.load(f);
				unableToVerifyPools = set(unableToVerifyPoolsList);
		except json.decoder.JSONDecodeError:
			print("JSONDecodeError! Running without cache...")
	
	print("Querying pool data from the Balancer Subgraph...")

	customUrl = None;
	usingJsonEndpoint = False;

	if network == "fantom":
		customUrl = "https://graph-node.beets-ftm-node.com/subgraphs/name/beethovenx";
		usingJsonEndpoint = True;

	bg = balGraph.TheGraph(network, customUrl, usingJsonEndpoint)
	pools = bg.getV2PoolIDs(batch_size=100, verbose=verbose);
	poolData = pools["pools"]

	for poolType in poolData.keys():
		poolIds = poolData[poolType];
		for poolId in poolIds:
			scriptName = "verify" + poolId + ".sh";
			scriptPath = os.path.join(savePath, scriptName);

			try:
				if poolId in verifiedPools or poolId in unableToVerifyPools:
					print("\tPool is verified (source: cache)")
					continue;
				isVerified = bal.isContractVerified(poolId, verbose=verbose);
				if isVerified:
					print("\tPool is verified (source: Etherscan)")
					verifiedPools.add(poolId);
					writeToJson(list(verifiedPools), cachedVerifiedPools);
					continue;
				else:
					#if not os.path.exists(scriptPath):
					print("Verifying:", network, poolType, poolId);
					command = bal.balGeneratePoolCreationArguments(poolId, verbose=verbose);
					#else:
						#print("\tVerification script already exists!")
						#print("\tRegenerating it anyway with hopefully different Etherscan API key");
                                                    #continue;
				
			except KeyboardInterrupt:
				print("Caught Ctrl+C! Quitting...");
				quit();
			except:
				print("\tUnable to generate verification");
				unableToVerifyPools.add(poolId)
				writeToJson(list(unableToVerifyPools), cachedUnverifiedPools);
				continue;

			scriptOutput = "";
			scriptOutput += command + " && ";
			scriptOutput += "rm " + scriptPath + "\n";
			
			with open(scriptPath, 'w') as f:
				f.write(scriptOutput);
			print("\tVerification script created!")
	
if __name__ == '__main__':
	main();
