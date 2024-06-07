#!/bin/bash
echo "Checking package size is compatable with AWS"

mkdir -p /tmp/droppii_package

pip install . -t /tmp/droppii_package

MAX_SIZE=250000000
PACKAGE_SIZE=$(du -bs /tmp/droppii_package|cut -f1)

echo "
Package size is $PACKAGE_SIZE bytes
"

if [ $PACKAGE_SIZE -gt $MAX_SIZE ]; then
    echo "ERROR: Package size exceeds 250mb"
    rm -R /tmp/droppii_package
    exit 1
fi

rm -R /tmp/droppii_package

