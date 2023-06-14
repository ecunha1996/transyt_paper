from Bio import SeqIO

def write_faa(path, search_taxonomy = True):

    filepath = path + "/genome.gbff"
    newFile = path + "/protein.faa"

    record = SeqIO.read(filepath, "genbank")

    dic = {}
    taxid = None

    for feature in record.features:
        if feature.type == "source":
            if "db_xref" in feature.qualifiers.keys():
                for ref in feature.qualifiers["db_xref"]:
                    if "taxon" in ref:
                        taxid = ref.split(":")[1]

        if feature.type == "CDS":

            if "locus_tag" in feature.qualifiers.keys():
                locus_tag = feature.qualifiers["locus_tag"][0]
            else:
                locus_tag = None

            if "protein_id" in feature.qualifiers.keys() and "translation" in feature.qualifiers.keys():
                protein_id = feature.qualifiers["protein_id"][0]

                if locus_tag is None:
                    locus_tag = protein_id

                sequence = feature.qualifiers["translation"][0]

                if locus_tag not in dic.keys():
                    dic[locus_tag] = {"protein_id": protein_id, "sequence": sequence}

    if search_taxonomy and taxid is not None:
        f = open(path + "params.txt", "w+")
        f.write("taxID\t" + str(taxid))
        f.close()

    f = open(newFile, "w")

    for locus in dic.keys():
        f.write(">" + locus + "\n")
        f.write(dic[locus].get("sequence") + "\n")
        f.write("\n")

    f.close()


if __name__ == '__main__':

    path = None #path to the directory containing the files
    write_faa(path)
