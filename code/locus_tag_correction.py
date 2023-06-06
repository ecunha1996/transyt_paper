
from Bio import SeqIO
import os

def main(gb_file, fasta_file):
    gb = SeqIO.parse(gb_file, format='genbank')
    fasta = SeqIO.parse(fasta_file, format='fasta')

    protein_ids_locust_tag_map = {}

    for record in gb:
        for feature in record.features:
            if feature.type == "CDS":
                if "protein_id" in feature.qualifiers and "locus_tag" in feature.qualifiers:
                    protein_ids_locust_tag_map[feature.qualifiers['protein_id'][0]] = feature.qualifiers['locus_tag'][0]

    res = []
    for record in fasta:
        record.id = protein_ids_locust_tag_map[record.id]
        record.description = ""
        res.append(record)

    SeqIO.write(res, f"{fasta_file.split('/')[0]}/protein.faa", "fasta")


def correct_pseudomonas(fasta_file="GCA_000166315.1_ASM16631v1_protein.faa"):
    seqrecord = SeqIO.parse(fasta_file, format='fasta')
    res = []
    for record in seqrecord:
        locus_tag = record.description.split('locus_tag=')[1].split("]")[0].strip()
        record.id = locus_tag
        record.description = ""
        res.append(record)
    SeqIO.write(res, "Paeruginosa/protein.faa", "fasta")



if __name__ == '__main__':
    data_dir = r"../case_study"
    os.chdir(data_dir)
    # main(gb_file = "sequence(1).gb", fasta_file="GCA_000166315.1_ASM16631v1_protein.faa")
    # main(gb_file="Scerevisiae/GCF_000146045.2_R64_genomic.gbff", fasta_file="Scerevisiae/GCF_000146045.2_R64_protein.faa")
    # main(gb_file="Olucimarinus/GCF_000092065.1_ASM9206v1_genomic.gbff", fasta_file="Olucimarinus/GCF_000092065.1_ASM9206v1_protein.faa")
    # correct_pseudomonas("Paeruginosa/sequence.txt")