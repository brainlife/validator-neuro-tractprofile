#!/usr/bin/env python3

import os
import sys
import json
import shutil
import pandas

from json import encoder
#encoder.FLOAT_REPR = lambda o: format(o, '.2f')

with open('config.json') as config_json:
    config = json.load(config_json)

if config['profiles'] is None:
    print("profiles is not set in config.json")
    sys.exit(1)

results = {"errors": [], "warnings": [], "brainlife": [], "datatype_tags": [], "tags": [], "meta": {}}

if not os.path.exists("secondary"):
    os.mkdir("secondary")
if not os.path.exists("secondary/profiles"):
    os.mkdir("secondary/profiles")

if not os.path.exists("output"):
    os.mkdir("output")
if not os.path.exists("output/profiles"):
    os.mkdir("output/profiles")

if not os.path.isdir(config["profiles"]):
    results["errors"].append("profiles directory does not exist")
else:
    rows = None
    for name in os.listdir(config["profiles"]):
        #check file extension
        filename, file_extension = os.path.splitext(name)
        if file_extension != ".csv":
            results["warnings"].append("contains non-csv file:"+name)
            continue

        csv = pandas.read_csv(config["profiles"]+"/"+name)
        #print(name)
        #print(csv.shape)
        if not rows:
            rows = csv.shape[0]
            results["meta"]["nodes"] = rows
        else:
            if rows != csv.shape[0]:
                results["errors"].append("row count doesn't match for "+name+" "+str(csv.shape[0]))

        if csv.shape[1] != 16:
            results["errors"].append(name+" should have 16 columns but it has "+str(csv.shape[1]))
                         
        #if os.path.lexists("output/profiles/"+csv):
        #    os.remove("output/profiles/"+csv)
        #os.symlink("../../"+config['profiles']+"/"+csv, "output/profiles/"+csv)

        #print(csv)
        nans = csv["ad_1"].isnull().sum()
        if nans > rows*0.2:
            results["warnings"].append(str(nans/rows*100)+"% of rows are NaNs for "+name)

        csv.to_csv("output/profiles/"+name, index=False, na_rep='NaN', float_format="%.6f")

        #let's just copy all the files to secondary..
        if os.path.lexists("secondary/profiles/"+name):
            os.remove("secondary/profiles/"+name)
        os.symlink("../../output/profiles/"+name, "secondary/profiles/"+name)

with open("product.json", "w") as fp:
    #json.dump(results, fp, cls=NumpyEncoder)
    json.dump(results, fp)

if len(results["errors"]) > 0:
    print("errors detected")
    print(results["errors"])

if len(results["warnings"]) > 0:
    print("warnings detected")
    print(results["warnings"])


