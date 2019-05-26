#!/bin/sh

# Shell script to launch machine learning experiments.

# This is a template to use as a starting point for creating
# your own script files. Please do not overwrite it.

# Allows you to set up each experiment with unique arguments
# which are sent to main.py at execution time. It also handles
# the creation of output log directories and other file-system
# operations allowing you to automate the execution of multiple
# scipts using a scheduler such as jobdispatcher.py.

# Instructions for use:
# Make sure the paths are correct and execute from the command
# line using:
# $ ./yourscript.sh
# You will have to change file permissions before you can
# execute it:
# $ chmod +x yourscript.sh


MODEL='LeNet'

# Setup
TIMESTAMP=`date +%y%m%d%H%M%S`  # Use this in LOGDIR (optional)
FILENAME=`basename "$0"`  # Use this in --label (optional)
DATASET='mnist'   # Use the dataset name in LOGDIR (recommended)
DATADIR='/../data/'  # This could be a shared data file store

BASELOG='../logs/'$DATASET/$MODEL
LOGDIR=$BASELOG/$TIMESTAMP

mkdir -p $DATADIR
mkdir -p $BASELOG


python -u ../main.py \
    --model $MODEL \
    --dataset $DATASET \
    --data-dir $DATADIR \
    --log-dir $LOGDIR \
    --comment 'Template script' \
    --batch-size 128 \
    --dropout 0.2 \
    --log-interval 100 \
    --epochs 50 \
    --optimizer SGD \
    --momentum 0.9 \
    --lr 0.1 \
    --lr-schedule '[[0,1],[25,0.1]]' \
    --label $FILENAME \
    > $LOGDIR/log.out 2>&1 # Write stdout directly to log.out
                           # if you want to see results in real time,
                           # use tail -f

