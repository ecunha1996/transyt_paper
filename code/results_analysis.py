import os

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib_venn import venn2

###  show all columns of a dataframe
pd.set_option('display.max_columns', None)


def main():
    transportdb_df, transportdb_dict = load_transportdb_results(r'load_transportdb_results.csv')
    transyt = load_transyt_results([r'results/scoresMethod1.txt', r'results/scoresMethod2.txt'])
    print(transportdb_dict)
    print("#"*100)
    print(transyt)
    print('BBMN68_1022' in transyt.keys())
    diff = set(transportdb_dict.keys()) - set(transyt.keys())
    print(diff)
    df_diff = transportdb_df.loc[transportdb_df.index.isin(diff)]
    print(df_diff)
    df_diff.to_csv("diff.csv")
    print("#"*100)

    diff2 = set(set(transyt.keys() - transportdb_dict.keys()))
    print(diff2)
    df_diff2 = pd.DataFrame.from_dict({key:value for key, value in transyt.items() if key in diff2}, orient='index')
    df_diff2.to_csv("in_transyt_not_tdb.csv")
    # substrates = transportdb_df["substrate"].tolist()
    #count each substrate
    # substrates_count = {}
    # for substrate in substrates:
    #     substrates_count[substrate] = substrates.count(substrate)
    # print(substrates_count)
    # # count each family
    # families = transportdb_df["family"].tolist()
    # families_count = {}
    # for family in families:
    #     families_count[family] = families.count(family)
    # print(families_count)
    # print(transportdb_df.loc[transportdb_df["family"] == "3.A.1"])
    # transportdb_df.loc[transportdb_df["family"] == "3.A.1"].to_csv("3.A.1.csv")


def load_transyt_results(filenames):
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


def load_transportdb_results(filename):
    transportdb_results = pd.read_csv(filename, header=None, index_col=0)
    num_cols = len(transportdb_results.columns)
    transportdb_results.columns = ["substrate"] + [f"col{i}" for i in range(1, num_cols-1)] + ["family"]
    transportdb_results.index = transportdb_results.index.str.lower()
    transportdb_results.index = transportdb_results.index.str.replace("-", "_")
    transportdb_results_temp = transportdb_results.drop(columns=["substrate", "col1", "col2", "col3", "col4"], axis=1)
    ## discard rows where family starts by 9
    transportdb_results_dict = transportdb_results_temp.to_dict(orient="index")
    for key, value in transportdb_results_dict.items():
        transportdb_results_dict[key] = value["family"]
    return transportdb_results, transportdb_results_dict


def parse_results(file_path):
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
    genes = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            genes[line.split("\t")[0]] = ""
    return genes


def get_different_genes(case_study_results):
    in_tdb_not_in_transyt = set(case_study_results[1].keys()) - set(case_study_results[2].keys())
    in_transyt_not_in_tdb = set(case_study_results[2].keys()) - set(case_study_results[1].keys())
    print(f"Number of genes in transportdb but not in transyt: {len(in_tdb_not_in_transyt)}")
    print(f"Number of genes in transyt but not in transportdb: {len(in_transyt_not_in_tdb)}")
    return in_tdb_not_in_transyt, in_transyt_not_in_tdb


def get_family_distribution(gene_family_dict:dict):
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
    ax1.set_title("TransportDB")
    ax2.pie(transyt.values(), labels=transyt.keys(), autopct='%1.1f%%')
    ax2.set_title("Transyt")
    #plt.show()


def anaylise_substrates_missing(tdb_df, tdb_dict, transyt_dict):
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


def venn_diagram(case_study_results, parameter_set):
    plt.clf()
    venn2([set(case_study_results[1].keys()), set(case_study_results[2].keys())], set_labels=('TransportDB', 'Transyt'))
    plt.title(case_study, fontstyle='italic') # + " - " + parameter_set
    plt.show()


if __name__ == '__main__':
    os.chdir("../case_study")
    case_studies = ["Scerevisiae", "Paeruginosa", "Olucimarinus"]  #, "Blongum"
    parameter_sets = {"cov_80": "restricted"} #"cov_60": "relaxed",
    case_study_results_map = {}
    for case_study in case_studies:
        print(case_study)
        for parameter_set, name in parameter_sets.items():
            transportdb_df, transportdb_dict = load_transportdb_results(rf'{case_study}/transportdb.csv')
            transyt = load_transyt_results([rf'{case_study}/{parameter_set}/results/results/scoresMethod1.txt', rf'{case_study}/{parameter_set}/results/results/scoresMethod2.txt'])
            case_study_results_map[case_study] = [transportdb_df, transportdb_dict, transyt]
            case_study_analysis(case_study_results_map[case_study])
            venn_diagram(case_study_results_map[case_study], name)