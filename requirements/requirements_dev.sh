#!/bin/bash

cd "$(dirname "$0")"

for x in "8" "9" "10" "11" "12" "13"; do
  "python3.${x}" -m uv pip compile requirements_dev.in \
  --upgrade -v -o requirements_dev-py3${x}.txt &
done

wait
