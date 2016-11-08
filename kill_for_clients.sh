#!/bin/bash

echo "Existing fort process"
ps -ef | grep fort
echo "Killing them"
ps -ef | grep fort | awk '{print $2} ' | xargs sudo kill -9
echo "Rechecking"
ps -ef | grep fort
echo "Your /etc/resolv.conf is"
echo "------------------------"
cat /etc/resolv.conf
echo "========================"
echo "Tmp /etc/resolv.conf is"
echo "------------------------"
cat /tmp/resolv.conf.orig
echo "========================"
echo -n "Replace(y/n):"
read repl
if [[ "x$repl" -eq "xy" ]] ; then
  sudo cp /tmp/resolv.conf.orig /etc/resolv.conf
fi
