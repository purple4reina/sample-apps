#!/bin/bash

cmd=$@

source /data/env/bin/activate

exec $cmd
