#!/bin/sh
find . -name "*.py" -print | zip dependencies.zip -@
PYSPARK_PYTHON=/usr/bin/python3 spark-submit --py-files dependencies.zip ./open990/csv2parquet.py $@
