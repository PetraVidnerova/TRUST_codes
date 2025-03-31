import pandas as pd

INFO_FILES = [f"{start}_{start+100}.csv" for start in range(0, 2000, 100)]
KEYWORD_FILES = [f"keywords_{start}_{start+100}.csv" for start in range(0, 2000, 100)]
KEYWORD_FILE = "keywords.txt"

def read_files(filenames):
    dfs = []
    for file in filenames:
        df = pd.read_csv(file, index_col=0)
        dfs.append(df)

    df = pd.concat(dfs)
    return df

def read_info_files():
    df = read_files(INFO_FILES)
    
    df["published"] = pd.to_datetime(df["published"])
    df["year"] = df["published"].dt.year

    return df

def read_keyword_files():
    df = read_files(KEYWORD_FILES).set_index("id")
    return df != "NO"
    
    
def read_keyword_lists():
    keys = {}
    with open(KEYWORD_FILE, "r") as f:
        for line in f:
            fields = line.split(":")
            id_ = (fields[0] + ":" + fields[1]).strip()
            keywords = [keyword.strip().lower() for keyword in fields[2].split(",")]
            keys[id_] = set(keywords)
    return keys
