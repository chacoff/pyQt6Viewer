import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

FILE_PATH = 'ZH026_3260_34K_excluded_Datetime.csv'
OUTPUT_FILE_PATH = 'cluster_finder_output.csv'
TIME_DIFFERENCE_THRESHOLD = 1


def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df['Modification Date'] = pd.to_datetime(df['Modification Date'])
    df = df.sort_values(by='Modification Date')
    df['Time Difference'] = df['Modification Date'].diff().dt.total_seconds() / 60
    df['Cluster'] = (df['Time Difference'].isnull() | (df['Time Difference'] > TIME_DIFFERENCE_THRESHOLD)).cumsum()
    return df


def save_data_to_csv(df, output_file_path):
    df.to_csv(output_file_path, index=False)


def plot_data(df):
    images_per_cluster = df['Cluster'].value_counts()
    df_images_per_cluster = pd.DataFrame({'Cluster': images_per_cluster.index, 'Images': images_per_cluster.values})

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='Cluster', y='Images', data=df_images_per_cluster, ax=ax, color='skyblue', errorbar=None)

    ax.set_title('Number of Images per Cluster', fontsize=16)
    ax.set_xlabel('Cluster', fontsize=14)
    ax.set_ylabel('Number of Images', fontsize=14)

    for i in ax.containers:
        ax.bar_label(i)
    plt.show()


def main():
    # Perform all actions
    df = preprocess_data(FILE_PATH)
    save_data_to_csv(df.loc[:, ["File", "Path", "Modification Date", "Cluster"]], OUTPUT_FILE_PATH)
    plot_data(df)


# Call the main function
if __name__ == "__main__":
    main()
