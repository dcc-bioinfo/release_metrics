#!/bin/bash

while read line
do
    name=$line
    python determineEmbargo.py $name
done <$1
