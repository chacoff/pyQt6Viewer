import sqlite3
import pandas as pd


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


def export_to_csv(name):
    target_db = f'{name}.db'
    conn_target = sqlite3.connect(target_db)

    query = "SELECT FileName, Ground_truth, Predict FROM seams_processor"
    df = pd.read_sql_query(query, conn_target)
    # df['Ground_truth'].fillna('NoSeams', inplace=True)
    df = df[df['Ground_truth'] != 'None']
    df.to_csv(f'{name}.csv', index=False, encoding="utf-8")
    conn_target.close()


if __name__ == "__main__":
    name = 'ZH026_3260_34K'
    for i in range(1, 52):
        source_db_name = f"seams_processor_{i}.db"
        print(source_db_name.split('/')[-1])
        target_db_name = f"{name}.db"
        merge_databases(source_db_name, target_db_name)
    export_to_csv(name)
