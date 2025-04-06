import click 
from utils import read_id_table, get_config, read_refs

@click.command()
@click.argument("config_file", default="config.yaml", type=click.Path(exists=True))
def main(config_file):

    file_config = get_config(config_file, section="files")
    dir = file_config["data_dir"]

    config = get_config(config_file, section="alex")
    id_table_file = config["id_table"]
    refs_file = config["citations_file"]
    output_file = config["citation_graph_file"]

    _, alex2id = read_id_table(f'{dir}/{id_table_file}')

    refs = read_refs(f'{dir}/{refs_file}')
    edges = 0
    with open(f"{dir}/{output_file}", "w") as f:
        print("cited paper,citing paper", file=f)
        for node in refs.keys():
            for referee in set(refs[node]):
                node2 = alex2id.get(referee, None)
                if node2 is not None:
                    print(node, node2, sep=",", file=f)
                    edges += 1
    print(f"Graph saved to {output_file} with {edges} edges.")

if __name__ == "__main__":
    main()