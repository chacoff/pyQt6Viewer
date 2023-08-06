import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


def kmeans_fit(_df: pd, _n_clus: int, _state: int) -> pd:

    kmeans = KMeans(n_clusters=_n_clus, random_state=_state)
    _df['Cluster'] = kmeans.fit_predict(_df[['Timestamp']])

    return _df


def timestamp_transform(_df: pd) -> pd:

    _df['Modification Date'] = pd.to_datetime(_df['Modification Date'])
    _df['Timestamp'] = _df['Modification Date'].astype('int64') // 10 ** 9

    scaler = StandardScaler()
    _df['Timestamp'] = scaler.fit_transform(_df[['Timestamp']])

    return _df


def main() -> None:

    # Parameters
    file_path = 'ZH026_3260_34K_Datetime.csv'
    output_path = 'ZH026_3260_34K_Datetime_clustered_data.csv'

    df = pd.read_csv(file_path)
    df = timestamp_transform(df)
    df = kmeans_fit(df, 270, 0)

    df.to_csv(output_path, index=False)

    show: bool = False
    if show:
        plt.scatter(df['Timestamp'], [0] * len(df), c=df['Cluster'], cmap='Oranges')
        plt.xlabel('Standardized Timestamp')
        plt.ylabel('Cluster')
        plt.show()


if __name__ == "__main__":
    main()


