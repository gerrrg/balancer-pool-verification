sleepTime=300;
while :
do
	date;
	./verifyAllPools.sh;
	echo "Sleeping for $sleepTime seconds"
	sleep $sleepTime;
done
