#!/bin/sh

echo -------------------------------- > list.fbd
date >> list.fbd
echo $1 >> list.fbd
find $1 -type f -exec ls -l --full-time {} \; -exec sha1sum {} \; >> list.fbd