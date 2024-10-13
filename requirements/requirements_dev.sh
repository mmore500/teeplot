#!/bin/bash

for x in "7" "8" "9" "10" "11"; do
  "python3.${x}" -m uv pip compile requirements_dev.in \
  --upgrade -v -o requirements_dev-py3${x}.txt &
done

wait
