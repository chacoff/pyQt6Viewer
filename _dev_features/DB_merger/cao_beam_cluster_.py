import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def kmeans_fit(_df: pd.DataFrame, _n_clus: int, _state: int) -> pd.DataFrame:
    kmeans = KMeans(n_clusters=_n_clus, random_state=_state, n_init=10)
    _df['Cluster'] = kmeans.fit_predict(_df[['Timestamp']])
    return _df


def timestamp_transform(_df: pd) -> pd:
    _df['Modification Date'] = pd.to_datetime(_df['Modification Date'])
    _df['Timestamp'] = _df['Modification Date'].astype('int64') // 10**9

    scaler = StandardScaler()
    _df['Timestamp'] = scaler.fit_transform(_df[['Timestamp']])

    return _df


def find_optimal_clusters(data, max_k):
    iters = range(2, max_k + 1, 2)

    sse = []
    for k in iters:
        sse.append(KMeans(n_clusters=k, random_state=0, n_init=10).fit(data).inertia_)

    # Compute the difference in inertia
    diff = np.diff(sse)
    diff_r = diff[1:] / diff[:-1]

    # Compute the "elbow"
    elbow = np.argmin(diff_r) + 2  # adding 2 because the indices start at 0

    # Plot the elbow curve
    # f, ax = plt.subplots(1, 1)
    # ax.plot(iters, sse, marker='o')
    # ax.set_xlabel('Cluster Centers')
    # ax.set_xticks(iters)
    # ax.set_xticklabels(iters)
    # ax.set_ylabel('SSE')
    # ax.set_title('SSE by Cluster Center Plot')
    # plt.show()

    return elbow


def main() -> None:
    file_path = 'ZH026_3260_34K_excluded_Datetime.csv'
    output_path = 'beam_cluster_output.csv'
    df = pd.read_csv(file_path)
    df = timestamp_transform(df)

    n_clusters = find_optimal_clusters(df[['Timestamp']], 20)
    df = kmeans_fit(df, n_clusters, 0)

    # Save the data to a csv file
    df.loc[:, ["File", "Path", "Modification Date", "Cluster"]].to_csv(output_path, index=False)

    # Plot the distribution of images per cluster
    cluster_counts = df['Cluster'].value_counts().sort_index()
    plt.bar(cluster_counts.index, cluster_counts.values)
    plt.xlabel('Cluster')
    plt.ylabel('Number of Images')
    plt.title('Distribution of Images per Cluster')
    plt.show()


if __name__ == "__main__":
    main()
