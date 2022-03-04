if [[ -z $GARBAGE_PRIVATE_KEY ]]; then
	echo
	echo "You must set your keys in env/networks.config!"
	echo
	exit 1
fi

sleepTime=300;
while :
do
	date;
	./verifyAllPools.sh;
	echo "Sleeping for $sleepTime seconds"
	sleep $sleepTime;
done
