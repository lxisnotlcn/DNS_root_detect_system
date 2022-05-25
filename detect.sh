#!/bin/bash

for RSI in "$@"
do
{
	file="./raw_data/raw_data_"${RSI:0:1}".txt"
	exec 1> $file
	echo "******"
	date +%Y-%m-%dT%H:%M:%SZ
	echo "******"
	dig @$RSI +noedns +short CHAOS TXT hostname.bind +tcp +norecurse
	echo "******"
	dig @114.114.114.114 www.rssac047.errcom A +norecurse
	
	
}&
done
wait


