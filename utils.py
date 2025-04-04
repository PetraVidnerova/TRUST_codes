import pandas as pd
import yaml

#INFO_FILES = [f"{start}_{start+batchsize}.csv" for start in range(0, 2000, 100)]
#EYWORD_FILES = [f"keywords_{start}_{start+100}.csv" for start in range(0, 2000, 100)]
#KEYWORD_FILE = "keywords.txt"

def info_files(start, end, batchsize):
    return [f"{start}_{start+batchsize}.csv" for start in range(start, end, batchsize)]

def keyword_files(start, end, batchsize):
    return [f"keywords_{start}_{start+batchsize}.csv" for start in range(start, end, batchsize)]

def get_config(filename, section=None):
    with open(filename, "r") as f:
        config = yaml.safe_load(f)
    if section is None:
        return config
    else:
        return config[section]

    
def read_files(filenames):
    dfs = []
    for file in filenames:
        df = pd.read_csv(file, index_col=0)
        dfs.append(df)

    df = pd.concat(dfs)
    return df

def read_info_files(input_dir):
    filenames = [f"{input_dir}/{filename}" for filename in INFO_FILES]
    df = read_files(filenames)
    df["published"] = pd.to_datetime(df["published"])
    df["year"] = df["published"].dt.year

    return df

def read_keyword_files(input_dir):
    # todo: check if answers are really only YES, NO
    filenames = [f"{input_dir}/{filename}" for filename in KEYWORD_FILES]
    df = read_files(filenames).set_index("id")
    return df != "NO"
    
    
def read_keyword_lists(input_dir):
    keys = {}
    filename = f"{input_dir}/{KEYWORD_FILE}"
    with open(filename, "r") as f:
        for line in f:
            fields = line.split(":")
            id_ = (fields[0] + ":" + fields[1]).strip()
            keywords = [keyword.strip().lower() for keyword in fields[2].split(",")]
            keys[id_] = set(keywords)
    return keys

def read_id_table(filename):
    df = pd.read_csv(filename, index_col=0)
    return (
        {row["id"]: row["alex_id"] for _, row in df.iterrows()},
        {row["alex_id"]: row["id"] for _, row in df.iterrows()} 
    )
    
def read_refs(filename):
    refs = {}
    with open(filename, "r") as f:
        for line in f:
            id_, fields = line.split(" : ")
            fields = [field.strip() for field in fields.split(",")]
            refs[id_] = fields
    return refs
    
def clean_id(id):
    arxiv_prefix = "http://arxiv.org/abs/"
    alex_prefix = "http://export.arxiv.org/src/"
    for prefix in arxiv_prefix, alex_prefix:
        if id.startswith(prefix):   
            return id[len(prefix):] 
    return id

