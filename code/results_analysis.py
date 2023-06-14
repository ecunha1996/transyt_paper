import os

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib_venn import venn2

###  show all columns of a dataframe
pd.set_option('display.max_columns', None)

def load_transyt_results(filenames):
    """
    Load results from transyt.
    :param filenames: list of filenames
    :return: dictionary with results
    """
    results , method2 = {}, {}
    for filename in filenames:
        if filename.endswith('scoresMethod1.txt'):
            results = parse_results(filename)
        elif filename.endswith('scoresMethod2.txt'):
            method2 = parse_method2(filename)
        else:
            raise Exception('Invalid file name')
    results.update(method2)
    return results


def load_transaap_results(filename):
    """
    Load results from transaap.
    :param filename:
    :return:
    """
    transportdb_results = pd.read_csv(filename, header=None, index_col=0, sep="\t")
    transportdb_results.dropna(axis=1, how='all', inplace=True)
    num_cols = len(transportdb_results.columns)
    transportdb_results.columns = [f"col{i}" for i in range(1, num_cols-1)] + ["family", "last_col"]
    transportdb_results["substrate"] = transportdb_results["col6"]
    transportdb_results.index = transportdb_results.index.str.lower()
    transportdb_results.index = transportdb_results.index.str.strip()
    transportdb_results.index = transportdb_results.index.str.replace("-", "_")
    transportdb_results = transportdb_results.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    transportdb_results_temp = transportdb_results.drop(columns=["substrate", "col1", "col2", "col3", "col4", "last_col"], axis=1)
    transportdb_results_dict = transportdb_results_temp.to_dict(orient="index")
    for key, value in transportdb_results_dict.items():
        transportdb_results_dict[key] = value["family"]
    return transportdb_results, transportdb_results_dict


def parse_results(file_path):
    """
    Parse results from transyt.
    :param file_path:
    :return:
    """
    results = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        if lines[i].startswith('>'):
            key = lines[i].strip()[1:].lower()
            value = lines[i + 1].strip().split('-')[0]
            results[key] = value
            i += 2
        else:
            i += 1
    return results

def parse_method2(file_path):
    """
    Parse results from transyt with method 2.
    :param file_path:
    :return:
    """
    genes = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            genes[line.split("\t")[0]] = ""
    return genes


def get_different_genes(case_study_results):
    """
    Get genes that are in transportdb but not in transyt and vice versa.
    :param case_study_results:
    :return:
    """
    in_tdb_not_in_transyt = set(case_study_results[1].keys()) - set(case_study_results[2].keys())
    in_transyt_not_in_tdb = set(case_study_results[2].keys()) - set(case_study_results[1].keys())
    print(f"Number of genes in transportdb but not in transyt: {len(in_tdb_not_in_transyt)}")
    print(f"Number of genes in transyt but not in transportdb: {len(in_transyt_not_in_tdb)}")
    return in_tdb_not_in_transyt, in_transyt_not_in_tdb


def get_family_distribution(gene_family_dict:dict):
    """
    Get distribution of gene families.
    :param gene_family_dict:
    :return:
    """
    family_distribution = {}
    for key, value in gene_family_dict.items():
        family = '.'.join(value.split(".")[:3])
        if family in family_distribution:
            family_distribution[family] += 1
        else:
            family_distribution[family] = 1
    # sort dict
    family_distribution = {k: v for k, v in sorted(family_distribution.items(), key=lambda item: item[1], reverse=True)}
    print(family_distribution)
    return family_distribution


def create_pie_chart(tdb_results, transyt_results, title):
    """
    Create pie chart from results.
    :param tdb_results:
    :param transyt_results:
    :param title:
    :return:
    """
    # create pie char from dict
    tdb, transyt = {'other':0}, {'other':0}
    for key, value in tdb_results.items():
        if value < 10:
            tdb['other'] += value
        else:
            tdb[key] = value
    for key, value in transyt_results.items():
        if value < 10:
            transyt['other'] += value
        else:
            transyt[key] = value
    # create two pie charts
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle(title)
    ax1.pie(tdb.values(), labels=tdb.keys(), autopct='%1.1f%%')
    ax1.set_title("TransAAP")
    ax2.pie(transyt.values(), labels=transyt.keys(), autopct='%1.1f%%')
    ax2.set_title("Transyt")
    #plt.show()


def anaylise_substrates_missing(tdb_df, tdb_dict, transyt_dict):
    """
    Analyse substrates that are in transportdb but not in transyt.
    :param tdb_df:
    :param tdb_dict:
    :param transyt_dict:
    :return:
    """
    diff = set(tdb_dict.keys()) - set(transyt_dict.keys())
    print(f"Number of substrates in transportdb but not in transyt: {len(diff)}")
    families = tdb_df["family"].loc[list(diff)].tolist()
    families_count = {}
    for family in families:
        families_count[family] = families.count(family)
    families_count = {k: v for k, v in sorted(families_count.items(), key=lambda item: item[1], reverse=True)}
    print(families_count)
    substrates = tdb_df["substrate"].loc[list(diff)].tolist()
    substrates_count = {}
    for substrate in substrates:
        substrates_count[substrate] = substrates.count(substrate)
    substrates_count = {k: v for k, v in sorted(substrates_count.items(), key=lambda item: item[1], reverse=True)}
    print(substrates_count)

def case_study_analysis(case_study_results: list):
    """
    Analyse case study results.
    :param case_study_results:
    :return:
    """
    different_genes = get_different_genes(case_study_results)
    print("Genes in transyt but not in transportdb:")
    print(different_genes[1])
    print("Genes in transportdb but not in transyt:")
    print(different_genes[0])
    print('Transyt family distribution:')
    familly_distribution_transyt = get_family_distribution(case_study_results[2])
    print('Transportdb family distribution:')
    familly_distribution_transportdb = get_family_distribution(case_study_results[1])
    create_pie_chart(familly_distribution_transportdb, familly_distribution_transyt, case_study)
    anaylise_substrates_missing(case_study_results[0], case_study_results[1], case_study_results[2])


def venn_diagram(case_study_results, case_study, parameter_set):
    """
    Create venn diagram from case study results.
    :param case_study_results:
    :param case_study:
    :param parameter_set:
    :return:
    """
    plt.clf()
    plt.figure(figsize=(2.3, 2.3))
    total = len(set(case_study_results[1].keys()).union(set(case_study_results[2].keys())))
    venn2([set(case_study_results[1].keys()), set(case_study_results[2].keys())], set_labels=('TransAAP', 'TranSyT'))
          # subset_label_formatter=lambda x: str(x) + "\n(" + f"{(x/total):1.0%}" + ")")
    plt.title(case_study[0] + ". " + ''.join(case_study[1:]), fontstyle='italic', fontsize=10) # + " - " + parameter_set
    # set fontsize
    for text in plt.gca().texts:
        text.set_fontsize(8)
    # plt.show()
    plt.savefig(f"{case_study}/{parameter_set}.png", bbox_inches='tight')


if __name__ == '__main__':
    os.chdir("../case_study")
    case_studies = ["Scerevisiae", "Paeruginosa", "Olucimarinus"]  #, "Blongum"
    parameter_sets = {"default": "default", "relaxed": "relaxed"} #"cov_60": "relaxed",
    case_study_results_map = {}
    for case_study in case_studies:
        print(case_study)
        for parameter_set, name in parameter_sets.items():
            transportdb_df, transportdb_dict = load_transaap_results(rf'{case_study}/transaap.txt')
            transyt = load_transyt_results([rf'{case_study}/{parameter_set}/results/results/scoresMethod1.txt', rf'{case_study}/{parameter_set}/results/results/scoresMethod2.txt'])
            case_study_results_map[case_study] = [transportdb_df, transportdb_dict, transyt]
            case_study_analysis(case_study_results_map[case_study])
            venn_diagram(case_study_results_map[case_study], case_study, name)