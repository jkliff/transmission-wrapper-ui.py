#!/bin/bash

# run as transmittion-debian

DEBUG=
REMOTE_BASE=/home/transmission

REMOTE="ssh torrents@svpnproxy"
TRANS="$REMOTE transmission-remote --auth=transmission:transmission"

# for every complete torrent
for f in `$TRANS -l | awk '{print $1, $2}' | grep 100% | awk '{print $1}'` ; do
    # stop the transfer
    $DEBUG $TRANS -t $f -S;
    # move to the shared directory
    $DEBUG $TRANS -t $f --move "$REMOTE_BASE/done" ;
done
