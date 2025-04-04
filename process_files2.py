import pandas as pd
from tqdm import tqdm
import click

from interface import OllamaChat
from utils import get_config, info_files


def process_file(filename, topics, output_filename, client):
    df = pd.read_csv(filename)

    results = []

    for index, row in tqdm(df.iterrows(), total=len(df)):

        row_dict = {
            "id": row["id"],
        }
        
        for topic in topics:
            
            query = f"I give you an abstract of a scientific text:"
            query += f"\n{row['summary']}\n"
            query += f"Answer with one word, either YES or NO whether the abstract mentions {topic}."
            response = client.complete(query)

            row_dict[topic] = response.upper()


        results.append(row_dict)

    res_df = pd.DataFrame(results)
    res_df.to_csv(output_filename)

@click.command()
@click.option("--fixed_keywords/--target_keywords", default=True, is_flag=True)
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(fixed_keywords, config_file):
    client = OllamaChat()
    
    config = get_config(config_file, section="process")
    input_dir = config.get("input_dir")
    output_dir = config.get("output_dir")
    topics = config.get("fixed_keywords" if fixed_keywords else "target_keywords")

    config_files = get_config(config_file, section="download")
    start = config_files.get("start")
    end = config_files.get("end")
    batch = config_files.get("batch_size")
    info_file = get_config(config_file, section="files")["info_filename"]
    
    if not fixed_keywords:
        file_list = info_files(start, end, batch)
    else:
        file_list = [info_file]
    
    for file in file_list:
        print(f"Processing {input_dir}/{file}.")
        process_file(f"{input_dir}/{file}",
                     topics, 
                     f"{output_dir}/{'keywords' if fixed_keywords else 'filter'}_{file}",
                     client)
    print("Done.")

if __name__ == "__main__":
    main()

