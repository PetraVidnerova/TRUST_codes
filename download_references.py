import os

import tqdm
import pandas as pd
import click
import pyalex

from utils import read_id_table, get_config

pyalex.config.email = "petra@cs.cas.cz"

pyalex.config.max_retries = 2
pyalex.config.retry_backoff_factor = 0.1
pyalex.config.retry_http_codes = [429, 500, 503]



def clean_title(title):
    title = title.replace(",", "").replace(".", "").replace("\n", " ")
    title = title.replace("&amp;", "").replace("&", "")
    title = " ".join(title.split())
    return title.lower()                 

def get_openalex_id_from_arxiv(arxiv_url):

    number = arxiv_url[len("http://arxiv.org/abs/"):]
    if "v" in number:
        number = number[:number.index("v")]
    for query in f"http://arxiv.org/abs/{number}", f"https://arxiv.org/abs/{number}":

        ws = pyalex.Works().filter(**{  # "primary_location.source.id": ID,
            "primary_location.landing_page_url": query
        }).get()

        if len(ws) > 0:
            return ws[0]['id']  
    return None

def get_references(alex_id):
    work = pyalex.Works()[alex_id]

#    print(work["cited_by_api_url"])
#    exit()
    return work["referenced_works"]

def get_citations(alex_id, title):
    papers = get_papers_with_title(title)
    if alex_id not in papers:
        print(f"Warning: Paper {alex_id}({title}) not found in fetched papers. This is weird, look for a bug.")
        papers.append(alex_id)

    all_works = set()
    for paper in papers:
        works = pyalex.Works().filter(cites=paper).get()
        ids = [work["id"] for work in works]
        all_works.update(ids)
    
    return ids
    

def get_ids_from_txt(filename):
    if not os.path.exists(filename):
        return []
    ret = []
    with open(filename, "r") as f:
        for line in f:
            id, _ = line.split(" : ")
            ret.append(id.strip())
    return ret

def get_papers_with_title(title):
    collection = pyalex.Works().search_filter(title=clean_title(title)).get()
    results = []
    for paper in collection:
        if clean_title(paper["title"]) != clean_title(title):
            continue
        
        results.append(paper["id"])
    return results

def nearest_arxiv(paperid):

    title = pyalex.Works()[paperid]["title"]
    # there is at least one paper untitled in openalex
    if title is None:
        print(f"Warning: Title is None for {paperid}.")
        return []
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
@click.argument("configfile", default="config.yaml", type=click.Path(exists=True))
def init(configfile):
    
    config = get_config(configfile, section="files")
    df = pd.read_csv(f"{config['data_dir']}/{config['info_filename']}", index_col=0)
    
    resulting_table = []

    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        id = row["id"]

        res = get_openalex_id_from_arxiv(id)
        #    print(i, res)

        if res is not None:
            resulting_table.append({"id": id, "alex_id": res})
        else:
            print(f"{id} not found.")

    df = pd.DataFrame(resulting_table)
    df.to_csv(f"{config['data_dir']}/id2alex.csv")
    print("Table saved to id2alex.csv")

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
@click.argument("configfile", default="config.yaml", type=click.Path(exists=True))
def citations(configfile):
    config = get_config(configfile, section="alex")
    files_config = get_config(configfile, section="files")
    dir = files_config["data_dir"]
    info_file = files_config["info_filename"]
    id_table_file = config["id_table"]
    citations_file = config["citations_file"] 
    processed_ids = get_ids_from_txt(f"{dir}/{citations_file}")
    
    df_info = pd.read_csv(f"{dir}/{info_file}", index_col=0)

    df = pd.read_csv(f"{dir}/{id_table_file}", index_col=0)
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        id_ = row["id"]
        alex_id = row["alex_id"]
        title = df_info.loc[df_info["id"] == id_]["title"].values[0]
        if id_ in processed_ids:
            continue
        citations = get_citations(alex_id, title)
        arxiv_citations = []
        for citation in citations:
            arxiv_citations.extend(nearest_arxiv(citation))
        #if arxiv_citations:
        with open(f"{dir}/{citations_file}", "a") as f:
            print(row["id"], ":", ",".join(arxiv_citations), file=f)

if __name__ == "__main__":
    
    download()
    #cit = get_citations("https://openalex.org/W4307933250",
    #        "Automated Dominative Subspace Mining for Efficient Neural Architecture Search")              
    
    # check titles 
    
    #df = pd.read_csv("data/id2alex.csv", index_col=0)
    #df_info = pd.read_csv("data/info.csv", index_col=0)
#
    #count = 0
  #  for i, row in tqdm.tqdm(df.iterrows(), total=len(df)):
 #       id = row["id"]
   #     alex_id = row["alex_id"]
    #    title_alex = pyalex.Works()[alex_id]["title"]
     #   title_arxiv = df_info.loc[df_info["id"] == id]["title"].values[0]
#
 #       if clean_title(title_alex) != clean_title(title_arxiv):
  #          print(f"Title mismatch for {id}:")
   #         print(f"OpenAlex: {title_alex}")
    #        print(f"Arxiv: {title_arxiv}")
     #       print()
      #      count += 1
    #print(f"Total mismatches: {count}")