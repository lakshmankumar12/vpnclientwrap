#!/bin/sh

echo "Existing fort process"
ps -ef | grep fort
echo "Killing them"
ps -ef | grep fort | awk '{print $2} ' | xargs sudo kill -9
echo "Rechecking"
ps -ef | grep fort
