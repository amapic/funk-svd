import pandas as pd
import numpy as np
import datetime
import zipfile
import shutil
import urllib
import os


__all__ = [
    "fetch_ml20m_ratings",
]


def get_data_dir_path(data_dir_path=None):
    """Returns the path of the funk-svd data directory.
    
    This folder is used to store large datasets to avoid downloading them
    several times.
    By default the data dir is set to a folder named 'funk_svd_data' in the
    user home folder. Alternatively, it can be set by the 'FUNK_SVD_DATA'
    environment variable or programmatically by giving an explicit
    `data_dir_path`.
    If the folder does not already exist, it is automatically created.
    
    Args:
        data_dir_path (string, default to `None`): explicit data directory path
            for large datasets.
        
    Returns:
        data_dir_path (string): explicit data directory path for large
            datasets.
    """
    if data_dir_path is None:
        default = os.path.join("~", "funk_svd_data")
        data_dir_path = os.environ.get("FUNK_SVD_DATA", default=default)
        data_dir_path = os.path.expanduser(data_dir_path)
        
    if not os.path.exists(data_dir_path):
        os.makedirs(data_dir_path)
            
    return data_dir_path


def ml20m_ratings_csv_to_df(csv_path):
    names = ["u_id", "i_id", "rating", "timestamp"]
    dtype = {"u_id": np.uint32, "i_id": np.uint32, "rating": np.float64}
    
    def date_parser(time):    
        return datetime.datetime.fromtimestamp(float(time))
    
    df = pd.read_csv(csv_path, names=names, dtype=dtype, header=0,
                     parse_dates=["timestamp"], date_parser=date_parser)
    
    df.sort_values(by="timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    return df


def fetch_ml20m_ratings(data_dir_path=None):
    """Fetches MovieLens 20M ratings dataset.
    
    Args:
        data_dir_path (string, default to `None`): explicit data directory path
            to MovieLens 20M ratings csv.
    
    Returns:
        df (pandas DataFrame): containing the dataset.
    """
    if data_dir_path is None:
        data_dir_path = get_data_dir_path(data_dir_path)
        dirname = "ml-20m"
        filename = "ratings.csv"
        csv_path = os.path.join(data_dir_path, dirname, filename)
        zip_path = os.path.join(data_dir_path, dirname) + ".zip"
        url = "http://files.grouplens.org/datasets/movielens/ml-20m.zip"
    else:
        csv_path = data_dir_path

    if os.path.exists(csv_path): # Return data loaded into a DataFrame
        df = ml20m_ratings_csv_to_df(csv_path)
        return df
    
    elif os.path.exists(zip_path): # Unzip file before calling back itself
        print("Unzipping data...")

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(data_dir_path)

        os.remove(zip_path)

        return fetch_ml20m_ratings()
    
    else: # Download the ZIP file before calling back itself
        print("Downloading data...")
        with urllib.request.urlopen(url) as r, open(zip_path, "wb") as f:
            shutil.copyfileobj(r, f)
    
        return fetch_ml20m_ratings()
