import pandas as pd
from tqdm import tqdm
import click 

from interface import OllamaChat
from utils import get_config, INFO_FILES

def process_file(filename, topics, output_filename, client):
    df = pd.read_csv(filename)

    results = []
    
    for index, row in tqdm(df.iterrows(), total=100):

        row_dict = {
            "id": row["id"],
        }
        
        for topic in topics:
            
            query = f"I give you an abstract of a scientific text:"
            query += f"\n{row['summary']}\n"
            query += f"Answer with one word, either YES or NO whether the abstract mentions {topic}."
            response = client.complete(query)

            row_dict[topic] = response


        results.append(row_dict)

    res_df = pd.DataFrame(results)
    res_df.to_csv(output_filename)

@click.command()
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(config_file):
    client = OllamaChat()
    
    config = get_config(config_file, section="process")
    input_dir = config.get("input_dir")
    output_dir = config.get("output_dir")
    topics = config.get("fixed_keywords")

    for file in INFO_FILES:
        print(f"Processing {input_dir}/{file}.")
        process_file(f"{input_dir}/{file}",
                     topics, 
                     f"{output_dir}/keywords_{file}",
                     client)
    print("Done.")

if __name__ == "__main__":
    main()

