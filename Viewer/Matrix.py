import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


def create_matrix():
    sns.set_style("whitegrid")
    main_source = f'..'
    source = f'{main_source}\\ZH.csv'
    name = 'ZH018'  # (source.split('\\')[-1]).split('.')[0]
    df = pd.read_csv(source)
    df.index += 1

    y_pred = df['Ground_truth']
    y_test = df['Predict']
    labels = y_test.unique()
    labels.sort()

    c_pred = y_pred.value_counts(dropna=False)
    p_pred = y_pred.value_counts(dropna=False, normalize=True).mul(100).round(2)
    pred = pd.concat([c_pred, p_pred], axis=1, keys=['counts', '%'])

    c_test = y_test.value_counts(dropna=False)
    p_test = y_test.value_counts(dropna=False, normalize=True).mul(100).round(2)
    test = pd.concat([c_test, p_test], axis=1, keys=['counts', '%'])

    brief = f'\nPREDICTIONS\n{pred}\n\nGROUND TRUTH\n{test}'


    cf_matrix = confusion_matrix(y_test, y_pred)
    # print(cf_matrix)

    # ax = sns.heatmap(cf_matrix, annot=True, cmap='Blues', fmt='g')
    ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True, fmt='.2%', cmap='Oranges')

    ax.set_title('TMB Seams - Confusion Matrix')
    ax.set_xlabel('Predicted Values')
    ax.set_ylabel('Actual Values ')

    ax.xaxis.set_ticklabels(labels)
    ax.yaxis.set_ticklabels(labels)

    # plt.show()
    lastname = os.path.join('matrix', 'confusion_matrix.png')
    plt.savefig(lastname, bbox_inches='tight', dpi=199)