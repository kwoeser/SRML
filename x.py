


import pandas as pd

#define DataFrame
df = pd.DataFrame({'points': [25, 12, 15, 14],
                   'assists': [5, 7, 13, 12]})

#view DataFrame
print(df)


"""
   points  assists
0      25        5
1      12        7
2      15       13
3      14       12
"""


import numpy as np

#attempt to add 'rebounds' column
#df['rebounds'] = np.array([3, 3, 7])

#attempt to add 'rebounds' column
p = df['rebounds'] = pd.Series([3, 3, 7])

print(p)
