import Utilities
import cobra
import re
import copy
import os
import xlwt

def read_rast_functions(path):

    dic = {}

    for line in open(path, "r"):

        line_split = line.split("\t")

        reference = line_split[1].strip()
        gene = line_split[2].strip()

        if reference not in dic:
            dic[reference] = []

        if gene not in dic[reference]:
            dic[reference].append(gene)

    return dic

def read_generic_transyt_map_string_list(path):

    dic = {}

    for line in open(path, "r"):

        line_split = line.split("\t")

        reference = line_split[0].strip()

        if reference != "GCF_000145035.1" and reference != "GCF_001742225.1":

            text = None

            if line_split[1].strip() != "":
                text = line_split[1].strip().split(";")

            dic[reference] = text

    return dic

def validate_transyt_results(path, results_path):
    directories = [f.path for f in os.scandir(path) if f.is_dir()]

    not_found = open(results_path + "/notFound.txt", "a")

    for directory in directories:

        path_split = directory.split("/")
        identifier = path_split[len(path_split) - 1]

        if 'GCF' in identifier and "GCF_000145035.1" not in identifier and "GCF_001742225.1" not in identifier:
            transyt_model = directory + "/results/transyt.xml"
            model_fix_path = path + '/temp_cobra_model.xml'

            if os.path.exists(transyt_model):

                Utilities.fix_model_to_cobra_format(transyt_model, model_fix_path)

                model = cobra.io.read_sbml_model(model_fix_path)

                create_active_genes_report(results_path, identifier, model)

                create_compounds_by_gene_report(results_path + "/refG_compounds_by_gene", identifier, model)

                create_reactions_by_gene_report(results_path + "/refG_reactions_by_gene", identifier, model)

                os.remove(model_fix_path)

            else:
                not_found.write(identifier + "\n")
                create_active_genes_report(path, identifier, None)

    not_found.close()


def compounds_by_gene_2(model):

    genes = {}

    for reaction in model.reactions:

        reactionId = reaction.id

        l = []

        for metabolite in reaction.metabolites:
            suffix = "_" + metabolite.compartment + str(metabolite.charge)
            id = metabolite.id.replace(suffix, "")

            if id not in l:
                l.append(id.strip())

        rule = Utilities.strip_gene_rule(reaction.gene_reaction_rule)

        filter_reaction_compounds(reactionId, l)

        for gene in rule:

            if gene not in genes:
                genes[gene] = []

            compounds = genes[gene]

            for id in l:
                if id not in compounds:
                    compounds.append(id.strip())

        genes[gene] = compounds

    return genes

def filter_reaction_compounds(reactionId, compounds):

    if re.search("T.1.*", reactionId) or re.search("T.2.*", reactionId):
        strip_symport_antiport_reactions(compounds)

    elif re.search("T.3.*", reactionId):
        strip_abc_reactions(compounds)

    elif re.search("T.4.*", reactionId):
        strip_pts_reactions(compounds)

    elif re.search("T.5.*", reactionId):
        strip_coa_reactions(compounds)

    elif re.search("T.6.*", reactionId):
        strip_nad_reactions(compounds)

def strip_gene_rule(rule):

    genes = []

    aux_split = rule.replace(" and ", " or ").replace(" )", "").replace("( ", "").split(" or ")

    for gene in aux_split:
        if gene not in genes:
            genes.append(gene)

    return genes

def strip_symport_antiport_reactions(compounds):

    compounds_copy = copy.deepcopy(compounds)

    for compound in compounds_copy:
        if compound == 'cpd00067' or compound == 'cpd00971':
            compounds.remove(compound)

def strip_abc_reactions(compounds):

    compounds_copy = copy.deepcopy(compounds)

    for compound in compounds_copy:
        if compound == 'cpd00001' or compound == 'cpd00002' or compound == 'cpd00008' or compound == 'cpd00009' or compound == 'cpd00012' or compound == 'cpd00067':
            compounds.remove(compound)

def strip_pts_reactions(compounds):

    compounds_copy = copy.deepcopy(compounds)

    for compound in compounds_copy:
        if compound == 'cpd00061' or compound == 'cpd000020':
            compounds.remove(compound)

def strip_coa_reactions(compounds):

    compounds_copy = copy.deepcopy(compounds)

    for compound in compounds_copy:
        if compound == 'cpd00001' or compound == 'cpd00002' or compound == 'cpd00007' or compound == 'cpd000010' or compound == 'cpd00012' or compound == 'cpd00018':
            compounds.remove(compound)

def strip_nad_reactions(compounds):

    compounds_copy = copy.deepcopy(compounds)

    for compound in compounds_copy:
        if compound == 'cpd00003' or compound == 'cpd000004' or compound == 'cpd00067':
            compounds.remove(compound)

def  create_compounds_by_gene_report(path, identifier, model):

    genes = compounds_by_gene_2(model)

    '''
    count = {}

    for gene in genes.keys():
        for compound in genes[gene]:

            if compound in count:
                count[compound] = count[compound] + 1
            else:
                count[compound] = 1
    '''

    f = open(path + "/" + identifier + ".txt", "a+")

    for gene in genes.keys():
        text = None
        for compound in genes[gene]:
            if text is None:
                text = compound
            else:
                text = text + ";" + compound

        if "__" in gene:
            gene = gene.replace("__", ".")

        message = str(gene) + "\t" + str(text) + "\n"
        f.write(message)

    f.close()


def create_reactions_by_gene_report(path, identifier, model):

    genes = {}

    for reaction in model.reactions:

        reactionId = reaction.id

        rule = Utilities.strip_gene_rule(reaction.gene_reaction_rule)

        for gene in rule:

            if gene not in genes:
                genes[gene] = []

            if reactionId not in genes[gene]:
                genes[gene].append(reactionId)

    f = open(path + "/" + identifier + ".txt", "a+")

    for gene in genes.keys():
        text = None
        for reaction in genes[gene]:
            if text is None:
                text = reaction
            else:
                text = text + ";" + reaction

        if "__" in gene:
            gene = gene.replace("__", ".")

        message = str(gene) + "\t" + str(text) + "\n"
        f.write(message)

    f.close()

def create_active_genes_report(results_path, identifier, model_path):

    text = ""

    if model_path is not None:

        genes = get_active_genes(model_path)
        print(identifier + "\t" + str(len(genes)))

        for gene in genes:

            if "__" in gene:
                gene = gene.replace("__", ".")

            if text == "":
                text = gene
            else:
                text = text + ";" + gene

    f = open(results_path + "/refG_data_genes_list.txt", "a+")
    message = identifier + "\t" + text + "\n"
    f.write(message)
    f.close()

def get_active_genes(model):

    genes = []

    for reaction in model.reactions:

        rule = reaction.gene_reaction_rule.replace(" and ", " or ").replace(" )", "").replace("( ", "").split(
            " or ")

        for gene in rule:

            if "__" in gene:
                gene = gene.replace("__", ".")

            if gene not in genes:
                genes.append(gene)

    return genes

def read_rast_refseq_file(rast_refseq_path):

    dic_rast = {}
    dic_refseq = {}

    for line in open(rast_refseq_path, "r"):

        text = line.strip()

        if "GCF_000145035.1" not in line and "GCF_001742225.1" not in line:

            if "rast_isTrans" not in line:

                line_split = line.split("\t")

                reference = line_split[1].strip()
                gene = line_split[2].strip()

                rast_ann = line_split[3].strip()
                rast_is_trans = eval(line_split[4].strip())

                refseq_ann = line_split[5].strip()
                refseq_is_trans = eval(line_split[6].strip())

                if reference not in dic_rast:
                    dic_rast[reference] = {}
                    dic_refseq[reference] = {}

                dic_rast[reference][gene] = rast_ann, rast_is_trans
                dic_refseq[reference][gene] = refseq_ann, refseq_is_trans

    return dic_rast, dic_refseq


def read_rast_or_refseq_annotations_file(rast_refseq_path):

    dic = {}

    for line in open(rast_refseq_path, "r"):

        if "GCF_000145035.1" not in line and "GCF_001742225.1" not in line:

            line_split = line.split("\t")

            reference = line_split[1].replace(".RAST2", "").strip()
            gene = line_split[2].strip()
            annotation = line_split[3].strip()

            if reference not in dic:
                dic[reference] = {}

            dic[reference][gene] = annotation

    return dic


def combine_rast_refseq_transyt_annotations(rast_refseq_path, transyt_workdir):

    new_file = open(transyt_workdir + "/reactions_combinations.tsv", "w")
    new_file.write("reference" + "\t" + "rast_only" + "\t" + "refseq_only" + "\t" + "transyt_only" + "\t" + "rast_and_refseq"
                   + "\t" + "rast_and_transyt" + "\t" + "refseq_and_transyt" + "\t" + "all_combined" + "\t" + "lineage" + "\n")

    dic_rast, dic_refseq = read_rast_refseq_file(rast_refseq_path)

    transyt_data = read_generic_transyt_map_string_list(transyt_workdir + "/refG_data_genes_list.txt")

    dic_uncharacterized = {}
    dic_uncharacterized_not_trans = {}

    taxonomies = {}

    for line in open(workdir + "/taxonomies.tsv", "r"):
        line_split = line.strip().split("\t")
        taxonomies[line_split[0]] = {"tax_id": line_split[1], "lineage":line_split[2]}

    #references = ["GCF_000005845.2"]
    #for reference in references:
    for reference in transyt_data.keys():   #only for genomes used in transyt

        if transyt_data[reference] is not None:

            rast_only_trans = 0
            refseq_only_trans = 0
            transyt_only = 0
            rast_and_refseq_trans = 0
            rast_and_transyt_trans = 0
            refseq_and_transyt_trans = 0
            all_trans = 0

            for gene in dic_rast[reference].keys():

                rast_ann = dic_rast[reference][gene][0]
                refseq_ann = dic_refseq[reference][gene][0]
                rast_bool = dic_rast[reference][gene][1]
                refseq_bool = dic_refseq[reference][gene][1]
                transyt_bool = False

                if reference in transyt_data:
                    if gene in transyt_data[reference]:
                        transyt_bool = True

                if rast_bool and refseq_bool and transyt_bool:
                    all_trans += 1
                elif rast_bool and transyt_bool:
                    rast_and_transyt_trans += 1
                elif refseq_bool and transyt_bool:
                    refseq_and_transyt_trans += 1
                elif rast_bool and refseq_bool:
                    rast_and_refseq_trans += 1
                elif rast_only_trans:
                    rast_only_trans += 1
                elif refseq_bool:
                    refseq_only_trans += 1
                elif transyt_bool:
                    transyt_only += 1

                '''
                if transyt_bool:
                    if (re.search("hypothetical", rast_ann, re.IGNORECASE) or \
                     re.search("unknown", rast_ann, re.IGNORECASE) or \
                     re.search("Uncharacterized", rast_ann, re.IGNORECASE) or \
                     re.search("putative", rast_ann, re.IGNORECASE) or re.search("probable", rast_ann, re.IGNORECASE)) and rast_bool:
                        if rast_ann not in dic_uncharacterized:
                            dic_uncharacterized[rast_ann] = 0
                        dic_uncharacterized[rast_ann] = dic_uncharacterized[rast_ann] + 1

                    elif re.search("hypothetical", rast_ann, re.IGNORECASE) or \
                     re.search("unknown", rast_ann, re.IGNORECASE) or \
                     re.search("Uncharacterized", rast_ann, re.IGNORECASE) or \
                     re.search("putative", rast_ann, re.IGNORECASE) or re.search("probable", rast_ann, re.IGNORECASE):
                        if rast_ann not in dic_uncharacterized_not_trans:
                            dic_uncharacterized_not_trans[rast_ann] = 0
                        dic_uncharacterized_not_trans[rast_ann] = dic_uncharacterized_not_trans[rast_ann] + 1
                '''
                '''
                if transyt_bool:
                    if (re.search("hypothetical", refseq_ann, re.IGNORECASE) or \
                     re.search("unknown", refseq_ann, re.IGNORECASE) or \
                     re.search("Uncharacterized", refseq_ann, re.IGNORECASE) or \
                     re.search("putative", refseq_ann, re.IGNORECASE) or re.search("probable", refseq_ann, re.IGNORECASE)) and refseq_bool:
                        if refseq_ann not in dic_uncharacterized:
                            dic_uncharacterized[refseq_ann] = 0
                        dic_uncharacterized[refseq_ann] = dic_uncharacterized[refseq_ann] + 1

                    elif re.search("hypothetical", refseq_ann, re.IGNORECASE) or \
                     re.search("unknown", refseq_ann, re.IGNORECASE) or \
                     re.search("Uncharacterized", refseq_ann, re.IGNORECASE) or \
                     re.search("putative", refseq_ann, re.IGNORECASE) or re.search("probable", refseq_ann, re.IGNORECASE):
                        if refseq_ann not in dic_uncharacterized_not_trans:
                            dic_uncharacterized_not_trans[refseq_ann] = 0
                        dic_uncharacterized_not_trans[refseq_ann] = dic_uncharacterized_not_trans[refseq_ann] + 1
                '''

            new_file.write(
                reference + "\t" + str(rast_only_trans) + "\t" + str(refseq_only_trans) + "\t" + str(transyt_only) + "\t"
                + str(rast_and_refseq_trans) + "\t" + str(rast_and_transyt_trans) + "\t" + str(refseq_and_transyt_trans)
                + "\t" + str(all_trans) + "\t" + taxonomies[reference]["lineage"] + "\n")

    new_file.close()

    print("#####################")

    for key in dic_uncharacterized.keys():
        print(key + "\t" + str(dic_uncharacterized[key]))

    print("#####################")
    print("#####################")
    print("#####################")

    for key in dic_uncharacterized_not_trans.keys():
        print(key + "\t" + str(dic_uncharacterized_not_trans[key]))

    print("#####################")

    #print("all_trans = " + str(all_trans))
    #print("rast_and_refseq = " + str(rast_and_refseq_trans))
    #print("rast_and_transyt = " + str(rast_and_transyt_trans))
    #print("refseq_and_transyt = " + str(refseq_and_transyt_trans))
    #print("rast_only = " + str(rast_only_trans))
    #print("refseq_only = " + str(refseq_only_trans))
    #print("transyt_only = " + str(transyt_only))
    #print("total = " + str(total))


def add_transport_type_and_compounds_to_rast_or_refseq(external_annotations_path, path, workidr, modelseed_compounds_mapping):
    dic = {}

    new_file = open(path, "w")
    #new_file.write("n" + "\t" + text + "\t" + "transport_type" + "\t" + "compounds")

    genes_data = read_generic_transyt_map_string_list(workidr + "/refG_data_genes_list.txt")
    #dic_rast, dic_refseq = read_rast_refseq_file(path + "/reactions_combinations.tsv")

    external_annotation = read_rast_or_refseq_annotations_file(external_annotations_path)

    reactions_mapping = None
    compounds_mapping = None

    current_mapping = ""

    new_file.write("n\tgenome_id\tgene_id\tfunction\ttransport_type\tcompounds\n")
    i = 0

    for reference in genes_data:
        if genes_data[reference] is not None:
            for gene in genes_data[reference]:
                i += 1

                if "GCF_000145035.1" != reference and "GCF_001742225.1" != reference:

                    function = "?"

                    if gene in external_annotation[reference]:
                        function = external_annotation[reference][gene]

                    text = str(i) + "\t" + reference + "\t" + gene + "\t" + function

                    if genes_data.get(reference) is not None:
                        if current_mapping != reference:
                            reactions_mapping = read_generic_transyt_map_string_list(workdir + "/refG_reactions_by_gene/" + reference + ".txt")
                            compounds_mapping = read_generic_transyt_map_string_list(workdir + "/refG_compounds_by_gene/" + reference + ".txt")
                            current_mapping = reference

                        if gene in reactions_mapping:
                            transport_types = get_gene_transport_types(reactions_mapping.get(gene))
                            compounds_names = get_compounds_names(compounds_mapping.get(gene), modelseed_compounds_mapping)

                            text = text + "\t" + str('; '.join(transport_types)) + "\t" + str('; '.join(compounds_names))
                        else:
                            print(reference + "\t" + gene)
                            text = None

                    else:
                        text = None

                    if text is not None:
                        new_file.write(text + "\n")

    new_file.close()

    return dic

def get_gene_transport_types(reactions):

    types = []

    for reactionId in reactions:

        type = get_transport_type_by_id(reactionId)

        if type not in types:
            types.append(type)

    return types

def get_transport_type_by_id(reactionId):
    type = None

    if re.search("T.0.*", reactionId):
        type = "uniport"

    elif re.search("T.1.*", reactionId):
        type = "symport"

    elif re.search("T.2.*", reactionId):
        type = "antiport"

    elif re.search("T.3.*", reactionId):
        type = "abc"

    elif re.search("T.4.*", reactionId):
        type = "pts"

    elif re.search("T.5.*", reactionId):
        type = "coa"

    elif re.search("T.6.*", reactionId):
        type = "redox"

    elif re.search("T.7.*", reactionId):
        type = "light"

    else:
        type = "other"

    return type


def get_compounds_names(compounds_ids, modelseed_data):

    names = []

    for compound_id in compounds_ids:
        compound_id = compound_id.strip()
        name = compound_id

        if compound_id in modelseed_data:
            name = modelseed_data.get(compound_id)

        if name not in names:
            names.append(name)

    return names

def check_results(path):

    both = 0
    rast = 0
    transyt = 0

    for line in open(path, "r"):

        line_split = line.split("\t")

        reference = line_split[1].strip()
        gene = line_split[2].strip()
        function = line_split[3].strip()
        transport_types = line_split[4].strip().replace("\"", "").split("; ")

        if re.search("abc", function, re.IGNORECASE) or re.search("atpase", function, re.IGNORECASE):
            if "abc" in transport_types:
                both += 1
            else:
                #print(reference + "\t" + gene + "\t" + function + "\t" + str(transport_types))
                rast += 1

        elif "abc" in transport_types:
            print(reference + "\t" + gene + "\t" + function)
            transyt += 1

    print(both)
    print(rast)
    print(transyt)

def check_results_2(path):

    abc, simple, pts, unkn, coa, redox, none = group_rast_functions(path)

    transport_types = {}

    total = 0

    for line in open(path, "r"):

        line_split = line.split("\t")

        n = line_split[0].strip()
        reference = line_split[1].strip()
        gene = line_split[2].strip()
        function = line_split[3].strip()
        transport = line_split[4].strip().replace("\"", "").split("; ")

        transport_types[n] = transport

        #if n in none:
        #    print(str(n) + "\t" + reference + "\t" + gene + "\t" + str(transport))

        if n != "":
            total += 1

    matches = {"abc":0, "coa":0, "simple":0, "pts":0, "redox":0}

    for n in abc:
        if n in transport_types:
            if "abc" in transport_types[n]:
                matches["abc"] += 1
            #else:
                #print(n)
    for n in coa:
        if n in transport_types:
            if "coa" in transport_types[n]:
                matches["coa"] += 1
    for n in simple:
        if n in transport_types:
            if "uniport" in transport_types[n] or "symport" in transport_types[n] or "antiport" in transport_types[n]:
                matches["simple"] += 1

    for n in pts:
        if n in transport_types:
            if "pts" in transport_types[n]:
                matches["pts"] += 1
    for n in redox:
        if n in transport_types:
            if "redox" in transport_types[n]:
                matches["redox"] += 1

    print("abc: " + str(((matches["abc"] * 100)/len(abc))))
    print("coa: " + str(((matches["coa"] * 100) / len(coa))))
    print("pts: " + str(((matches["pts"] * 100) / len(pts))))
    print("simple: " + str(((matches["simple"] * 100) / len(simple))))
    print("redox: " + str(((matches["redox"] * 100) / len(redox))))

    print(len(none))
    print(total)

    print(matches)

    print(len(abc))
    print(len(coa))
    print(len(simple))
    print(len(pts))
    print(len(redox))
    print(len(unkn))

    print("comparable: " + str(len(abc) + len(simple) + len(pts) + len(unkn) + len(redox) + len(coa) + len(none)))



def group_rast_functions(path):

    abc = []
    coa = []
    simple = []
    pts = []
    unkn = []
    redox = []
    none = []

    missing = []

    for line in open(path, "r"):

        line_split = line.split("\t")

        n = line_split[0].strip()
        #reference = line_split[1].strip()
        #gene = line_split[2].strip()
        function = line_split[3].strip()
        transport_types = line_split[4].strip().replace("\"", "").split("; ")

        #this could be written better but was not suposed to be so large

        if re.search("abc", function, re.IGNORECASE) or re.search("atpase", function, re.IGNORECASE) or\
            re.search("atp.binding", function, re.IGNORECASE) or re.search("ATP.synthase", function, re.IGNORECASE) or\
                re.search("3\.A\.1\.", function, re.IGNORECASE) or re.search("ATP.dependent", function, re.IGNORECASE) or\
                re.search("ecf", function, re.IGNORECASE) or re.search("LolC/LolE", function, re.IGNORECASE):
            abc.append(n)
        elif re.search("long-chain", function, re.IGNORECASE) or re.search("-CoA ", function, re.IGNORECASE) or\
                re.search("AMP.dependent", function, re.IGNORECASE) or re.search("coa.ligase", function, re.IGNORECASE):
            coa.append(n)
        elif re.search("uniport", function, re.IGNORECASE) or re.search("antiport", function, re.IGNORECASE) or\
                re.search("symport", function, re.IGNORECASE) or \
                re.search("channel", function, re.IGNORECASE) or re.search("porin ", function, re.IGNORECASE) or\
                re.search(" mfs ", function, re.IGNORECASE) or re.search("exchange", function, re.IGNORECASE) or\
                re.search("outer membrane", function, re.IGNORECASE) or re.search("tonb", function, re.IGNORECASE) or\
                re.search("permease", function, re.IGNORECASE) or re.search("exporter", function, re.IGNORECASE) or\
                re.search("porin", function, re.IGNORECASE) or re.search("facilitator", function, re.IGNORECASE) or\
                re.search("mfs", function, re.IGNORECASE) or re.search("c4.dicarboxylate", function, re.IGNORECASE) or\
                re.search("sss", function, re.IGNORECASE) or re.search("snf", function, re.IGNORECASE) or\
                re.search("sodium.solute.transporter", function, re.IGNORECASE) or re.search("apc", function, re.IGNORECASE) or\
                re.search("TC.[12]\.", function, re.IGNORECASE) or re.search("cotransport", function, re.IGNORECASE) or\
                re.search("tripartite tricarboxylate transporter", function, re.IGNORECASE) or\
                re.search("kup system", function, re.IGNORECASE) or re.search("bcct", function, re.IGNORECASE) or\
                re.search("betl", function, re.IGNORECASE) or re.search("ktrab", function, re.IGNORECASE) or\
                re.search("zip ", function, re.IGNORECASE):
            simple.append(n)
        elif re.search("pts", function, re.IGNORECASE) or re.search("phosphotransferase", function, re.IGNORECASE):
            pts.append(n)
        elif re.search("hypothetical", function, re.IGNORECASE) or\
                re.search("unknown function", function, re.IGNORECASE) or\
                re.search("Uncharacterized", function, re.IGNORECASE) or\
                re.search("putative", function, re.IGNORECASE) or re.search("probable", function, re.IGNORECASE):
            unkn.append(n)
        elif re.search("Cytochrome", function, re.IGNORECASE) or re.search("reductase", function, re.IGNORECASE) or\
                re.search("hydrogenase", function, re.IGNORECASE) or re.search("EC 1\.8\.5\.3", function, re.IGNORECASE)\
                or re.search("EC 1\.1\.1\.122", function, re.IGNORECASE) or re.search("nadh", function, re.IGNORECASE):
            redox.append(n)
        elif "?" == function:
            none.append(n)
        elif function not in missing and "" != function:
            missing.append(function)

    return abc, simple, pts, unkn, coa, redox, none

'''
    for s in missing:
        print(s)

    print(len(abc))
    print(len(coa))
    print(len(simple))
    print(len(pts))
    print(len(redox))
    print(len(none))
    print(len(unkn))
    print(len(missing))
'''

def group_rast_compounds(path):

    cmpd_rast_total = 0
    cmpd_matches = 0

    cmpd_aux = 0
    cmpd_aux_2 = 0

    for line in open(path, "r"):
        line_split = line.split("\t")

        n = line_split[0].strip()
        reference = line_split[1].strip()
        gene = line_split[2].strip()
        function = line_split[3].strip()
        transport = line_split[4].strip().replace("\"", "").split("; ")
        compounds = line_split[5].strip().replace("\"", "").split("; ")

        if re.search("Cellulose", function, re.IGNORECASE):
            cmpd_rast_total += 1
            if "Cellulose" in compounds:
                cmpd_matches += 1
            #lif "Tartrate" in compounds and "Nitrate/nitrite transporter" in function:
                    #and "Ni2+" in compounds and len(compounds) == 6:

                #print(str(compounds) + reference + "\t" + gene + "\t" + function)
                #cmpd_aux_2 += 1

            #elif "Allantoin" in compounds and len(compounds) == 2:
                    #and "Ni2+" in compounds and len(compounds) == 6:
            #    continue
                #print(str(compounds) + reference + "\t" + gene + "\t" + function)
                #cmpd_aux_2 += 1
            #elif "transporting ATPase (EC 3.6.3.3) (EC 3.6.3.5)" in function:
                #print(compounds)
            #else:
                #print(str(compounds) + reference + "\t" + gene + "\t" + function)
                #print(str(n) + "\t" + str(compounds))



    print("total: " + str(cmpd_rast_total))
    print("matches:" + str(cmpd_matches))
    print(cmpd_aux)
    print(cmpd_aux_2)


def get_reactions_distribution_by_genome(path, taxonomies_path, results_path):

    all_types = []
    counts = {}
    taxonomies = {}
    dirs = [f.path for f in os.scandir(path) if f.is_file()]

    for line in open(taxonomies_path, "r"):
        line_split = line.strip().split("\t")
        taxonomies[line_split[0]] = {"tax_id": line_split[1], "lineage":line_split[2]}

    for dir in dirs:

        dir_split = dir.split("/")
        reference = dir_split[len(dir_split)-1].replace(".txt", "")

        reactions_mapping = read_generic_transyt_map_string_list(dir)

        reactions = []

        for gene in reactions_mapping:
            for reaction_id in reactions_mapping[gene]:
                if reaction_id not in reactions:

                    reactions.append(reaction_id)

                    type = get_transport_type_by_id(reaction_id)

                    if type not in all_types:
                        all_types.append(type)

                    if reference not in counts:
                        counts[reference] = {}

                    if type not in counts[reference]:
                        counts[reference][type] = 0

                    counts[reference][type] += 1

    all_types = sorted(all_types)

    save_results_in_xlsx(results_path, all_types, counts, taxonomies)



def save_results_in_xlsx(results_path, types, results, taxonomies):
    book = xlwt.Workbook()
    sheet = book.add_sheet("sheet_1")

    sheet.write(0, 0, "reference_id")

    positions = {}

    col = 0

    for i in range(0, len(types)):
        col = i + 1
        sheet.write(0, col, types[i])
        positions[types[i]] = col

    col += 1
    sheet.write(0, col, "total")
    positions["total"] = col

    col += 1
    sheet.write(0, col, "taxonomy_id")
    positions["taxonomy_id"] = col

    col += 1
    sheet.write(0, col, "lineage")
    positions["lineage"] = col

    row = 1

    for key in results.keys():
        sheet.write(row, 0, key)
        sub_res = results[key]

        total = 0

        for type in types:

            if sub_res is None or type not in sub_res:
                text = 0
            else:
                text = sub_res[type]
                total = total + sub_res[type]

            sheet.write(row, positions[type], text)

        sheet.write(row, positions["total"], total)
        sheet.write(row, positions["taxonomy_id"], int(taxonomies[key]["tax_id"]))
        sheet.write(row, positions["lineage"], taxonomies[key]["lineage"])

        row += 1

    book.save(results_path)



if __name__ == '__main__':

    workdir = "/reference_data"
    rast_annotations_path = workdir + "/RAST/all_rast_annotations.tsv"
    refseq_annotations_path = workdir + "/refseq/all_genes_annotations.tsv"
    #rast_refseq_combined_annotations = workdir + "/RAST/all_rast_and_refseq_combined.tsv"
    rast_annotations_extra_info_path = workdir + "/rast_annotations_extra_info.tsv"
    refseq_annotations_extra_info_path = workdir + "/refseq_annotations_extra_info.tsv"

    # step 1 - create mini reports of each model
    validate_transyt_results(workdir + "/reference_genomes_results", workdir)

    # skippable step - combine rast, refseq and transyt annotations
    #combine_rast_refseq_transyt_annotations(rast_refseq_combined_annotations, workdir)

    # step 2 - complete rast annotations
    modelseed_compounds_mapping = Utilities.read_model_seed_compounds_names()
    add_transport_type_and_compounds_to_rast_or_refseq(
    rast_annotations_path, rast_annotations_extra_info_path, workdir, modelseed_compounds_mapping)

    # step 2.5 - complete refseq annotations
    modelseed_compounds_mapping = Utilities.read_model_seed_compounds_names()
    add_transport_type_and_compounds_to_rast_or_refseq(
        refseq_annotations_path, refseq_annotations_extra_info_path, workdir, modelseed_compounds_mapping)

    # step 3 - compare transport type matches between transyt and rast
    check_results_2(rast_annotations_extra_info_path)

    # step 3.5 - compare transport type matches between transyt and refseq
    check_results_2(refseq_annotations_extra_info_path)

    # step 4 - compare if compounds in transport match
    group_rast_compounds(rast_annotations_extra_info_path)

    get_reactions_distribution_by_genome(workdir + "/refG_reactions_by_gene", workdir + "/taxonomies.tsv",
                                         workdir + "/reactions_distribution.xls")

    # find transporters related to compound in RAST
    check_results(workdir + "/rast_annotations_extra_info.tsv")


''''
    genes_data = read_generic_transyt_map_string_list(workdir + "/refG_data_genes_list.txt")

    rast_data = {}

    for line in open(rast_annotations_path, "r"):

        if 'genome_id' not in line:

            try:

                line_split = line.split("\t")

                reference = line_split[1].strip()
                gene = line_split[2].strip()

                if reference not in rast_data:
                    rast_data[reference] = []

                rast_data[reference].append(gene)

                if gene not in genes_data[reference]:
                    print(reference + "\t" + gene)

            except:
                print(reference)



    for line in open(workdir + "/refG_data_genes_list.txt", "r"):

        line_split = line.split("\t")

        reference = line_split[0].strip()

        if len(line_split) > 1:
            genes = line_split[1].strip().split(";")

            for gene in genes:
                if gene not in rast_data[reference]:
                    print(reference + "\t" + gene)
'''
