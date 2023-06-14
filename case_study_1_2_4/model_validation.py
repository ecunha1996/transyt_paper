import cobra
import re
import Utilities

def compounds_by_gene(model_path):
    model = cobra.io.read_sbml_model(model_path)

    genes = {}

    for reaction in model.reactions:

        l = []

        for metabolite in reaction.metabolites:
            suffix = "_" + metabolite.compartment + str(metabolite.charge)
            id = metabolite.id.replace(suffix, "")

            if id not in l:
                l.append(id.strip())

        rule = reaction.gene_reaction_rule.replace(" and ", " or ").replace(" )", "").replace("( ", "").split(" or ")

        for gene in rule:

            if gene not in genes:
                genes[gene] = []

            compounds = genes[gene]

            for id in l:
                if id not in compounds:
                    compounds.append(id.strip())

        genes[gene] = compounds

        genes

    for gene in genes:
        res = genes[gene]
        res.sort()
        print(gene + "\t" + str(len(res)) + "\t" + str(res).replace("'", "").replace("[", "").replace("]", ""))

    print(len(genes.keys()))


def strip_gene_rule(rule):

    genes = []

    aux_split = rule.replace(" and ", " or ").replace(" )", "").replace("( ", "").split(" or ")

    for gene in aux_split:
        if gene not in genes:
            genes.append(gene)

    return genes


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text)]

def compareSameSizeLists(l1, l2):

    if not isinstance(l1, list):
        l1 = l1.split(", ")

    if not isinstance(l2, list):
        l2 = l2.split(", ")

    for s in l1:
        if s not in l2:
            #print(s)
            return False

    for s in l2:
        if s not in l1:
            #print(s)
            return False

    return True

def compareListsInFile(path, sublistSearch):

    f = open(path, "r")

    l1 = ''
    l2 = ''
    g = ''

    for x in f:
        if x[0] == 'b':
            line = x.split("\t")
            g = line[0].strip()
            l1 = line[2].strip()
            l2 = line[3].strip()

            res = None
            if(sublistSearch):
                res = isSublistOf(l1, l2)
            else:
                res = compareSameSizeLists(l1, l2)
            if not res:
                print(g + "\t" + str(res))

def isSublistOf(string1, string2):

    l1 = string1.split(", ")
    l2 = string2.split(", ")

    for s in l1:
        if s not in l2:
            print(s)
            return False

    return True

def read_Excel_File(path):

    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(2)

    for i in range(sheet.ncols):
        print(sheet.cell_value(0, i))
        #for j in range(sheet.nrows):
            #print(sheet.cell_value(j, i))

def reactions_by_gene(model_path, transporters_only=False):

    transporters = []

    model = cobra.io.read_sbml_model(model_path)

    genes = {}

    print("reactions_total: " + str(len(model.reactions)))

    for reaction in model.reactions:

        reaction_id = reaction.id

        compartments = []

        for metabolite in reaction.metabolites:
            comp = metabolite.compartment
            if comp not in compartments:
                compartments.append(comp)

        save = True

        if transporters_only and len(compartments) < 2:
            save = False
        elif len(compartments) > 1 and reaction_id not in transporters:
            transporters.append(reaction_id)

        if save:
            rule = reaction.gene_reaction_rule.replace(" and ", " or ").replace(" )", "").replace("( ", "").split(" or ")

            for gene in rule:
                if gene not in genes:
                    genes[gene] = []

                reactions = genes[gene]

                if reaction_id not in reactions:
                    reactions.append(reaction_id)

            genes[gene] = reactions

    for gene in genes:
        print(gene + "\t" + str(len(genes[gene])) + "\t" + str(genes[gene]))

    print(len(genes))
    print("transporters: " + str(len(transporters)))

def get_reactions_in_list(model_path, reactions_path, bigg_to_seed_path):

    compounds_by_reaction = {}
    reversibility = {}

    compounds_bigg_to_seed = Utilities.read_dic(bigg_to_seed_path)

    model = cobra.io.read_sbml_model(model_path)

    for line in open(reactions_path, "r"):

        reaction_id = line.strip()

        reaction = model.reactions.get_by_id(reaction_id)

        reversibility[reaction_id] = reaction.reversibility

        l = []

        for metabolite in reaction.metabolites:
            suffix = "_" + metabolite.compartment
            id = metabolite.id.replace(suffix, "").strip()

            seed_id = None

            if id in compounds_bigg_to_seed:
                seed_id = compounds_bigg_to_seed[id]

            if seed_id not in l:
                l.append(seed_id)

        if len(l) == 2 and "cpd00067" in l:
            l.remove("cpd00067")

        compounds_by_reaction[reaction_id] = l



    return compounds_by_reaction, reversibility

def find_match_in_transyt_reactions(model_path, compounds_by_reaction, reversibility_bigg):

    model = cobra.io.read_sbml_model(model_path)

    for reaction in model.reactions:

        l = []

        for metabolite in reaction.metabolites:
            suffix = "_" + metabolite.compartment + str(metabolite.charge)
            id = metabolite.id.replace(suffix, "")

            if id not in l:
                l.append(id.strip())

        for bigg_reaction in compounds_by_reaction.keys():

            #if reaction.id == "TI0000092" and bigg_reaction == "URAtpp":
            #    print(compounds_by_reaction[bigg_reaction])

            if len(l) == len(compounds_by_reaction[bigg_reaction]):
                match = compareSameSizeLists(l, compounds_by_reaction[bigg_reaction])

                if match:
                    same_rev = reaction.reversibility == reversibility_bigg[bigg_reaction]

                    print(bigg_reaction + "\t" + reaction.id + "\t" + str(same_rev) + "\t" + reaction.gene_reaction_rule)




if __name__ == '__main__':

    path = "/ecoli/ecoli_iML1515_new/"

    transyt_model = path + "results/results/transyt.xml"
    model_fix_path = path + 'Validation/transporters_sbml.xml'

    Utilities.fix_model_to_cobra_format(transyt_model, model_fix_path)

    compounds_by_gene(model_fix_path)

    reactions_by_gene(model_fix_path, True)

    compareListsInFile(path + "Validation/compounds.txt", True)

    bigg_model = '/ecoli/ecoli_iML1515/iML1515.xml'
    reactions_by_gene(path + "iML1515.xml", True)

    reactions_by_gene(bigg_model, True)

    compounds_by_reaction, reversibility = get_reactions_in_list(path + "iML1515.xml", path + "iML1515_no_gpr_reactions_test.txt",
                          "/ecoli/bigg_to_seed.txt")

    find_match_in_transyt_reactions(model_fix_path, compounds_by_reaction, reversibility)