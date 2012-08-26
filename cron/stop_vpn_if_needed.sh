#!/bin/bash

# run as root

ip=`grep bind-address-ipv4 /etc/transmission-daemon/settings.json | cut -c 27- | sed -e 's/\",//g' ` 
if [[ $ip == '0.0.0.0' ]] ; then
	/etc/init.d/tranmission-daemon stop;
fi
