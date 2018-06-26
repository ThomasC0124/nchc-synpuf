#!/bin/bash
sort -t '|' -k1,1 "$1" > "$2"
