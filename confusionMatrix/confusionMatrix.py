import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
argparser = argparse.ArgumentParser()
argparser.add_argument('--buildno', type=str, default=3036)
args = argparser.parse_args()

def getResponse():
    buildno = args.buildno
    build = f'"build":"{buildno}"'
    files = {
        'docs': (None, '[{'+build+', "suite":".*JCK.*"}]'),
    }
    try:
        response = requests.post('http://onega:8083/AutoRedGreen/_getstaticresults', files=files)
        return response.json()
    except:
        response = {'ok': 0}
        return response


def checkTP(kfdb_status, evaluation_status):
    if ((evaluation_status.lower() != 'unexpected')
            and ((kfdb_status.lower() == evaluation_status.lower())
                 or (kfdb_status.lower() == 'flaky' and evaluation_status.endswith('_new'))
                 or (kfdb_status.lower() == 'known') and evaluation_status.lower != 'unexpected_new')):
        return True
    else:
        return False


def checkTN(kfdb_status, evaluation_status):
    if ((
            (kfdb_status.lower() == 'unexpected' or kfdb_status.lower() == 'recurrence_unexpected')
            and (evaluation_status.lower() == 'unexpected' or evaluation_status.endswith('_new'))
    )):
        return True
    else:
        return False


def checkFP(kfdb_status, evaluation_status):
    if (
            (kfdb_status.lower() == 'waived' or kfdb_status.lower() == 'flaky')
        and (kfdb_status.lower() != evaluation_status.lower() and not evaluation_status.endswith('_new'))
    ):

        return True
    else:
        return False


def checkFN(kfdb_status, evaluation_status):
    if (
            (kfdb_status.lower() == 'unexpected' or kfdb_status.lower() == 'recurrence_unexpected')
        and ( evaluation_status.lower() != 'unexpected' and not evaluation_status.endswith('_new') )
    ):
        return True
    else:
        return False


def confusionMatrix():
    pass


def precision(cm):
    '''
    precision = True Positive/Actual Results
    precision = TP/TP+FP
    '''
    actual_result = cm['tp'] + cm['fp']
    try:
        precision = cm['tp'] / actual_result
    except:
        precision = 'undefined'
    return precision


def recall(cm):
    '''
    recall = True Positive/Predicted Results
    recall = TP/TP+FN
    '''
    predicted_result = cm['tp'] + cm['fn']
    try:
        recall = cm['tp'] / predicted_result
    except:
        recall = 'undefined'
    return recall

def plot(json_results):
    data = (json_results['results'])
    df = pd.DataFrame(data)
    kfdb = sns.catplot(x='kfdb_status', kind='count', palette='ch:0.95', data=df, hue='cycle')
    eval = sns.catplot(x='evaluation_status', kind='count', palette='ch:0.95', data=df, hue='cycle')
    kfdb.savefig("kfdb.png")
    eval.savefig("eval.png")

def extractMode(build):
    buildid = build.split()
    mode = buildid[-3].split('-')
    return(mode[-3])

json_results = getResponse()
confusion_matrix_gold = {'tp': 0,
                    'tn': 0,
                    'fp': 0,
                    'fn': 0,
                    'unaccounted': 0}
confusion_matrix_silver = {'tp': 0,
                    'tn': 0,
                    'fp': 0,
                    'fn': 0,
                    'unaccounted': 0}

if json_results['ok'] == 1:
    # print(f'kfdb\tEval\ttp\t\ttn\t\tfp\t\tfn\n-------------------------------------------------')
    # print(f'kfdb|Eval|tp|tn|fp|fn')
    plot(json_results)
    for result in json_results['results']:
        try:
            # print(f'{result["kfdb_status"]} - {result["evaluation_status"]}' )
            fn = checkFN(result["kfdb_status"], result["evaluation_status"])
            fp = checkFP(result["kfdb_status"], result["evaluation_status"])
            tn = checkTN(result["kfdb_status"], result["evaluation_status"])
            tp = checkTP(result["kfdb_status"], result["evaluation_status"])
            # print(f'{result["kfdb_status"]} - {result["evaluation_status"]}\t{tp}\t{tn}\t{fp}\t{fn}')
            # print(f'{result["kfdb_status"]}|{result["evaluation_status"]}|{tp}|{tn}|{fp}|{fn}')
            # print(result)
            mode = extractMode(result['build'])
            if tp:
                if result["cycle"] == 'Silver':
                    confusion_matrix_silver['tp'] += 1
                elif result["cycle"] == 'Gold':
                    confusion_matrix_gold['tp'] += 1
            elif tn:
                print(f'{result["cycle"]} | {result["config"]["name"]} | {mode} | {result["suite"]} | {result["test"]} | {result["kfdb_status"]} | {result["evaluation_status"]} | {tp}|{tn}|{fp}|{fn}')
                if result["cycle"] == 'Silver':
                    confusion_matrix_silver['tn'] += 1
                elif result["cycle"] == 'Gold':
                    confusion_matrix_gold['tn'] += 1
            elif fp:
                if result["cycle"] == 'Silver':
                    confusion_matrix_silver['fp'] += 1
                elif result["cycle"] == 'Gold':
                    confusion_matrix_gold['fp'] += 1
            elif fn:
                if result["cycle"] == 'Silver':
                    confusion_matrix_silver['fn'] += 1
                elif result["cycle"] == 'Gold':
                    confusion_matrix_gold['fn'] += 1
            else:
                if result["cycle"] == 'Silver':
                    confusion_matrix_silver['unaccounted'] += 1
                elif result["cycle"] == 'Gold':
                    confusion_matrix_gold['unaccounted'] += 1
        except:
            # print(result)
            pass
else:
    print('No response from API!!!')
    exit(1)

precision_gold = precision(confusion_matrix_gold)
recall_gold = recall(confusion_matrix_gold)
print('#'*70)
print(f'\nConfusion Matrix Gold:\n{confusion_matrix_gold}\n')
print(f'PRECISION: TP/TP+FP\n{precision_gold}\n')
print(f'RECALL: TP/TP+FN\n{recall_gold}\n')
print('-'*70)

precision_silver = precision(confusion_matrix_silver)
recall_silver = recall(confusion_matrix_silver)

print(f'\nConfusion Matrix Silver:\n{confusion_matrix_silver}\n')
print(f'PRECISION: TP/TP+FP\n{precision_silver}\n')
print(f'RECALL: TP/TP+FN\n{recall_silver}\n')
print('#'*70)