import os

def get_all_directories_paths(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in directories:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths
    return file_paths

def get_all_files_in_path(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths
    return file_paths

def fix_model_to_cobra_format(out_sbml_path, model_fix_path):
    if os.path.exists(out_sbml_path):
        # fix sbml header for cobra

        sbml_tag = '<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" fbc:required="false" groups:required="false" level="3" sboTerm="SBO:0000624" version="1" xmlns:fbc="http://www.sbml.org/sbml/level3/version1/fbc/version2" xmlns:groups="http://www.sbml.org/sbml/level3/version1/groups/version1">'
        model_tag = '<model extentUnits="substance" fbc:strict="true" id="transyt" metaid="transyt" name="transyt" substanceUnits="substance" timeUnits="time">'
        xml_data = None
        xml_fix = ""
        with open(out_sbml_path, 'r') as f:
            xml_data = f.readlines()
        for l in xml_data:
            if l.strip().startswith('<sbml'):
                xml_fix += sbml_tag
            elif l.strip().startswith('<model'):
                xml_fix += model_tag
            else:
                xml_fix += l

        if xml_data is not None:
            with open(model_fix_path, 'w') as f:
                f.writelines(xml_fix)

    print("model fixed")

def strip_gene_rule(rule):

    genes = []

    aux_split = rule.replace(" and ", " or ").replace(" )", "").replace("( ", "").split(" or ")

    for gene in aux_split:
        if gene not in genes:
            genes.append(gene)

    return genes

def read_model_seed_compounds_names():

    path = None #modelSEED compounds.tsv file (available in modelSEED repository)

    dic = {}

    header = True

    for line in open(path, "r"):

        if header:
            header = False
        else:
            line_split = line.split("\t")

            cpd_id = line_split[0].strip()
            cpd_name = line_split[2].strip()

            dic[cpd_id] = cpd_name

    return dic

def read_dic(path):

    dic = {}

    for line in open(path, "r"):

        line_split = line.split("\t")

        dic[line_split[0].strip()] = line_split[1].strip()

    return dic