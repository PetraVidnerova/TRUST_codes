import os
import time
import click
import requests

from utils import get_config, read_info_files

PREFIX = "http://arxiv.org/abs/"
ADDRESS = "http://export.arxiv.org"


@click.command()
@click.option("--pdf/--src", default=True) 
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(pdf, config_file):
    cfg = get_config(config_file, section="download")

    output_dir = cfg["output_dir"]
    pdf_dir = cfg["pdf_dir"]
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    df = read_info_files(output_dir)

    for i, row in df.iterrows():
        idx = row["id"]
        print(idx)

        assert idx.startswith(PREFIX)
        name = idx[len(PREFIX):]
        type_ = "pdf" if pdf else "src"
        address = f"{ADDRESS}/{type_}/{name}"
        print(address)

        suffix = "pdf" if pdf else "tar.gz"
        if os.path.exists(f"{pdf_dir}/{name}.{suffix}"):
            print("exists")
            continue
        
        while True:
            print("go sleep")
            time.sleep(5)
            print("wake up")
            
            print("downloading")
            response = requests.get(address)
            
            if response.status_code != 200:
                print("retry")
                continue
            print("success")
            with open(f"{pdf_dir}/{name}.{suffix}", "wb") as f:
                f.write(response.content)
            print(f"{i}: {name}.{suffix} saved")
            break
        
if __name__ == "__main__":
    main()
