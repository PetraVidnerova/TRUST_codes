import click

from utils import read_info_files, read_filter_files, get_config

@click.command()
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(config_file):
    config = get_config(config_file, section="download")

    directory = config["output_dir"]
    start = config["start"]
    end = config["end"]
    batch_size = config["batch_size"]

    config = get_config(config_file, section="files")
    output_file = config["info_filename"]
    
    df_info = read_info_files(directory, start, end, batch_size)
    df_filter = read_filter_files(directory, start, end, batch_size)

    df_filter["wanted"] = df_filter.sum(axis="columns") > 0 # logical_or per row
    
    df_info = df_info.merge(df_filter, on="id")
    df = df_info[df_info["wanted"] == True]
    df = df.drop(columns=df_filter.columns)

    print(f"{len(df)} files selected. Saving to {directory}/{output_file}.")
    df.to_csv(f"{directory}/{output_file}")
    print("Done.")
    
if __name__ == "__main__":
    main()
