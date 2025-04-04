import os
import tqdm
import pandas as pd
import click
import pyalex

from utils import read_info_files, read_id_table

pyalex.config.email = "petra@cs.cas.cz"

title = "Towards Accurate and Compact Architectures via Neural Architecture Transformer"


pyalex.config.max_retries = 2
pyalex.config.retry_backoff_factor = 0.1
pyalex.config.retry_http_codes = [429, 500, 503]



def clean_title(title):
    title = title.replace(",", "").replace(".", "").replace("\n", " ")
    title = " ".join(title.split())
    return title.lower()                 

def get_openalex_id_from_arxiv(arxiv_url):

    number = arxiv_url.split("/")[-1]
    if "v" in number:
        number = number[:number.index("v")]
    query = f"https://arxiv.org/abs/{number}"

    # works = pyalex.Works().search_filter(primary_location_source_id="https://arxiv.org",
    #                                      primary_location__landing_page_url=query).get()

    ws = pyalex.Works().filter(**{  # "primary_location.source.id": ID,
        "primary_location.landing_page_url": query
    }).get()

    if len(ws) == 0:
        return None
    
    return ws[0]['id']

def get_references(alex_id):
    work = pyalex.Works()[alex_id]

#    print(work["cited_by_api_url"])
#    exit()
    return work["referenced_works"]

def get_citations(alex_id):
    works = pyalex.Works().filter(cites=alex_id).get()
    ids = [work["id"] for work in works]
    return ids
    
def get_alex_ids():
    resulting_table = []

    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        id = row["id"]

        res = get_openalex_id_from_arxiv(id)
        #    print(i, res)

        if res is not None:
            resulting_table.append({"id": id, "alex_id": res})
        else:
            print("Not found.")

    df = pd.DataFrame(resulting_table)
    df.to_csv("id2alex.csv")

def get_ids_from_txt(filename):
    if not os.path.exists(filename):
        return []
    ret = []
    with open(filename, "r") as f:
        for line in f:
            id, _ = line.split(" : ")
            ret.append(id.strip())
    return ret

def nearest_arxiv(paperid):

    title = pyalex.Works()[paperid]["title"]
    collection = pyalex.Works().search_filter(title=clean_title(title)).get()
    
    results = []
    for paper in collection:
        if clean_title(paper["title"]) != clean_title(title):
            continue
        
        url = paper.get("primary_location")
        if url is None:
            url = ""
        else:
            url = url["landing_page_url"]
        if url.startswith("https://arxiv.org/abs/"):
            results.append(paper["id"])
                        
    return results

@click.group()
def download():
    pass 

@download.command()
def references():
    processed_ids = get_ids_from_txt("references.txt")
    
    df = pd.read_csv("data/id2alex.csv", index_col=0)
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        alex_id = row["alex_id"]
        id_ = row["id"]
        if id_ in processed_ids:
            continue
        references = get_references(alex_id)
        if references:
            with open("references.txt", "a") as f:
                print(id_, ":", references, file=f)

@download.command()
def citations(): 
    processed_ids = get_ids_from_txt("citations.txt")
    
    
    df = pd.read_csv("data/id2alex.csv", index_col=0)
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        id_ = row["id"]
        alex_id = row["alex_id"]
        if id_ in processed_ids:
            continue
        citations = get_citations(alex_id)
        arxiv_citations = []
        for citation in citations:
            arxiv_citations.extend(nearest_arxiv(citation))
        if arxiv_citations:
            with open("citations.txt", "a") as f:
                print(row["id"], ":", ",".join(arxiv_citations), file=f)


if __name__ == "__main__":
    
    download()
