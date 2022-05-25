#!/bin/bash

REF_ipv6=(2400:3200::1 2409:8088::a 2402:4e00::)

i=0
for var in "$@"
do
	env[$i]=$var
	i=`expr $i + 1`
done

for((j=0;j<$i-2;j++))
do
	ip_addr[$j]=${env[$j+2]}
done

for RSI in ${ip_addr[@]}
do
{
	file="./raw_data/ipv6/raw_data_"${RSI:0:1}".txt"
	exec 1> $file
	echo "******"
	dig -6 TXT +short o-o.myaddr.l.google.com @ns1.google.com
#	for ns in $(dig +short akamai.net NS) 
#	do 
#		dig -6 +short @$ns whoami.akamai.net AAAA
#	done
	echo "******"
	dig @$RSI . SOA +norecurse -6
	echo "******"
	dig @$RSI . SOA +norecurse -6 +tcp
	
	if [ "${env[0]}" = "-t" ]
	then
		echo "******"
		traceroute -I $RSI -6
	fi
	
	if [ "${env[1]}" = "-r" ]
	then
		for REF in ${REF_ipv6[@]}
		do
			echo "******"
			dig @$REF . SOA +norecurse
		done
	fi
	
}&
done
wait






