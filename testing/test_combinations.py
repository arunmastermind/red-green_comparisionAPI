import numpy as np
import pandas as pd

ks = ['unexpected', 'waived', 'flakey', 'known', 'rerun', 'no_status', 'recurrence_unexpected']
es = ['unexpected', 'waived', 'flakey', 'known', 'unexpected_new', 'waived_new', 'flakey_new', 'known_new']

for i in ks:
    for j in es:
        print(i, j)
