import pymongo
import pandas as pd
from pymongo import MongoClient
from joblib import Parallel, delayed
import multiprocessing
import requests
import json
import time
from flask import Flask, render_template, Markup, request, jsonify, make_response

app = Flask(__name__)

def getQueryData(testName=None):
    client = MongoClient('mongodb://onega:27017')
    db = client.AutoRedGreen
    collection = db.QUERY
    if testName is None:
        data = pd.DataFrame(list(collection.find()))
    else:
        data = pd.DataFrame(list(collection.find({"test": testName})))

    return data

def getResults(testName):
    resultDF = getQueryData(testName)
    return resultDF

def processed_result(str1, str2):
    json_data = {'str1': str1, 'str2': str2}
    headers = {
        'Content-Type': 'application/json',
    }
    response = requests.post('http://thames:8080/curldump/', json=json_data, headers=headers)

    return (response.json())

@app.route('/dump/', methods=['POST'])
@app.route('/dump', methods=['POST'])
def dump():
    data = request.json
    testName = data['test']
    checking_string = data['str1']
    all_results = getResults(testName)
    # (self, n_jobs=None, backend=None, verbose=0, timeout=None, pre_dispatch='2 * n_jobs', batch_size='auto', temp_folder=None, max_nbytes='1M', mmap_mode='r', prefer=None, require=None)

    results = Parallel(n_jobs=1, prefer='processes', verbose=100, batch_size=30)(delayed(processed_result)(i['output'], checking_string) for a, i in all_results.iterrows())

    # results = Parallel(n_jobs=1, prefer="threads", verbose=100)(delayed(processed_result)(i['output'], checking_string) for a, i in all_results.iterrows())
    # real    0m13.094s
    # user    0m0.307s
    # sys     0m0.052s

    # results = Parallel(n_jobs=1, backend='threading', verbose=100)(delayed(processed_result)(i['output'], checking_string) for a, i in all_results.iterrows())
    # real    0m13.281s
    # user    0m0.292s
    # sys     0m0.054s

    # results = Parallel(n_jobs=1, verbose=100)(delayed(processed_result)(i['output'], checking_string) for a, i in all_results.iterrows())
    # real    0m13.180s
    # user    0m0.301s
    # sys     0m0.036s    

    # results = Parallel(n_jobs=1, backend='multiprocessing', verbose=100)(delayed(processed_result)(i['output'], checking_string) for a, i in all_results.iterrows())
    # real    0m13.007s
    # user    0m0.274s
    # sys     0m0.059s

    # results = Parallel(n_jobs=2, backend='multiprocessing',verbose=100, pre_dispatch='1.5*n_jobs')(delayed(processed_result)(i['output'], checking_string) for a, i in all_results.iterrows())
    # real    0m19.587s
    # user    0m0.281s
    # sys     0m0.054s

    # finalr = []
    # for a, i in all_results.iterrows():
    #     results = processed_result(i['output'], checking_string)
    #     finalr.append(results)
    # return jsonify(results=finalr)

    # real    0m13.401s
    # user    0m0.325s
    # sys     0m0.041s

    return jsonify(results=results)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)