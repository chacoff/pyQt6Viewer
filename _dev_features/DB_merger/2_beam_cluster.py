import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns


def kmeans_fit(_df: pd, _n_clus: int, _state: int, _key: str) -> pd:

    kmeans = KMeans(n_clusters=_n_clus, random_state=_state, n_init=10)
    _df[_key] = kmeans.fit_predict(_df[['Timestamp']])

    return _df


def timestamp_transform(_df: pd, _key: str) -> pd:

    _df[_key] = pd.to_datetime(_df[_key])
    _df['Timestamp'] = _df[_key].astype('int64') // 10 ** 9

    scaler = StandardScaler()
    _df['Timestamp'] = scaler.fit_transform(_df[['Timestamp']])

    return _df


def plot_data(df):
    images_per_cluster = df['Cluster'].value_counts()
    df_images_per_cluster = pd.DataFrame({'Cluster': images_per_cluster.index, 'Images': images_per_cluster.values})

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='Cluster', y='Images', data=df_images_per_cluster, ax=ax, color='skyblue', errorbar=None)

    ax.set_title('Number of Images per Cluster', fontsize=16)
    ax.set_xlabel('Beam', fontsize=14)
    ax.set_ylabel('Number of Images', fontsize=14)

    for i in ax.containers:
        ax.bar_label(i)
    plt.show()


def main() -> None:

    # Parameters
    file_path = 'ZH026_3260_34K_Datetime.csv'
    output_path = 'ZH026_3260_34K_Datetime_clustered_data.csv'

    df = pd.read_csv(file_path)
    df = timestamp_transform(df, _key='Modification Date')
    df = kmeans_fit(df, 195, 0, _key='Cluster')

    df.to_csv(output_path, index=False)

    plot_data(df)
    # df.Cluster.value_counts()[df.Cluster.unique()].plot(kind='bar')  # value_counts()
    # plt.show()


if __name__ == "__main__":
    main()


