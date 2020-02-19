import requests
import argparse
import pandas as pd

argparser = argparse.ArgumentParser()
# argparser.add_argument('--buildno', type=str, default="20.01.0.0-b3")
argparser.add_argument('--buildno', type=str, default="3036")
args = argparser.parse_args()

def getResponse():
    buildno = args.buildno
    aa = f'"build":"{buildno}"'
    files = {
        'docs': (None, '[{'+aa+', "suite":".*JCK.*"}]'),
    }
    try:
        response = requests.post('http://onega:8083/AutoRedGreen/_getstaticresults', files=files)
        return response.json()
    except:
        response = {'ok': 0}
        return response

data = getResponse()
df = pd.DataFrame(data['results'])
print(df)