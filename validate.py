#!/usr/bin/env python3

import os
import sys
import json
import shutil
import pandas
import numpy

#from sklearn.linear_model import LinearRegression
#from sklearn.metrics import mean_squared_error, r2_score
#from sklearn.preprocessing import PolynomialFeatures

from json import encoder
#encoder.FLOAT_REPR = lambda o: format(o, '.2f')

with open('config.json') as config_json:
    config = json.load(config_json)

if config['profiles'] is None:
    print("profiles is not set in config.json")
    sys.exit(1)

results = {"errors": [], "warnings": [], "brainlife": [], "datatype_tags": [], "tags": [], "meta": {
    "tensor_measures": False,
    "noddi_measures": False,
    "csvs": []
}}

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
    shape = None
    for name in os.listdir(config["profiles"]):
        #check file extension
        filename, file_extension = os.path.splitext(name)
        if file_extension != ".csv":
            results["warnings"].append("contains non-csv file:"+name)
            continue

        results["meta"]["csvs"].append(name)

        csv = pandas.read_csv(config["profiles"]+"/"+name)

        if not shape:
            #first csv
            shape = csv.shape
            results["meta"]["nodes"] = shape[0]
            if shape[1] == 16:
                #assume it contains tensor measures (4x4)
                results["meta"]["tensor_measures"] = True
            elif shape[1] == 28:
                #assume it contains tensor and noddi measures (7x4)
                results["meta"]["tensor_measures"] = True
                results["meta"]["noddi_measures"] = True
            else:
                results["errors"].append("csv should have eitehr 16(tensor only) or 28(tensor+noddi) columns");
        else:
            if shape != csv.shape:
                results["errors"].append("csv shape doesn't match for "+name+" "+str(csv.shape))

        #check number of NaNs
        nans = csv["ad_1"].isnull().sum()
        if nans > shape[0]*0.2:
            results["warnings"].append(str(nans/shape[0]*100)+"% of rows are NaNs for "+name)

        if nans == 0:
            #fit 2nd degree polynomial to FA
            #TODO..
            None
            #polynomial_features = PolynomialFeatures(degree=2)
            #x_poly = polynomial_features.fit_transform([csv['ad_1']])
            #model = LinearRegression()
            #model.fit(x_poly, [csv.index.values])
            #print(polynomial_features.get_feature_names())
            #y_poly_pred = model.predict(x_poly)

        csv.to_csv("output/profiles/"+name, index=False, na_rep='NaN')
        csv.to_csv("secondary/profiles/"+name, index=False, na_rep='NaN', float_format="%.6f")

        #let's just copy all the files to secondary..
        #if os.path.lexists("secondary/profiles/"+name):
        #    os.remove("secondary/profiles/"+name)
        #os.symlink("../../output/profiles/"+name, "secondary/profiles/"+name)

with open("product.json", "w") as fp:
    #json.dump(results, fp, cls=NumpyEncoder)
    json.dump(results, fp)

if len(results["errors"]) > 0:
    print("errors detected")
    print(results["errors"])

if len(results["warnings"]) > 0:
    print("warnings detected")
    print(results["warnings"])


