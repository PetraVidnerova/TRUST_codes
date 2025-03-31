import time 
import os
import requests
import feedparser
import yaml

import pandas as pd
import click 

def search_arxiv(query="all:'neural architecture search'", max_results=2, start=0):
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        print("Failed to retrieve data from arXiv")
        return []

    feed = feedparser.parse(response.text)
    
    num_papers = len(feed.entries)
    if num_papers == 0:
        raise ValueError("Empty feed.")
    
    return [ 
            {
            "title": entry.title,
            "authors":  ";".join([author["name"] for author in entry.authors]),
            "id": entry.id,
             "published": entry.published,
             "summary": entry.summary
             }
            for entry in feed.entries
    ]

@click.command()
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(config_file):

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        config = config["download"] 
    
    query = config.get("query", "all: 'neural architecture search'")
    batch_size = config.get("batch_size", 100)
    sleep = config.get("sleep", 120)
    output_dir = config.get("output_dir", "./data/")
    start = config.get("start", 0)
    end = config.get("end", 2000)
    trials = config.get("trials", 5)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    start = 0
    while start < end:
        for _ in range(trials):
            try:    
                papers = search_arxiv(
                    query=query,
                    max_results=batch_size,
                    start=start
                )
            except ValueError:
                print("Empty feed. Retrying...")
                time.sleep(300)
                continue
            break        
        else:
            print(f"Failed to retrieve data from arXiv. Skipping batch {start} - {start+batch_size}.")
            continue
        
        df = pd.DataFrame(papers)
        df.to_csv(f"{output_dir}/{start}_{start + batch_size}.csv")
        print(f"{start}  - {start + batch_size} results saved")

        start += batch_size
        time.sleep(sleep)

        

if __name__ == "__main__":
    main()
