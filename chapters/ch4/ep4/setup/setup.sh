#!/bin/bash

# CHANGE THESE VALUES TO MATCH YOUR CLOUD BIGQUERY
GCP_PROJECT_ID="deb-01"
BIGQUERY_DATASET_NAME="sandbox_test"


# DSA & local params -- DO NOT CHANGE THESE
DSA_BUCKET="gs://data.datastack.academy/airspace"
DATA_DIR="./data"
AIRPORTS_FILE="deb-airports.csv"
ROUTES_FILE="deb-airports.csv"
AIRLINES_FILE="deb-airports.csv"
AIRCRAFT_FILE="deb-airports.csv"

# create tmp folders
if [ ! -d $DATA_DIR ]; then
    echo "creating ${DATA_DIR} dir"
    mkdir $DATA_DIR
else
    echo "emptying ${DATA_DIR} dir"
    rm -rf $DATA_DIR/*
fi

# download airspace files from DSA to local
gsutil -m cp -r "${DSA_BUCKET}/*.csv" $DATA_DIR

# check to see if files are downloaded
if [ ! -f "${DATA_DIR}/${AIRPORTS_FILE}" ]; then
    echo "${AIRPORTS_FILE} not downloaded"
    exit 1
else
    echo "${AIRPORTS_FILE} downlaoded"
fi

if [ ! -f "${DATA_DIR}/${ROUTES_FILE}" ]; then
    echo "${ROUTES_FILE} not downloaded"
    exit 1
else
    echo "${ROUTES_FILE} downlaoded"
fi

if [ ! -f "${DATA_DIR}/${AIRLINES_FILE}" ]; then
    echo "${AIRLINES_FILE} not downloaded"
    exit 1
else
    echo "${AIRLINES_FILE} downlaoded"
fi

if [ ! -f "${DATA_DIR}/${AIRCRAFT_FILE}" ]; then
    echo "${AIRCRAFT_FILE} not downloaded"
    exit 1
else
    echo "${AIRCRAFT_FILE} downlaoded"
fi

# function to create dataset safely
bq_safe_dataset_mk() {
    dataset=$BIGQUERY_DATASET_NAME
    exists="$(bq ls --project_id=${GCP_PROJECT_ID} --format=sparse -d | grep -w $dataset)"
    if [ -n "$exists" ]; then
        echo "$dataset dataset already exists"
    else
        echo "creating dataset: $dataset"
        bq mk --project_id=${GCP_PROJECT_ID} $dataset
    fi
}

bq_drop_table() {
    table=$1
    dataset=$BIGQUERY_DATASET_NAME
    echo "checking table $table"
    exists="$(bq ls --project_id=$GCP_PROJECT_ID $dataset | grep -w $table)"
    if [ -n $exists ]; then
        echo "table $table already exists"
    else
        echo "table $table does not exist"
    fi
}

bq_safe_dataset_mk

bq_drop_table "airports"
