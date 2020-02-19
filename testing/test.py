import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def getResponse():
    files = {
        'docs': (None, '[{"build":"3042", "suite":".*JCK.*"}]'),
    }
    try:
        response = requests.post('http://onega:8083/AutoRedGreen/_getstaticresults', files=files)
        return response.json()
    except:
        response = {'ok': 0}
        return response

json_results = getResponse()
'''
Index(['_id', 'test', 'status', 'kfdb_status', 'build', 'suite', 'config',
       'rerunCount', 'buildURL', 'testsRun', 'testsPassed', 'cycle', 'id',
       'state', 'evaluation_status', 'sig_sha', 'jira_id', 'jira_info',
       'top_3_fuzzy_matched_info', 'waived', 'failures', 'batch'],
      dtype='object')
'''
if json_results['ok'] == 1:
   data = (json_results['results'])
   df = pd.DataFrame(data)
   print(df.head())
   # sns.relplot(x='kfdb_status', y='id', data=df, hue='cycle')
   # sns.catplot(x='kfdb_status', y='id', hue='cycle', kind='bar', data=df)
   # sns.despine()
   plt.show()




else:
    print('status is not OK')
