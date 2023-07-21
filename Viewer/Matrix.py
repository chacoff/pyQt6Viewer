import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sqlite3
sns.set_style("whitegrid")


# TODO @Pierrick, please turn it into a class
def create_matrix(image_path, matrix_csv):

    df = pd.read_csv(matrix_csv)
    df.index += 1

    y_pred = df['Predict']
    y_test = df['Ground_truth']
    labels = y_pred.unique()
    labels.sort()
    print(labels)

    cf_matrix = confusion_matrix(y_test, y_pred)

    ax = sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True, fmt='.2%', cmap='Oranges')

    ax.set_title('TMB Seams - Confusion Matrix')
    ax.set_xlabel('Predicted Values')
    ax.set_ylabel('Actual Values ')

    ax.xaxis.set_ticklabels(labels)
    ax.yaxis.set_ticklabels(labels)

    plt.savefig(image_path, bbox_inches='tight', dpi=199)
    plt.clf()


def merge_databases(source_db, target_db):
    conn_target = sqlite3.connect(target_db)
    cursor_target = conn_target.cursor()

    conn_source = sqlite3.connect(source_db)
    cursor_source = conn_source.cursor()

    cursor_source.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor_source.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Merging table: {table_name}")

        cursor_source.execute(f"PRAGMA table_info('{table_name}')")
        columns = cursor_source.fetchall()
        column_names = [col[1] for col in columns]

        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(f'{col} TEXT' for col in column_names)})"
        cursor_target.execute(create_table_query)

        select_query = f"SELECT {', '.join(column_names)} FROM {table_name}"
        cursor_source.execute(select_query)
        rows = cursor_source.fetchall()

        insert_query = f"INSERT OR REPLACE INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
        cursor_target.executemany(insert_query, rows)

    conn_target.commit()
    conn_target.close()
    conn_source.close()


def export_to_csv(target_db):
    conn_target = sqlite3.connect(target_db)

    query = "SELECT FileName, Ground_truth, Predict FROM seams_processor"
    df = pd.read_sql_query(query, conn_target)
    # df['Ground_truth'].fillna('NoSeams', inplace=True)
    df = df[df['Ground_truth'] != 'None']
    df.to_csv("merged_data.csv", index=False, encoding="utf-8")
    conn_target.close()


def print_a_brief(matrix_csv):
    df = pd.read_csv(matrix_csv)
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
    print(brief)


def main():
    create_matrix('../trials/super_matrix.png', '../trials/merged_data.csv')


if __name__ == '__main__':
    main()
