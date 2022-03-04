if [[ -z $GARBAGE_PRIVATE_KEY ]] && [[ -z $ARG0 ]]; then
	echo
	echo "You must set your keys in env/networks.config!"
	echo
	exit 1
fi

# setup (or activate) your virtual environment
if [ ! -d ./venv ]; then
 	python3 -m venv ./venv
	source ./venv/bin/activate
	python3 -m pip install -r requirements.txt
else
	source ./venv/bin/activate
fi

envPath="./env"
declare -a networks=("mainnet" "kovan" "polygon") # "fantom")
for i in "${networks[@]}"
do
	cd $envPath
	source $i.env
	cd ..
	python generateVerificationScripts.py $i
done

if [ ! -d ./balancer-v2-monorepo ]; then
	git clone https://github.com/balancer-labs/balancer-v2-monorepo.git
	cd balancer-v2-monorepo
	sudo apt-get -y install nodejs npm
	sudo npm install -g yarn
	yarn
	yarn build
	yarn install
	cd -
fi

source $envPath/networks.config
cp hardhat.config.ts.template hardhat.config.ts
sed -i -e "s/GARBAGE_PRIVATE_KEY/$GARBAGE_PRIVATE_KEY/g" hardhat.config.ts
sed -i -e "s/INFURA_API_KEY/$INFURA_API_KEY/g" hardhat.config.ts
mv hardhat.config.ts balancer-v2-monorepo/pkg/deployments/hardhat.config.ts

if [ ! -d ./balancer-v2-monorepo/pkg/deployments/scripts ]; then
	mkdir balancer-v2-monorepo/pkg/deployments/scripts
fi
mv scripts/* balancer-v2-monorepo/pkg/deployments/scripts/
cd balancer-v2-monorepo/pkg/deployments/

for f in ./scripts/*.sh; do
  bash "$f" 
done

deactivate
