#!/bin/bash

#read json file
value=`cat product.txt`

#echo $value

# json echo service
curl "http://127.0.0.1:5000/products" -i -H "Content-type: application/json" -X POST -d"$value"

