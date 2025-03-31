import matplotlib.pyplot as plt
import seaborn as sns

def pie_plot(df_keys, key_names, title, filename):
    
    parts = [df_keys[part].sum() for part in key_names]

    paches, texts = plt.pie(parts, explode=[0.01]*len(key_names));
    plt.legend(paches, key_names, loc="upper right", bbox_to_anchor=[1.5, 1.0])
    plt.title(title)
    plt.savefig(filename, bbox_inches="tight")

def pie_timeline(timeline, key_names, title, filename):
    fig, axs = plt.subplots(nrows=1, ncols=8, figsize=(12, 2))
    for year in range(2017, 2025):
        i = year - 2017
        patches, texts = axs[i].pie(timeline.loc[year], explode=[0.01]*len(key_names))
        axs[i].set_title(year)

    plt.legend(patches, key_names, loc="upper right", bbox_to_anchor=(3.5, 1.05))
    plt.suptitle(title)
    plt.savefig(filename, bbox_inches="tight")
