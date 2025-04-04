import click
import pandas as pd

from interface import OllamaChat
from utils import get_config
from utils import INFO_FILES


def process_file(filename, forbidden_keyword, output_filename, client):
    df = pd.read_csv(filename)
    
    for index, row in df.iterrows():
        
        query = f"List  5 keywords from the following text:"
        query += f"\n{row['summary']}\n"
        query += f"Do not include the keyword '{forbidden_keyword}' in the list."
        query += f"Return only the keywords, comma separated, no other text."
        response = client.complete(query)
       
        print(index,":", response)
        print()

        keywords = response.split(',')
        keywords = [keyword.strip().lower() for keyword in keywords]
        
        with open(output_filename, 'a') as f:
            print(f"{row['id']}: {', '.join(keywords)}", file=f)
    
        
@click.command()
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(config_file):
    
    config = get_config(config_file, section="process")
    
    forbidden_keyword = config.get("forbidden_keyword")
    output_file = config.get("output_file")
    input_dir = config.get("input_dir")
    output_dir = config.get("output_dir")

    filenames = [f"{input_dir}/{filename}" for filename in INFO_FILES]

    client = OllamaChat()

    for file in filenames:
        print(f"Processing {file}.")
        process_file(file,
                     forbidden_keyword=forbidden_keyword,
                     output_filename=f"{output_dir}/{output_file}",
                     client=client
                     )

    print(f"Results saved to {output_dir}/{output_file}.")
    

if __name__ == "__main__":
    main()

