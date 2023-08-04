import os
import pandas as pd
from PIL import Image
from datetime import datetime
from tqdm import tqdm


def get_creation_date(_filepath: str) -> any:
    try:
        img = Image.open(_filepath)
        info = img._getexif()
        if 36867 in info:
            return info[36867]
        return None
    except Exception as e:
        return None


def get_modified_date(_filepath: str) -> any:
    try:
        modification_timestamp = os.path.getmtime(_filepath)
        modification_date = datetime.fromtimestamp(modification_timestamp).isoformat()
        return modification_date
    except Exception as e:
        return None


def search_bmp_images_from_csv(_folder_path: str, _csv_filename: str) -> list:

    df = pd.read_csv(_csv_filename)

    image_list = df['FileName'].str.strip().str.lower().str.endswith('.bmp')
    image_list = df.loc[image_list, 'FileName'].tolist()

    found_images = []

    for root, dirs, files in os.walk(_folder_path):
        pbar = tqdm(total=len(files))
        for _filename in files:
            if _filename.lower().endswith('.bmp') and _filename in image_list:
                _filepath = os.path.join(root, _filename)
                _creation_date = get_creation_date(_filepath)
                if _creation_date is None:
                    _creation_date = get_modified_date(_filepath)
                found_images.append((_filename, _filepath, _creation_date))
            pbar.update(1)
        pbar.close()

    return found_images


def main() -> None:
    # Parameters
    folder_path = 'S:\\Defects_all\\DefectsYolo\\ZH026\\3260\\Beam'
    csv_filename = 'ZH026_3260_34K.csv'
    output_csv_path = 'ZH026_3260_34K_Datetime.csv'

    results = search_bmp_images_from_csv(folder_path, csv_filename)

    if results:
        for filename, filepath, creation_date in results:
            print(f"File: {filename}, Path: {filepath}, Creation Date: {creation_date}")

        df_results = pd.DataFrame(results, columns=['File', 'Path', 'Modification Date'])
        df_results.to_csv(output_csv_path, index=False)

    else:
        print("No BMP images from the list were found in the folder.")


if __name__ == "__main__":
    main()
