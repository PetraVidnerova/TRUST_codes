import click
import tqdm 
import pandas as pd

from interface import OllamaChat
from utils import get_config
from utils import info_files


def process_file(filename, forbidden_keyword, output_filename, client, verbose=False):
    df = pd.read_csv(filename)
    
    for index, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        
        query = f"List  5 keywords from the following text:"
        query += f"\n{row['summary']}\n"
        query += f"Do not include the keyword '{forbidden_keyword}' in the list."
        query += f"Return only the keywords, comma separated, no other text."
        response = client.complete(query)

        if verbose:
            print(index,":", response)
            print()

        keywords = response.split(',')
        keywords = [keyword.strip().lower() for keyword in keywords]
        
        with open(output_filename, 'a') as f:
            print(f"{row['id']}: {', '.join(keywords)}", file=f)
    
        
@click.command()
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
@click.option("-v", "--verbose", default=False, is_flag=True)
def main(config_file, verbose):
    
    config = get_config(config_file, section="process")
    
    forbidden_keyword = config.get("forbidden_keyword")
    output_file = config.get("output_file")
    input_dir = config.get("input_dir")
    output_dir = config.get("output_dir")

    config_files = get_config(config_file, section="download")
    start = config_files["start"]
    end = config_files["end"]
    batch = config_files["batch_size"]

    filename = get_config(config_file, section="files")["info_filename"]

    client = OllamaChat()
    print(f"Processing {input_dir}/{filename}.")
    process_file(f"{input_dir}/{filename}",
                 forbidden_keyword=forbidden_keyword,
                 output_filename=f"{output_dir}/{output_file}",
                 client=client
            )
    

if __name__ == "__main__":
    main()

