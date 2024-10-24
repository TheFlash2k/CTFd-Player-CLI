#!/bin/bash

[[ -z "$1" ]] && echo "Usage: $0 <flag>" && exit 1
ctfd --skip --config-dir "{CONFIG_DIR}" submit --challenge-id {CHALLENGE_ID} --flag "$1"