import sqlite3
import pandas as pd
from Viewer.src.matrix import create_matrix


def merge_databases(source_db: str, target_db: str) -> None:
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


def export_to_csv(name: str) -> None:
    """ name of the database, without extension is the only parameter """
    target_db = f'{name}.db'
    conn_target = sqlite3.connect(target_db)

    query = "SELECT FileName, Ground_truth, Predict FROM seams_processor"
    df = pd.read_sql_query(query, conn_target)
    # df['Ground_truth'].fillna('NoSeams', inplace=True)
    df = df[df['Ground_truth'] != 'None']
    df.to_csv(f'{name}.csv', index=False, encoding="utf-8")
    conn_target.close()


def create_filtered_db(original_db: str, filter_prefix: str) -> None:
    """ from one database creates several databases by filtering the profile in FileName """
    new_db_name = f"{filter_prefix}_filtered.db"

    original_conn = sqlite3.connect(original_db)
    original_cursor = original_conn.cursor()

    original_cursor.execute("PRAGMA table_info(seams_processor)")
    columns = [column[1] for column in original_cursor.fetchall()]

    new_conn = sqlite3.connect(new_db_name)
    new_cursor = new_conn.cursor()

    create_table_query = f"CREATE TABLE IF NOT EXISTS seams_processor ({', '.join(columns)})"
    new_cursor.execute(create_table_query)

    original_cursor.execute(f"SELECT * FROM seams_processor WHERE FileName LIKE '{filter_prefix}%'")
    new_cursor.executemany(f"INSERT INTO seams_processor VALUES ({', '.join(['?'] * len(columns))})",
                           original_cursor.fetchall())

    new_conn.commit()
    new_conn.close()
    original_conn.close()


def main(_name: str) -> None:
    for i in range(1, 46):
        source_db_name = f"ZH024-026-028-030\\seams_processor_{i}.db"
        print(source_db_name.split('/')[-1])
        target_db_name = f"{_name}.db"
        merge_databases(source_db_name, target_db_name)


if __name__ == "__main__":
    skip_matrix = False
    skip_merge = True
    skip_split = True

    # normal matrix calculation
    if not skip_matrix:
        name = 'ZH030_filtered'
        if not skip_merge:
            main(name)
        export_to_csv(name)
        create_matrix(f'{name}.png', f'{name}.csv')

    # To split database according FileName, in case there is a mix of profiles
    if not skip_split:
        original_db = 'ZH024_026-028-030.db'
        filters = ['ZH024', 'ZH026', 'ZH028', 'ZH030']

        for filter_prefix in filters:
            create_filtered_db(original_db, filter_prefix)
            print(f"Filtered database for {filter_prefix} created.")
