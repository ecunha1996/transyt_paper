import re

def count_organisms_in_TCDB(fasta_path):

    file = open(fasta_path, "r")
    organisms = {}

    for line in file.readlines():

        if ">" in line:
            text = line.strip().split("|")[3].strip()

            organism = None

            if "OS=" in text:
                aux_split = text.split("OS=")[1].split(" ")

                organism = ""

                for aux in aux_split:
                    if "=" in aux:
                        break
                    else:
                        organism = organism + " " + aux

                organism = organism.replace("[", "").replace("]", "")

            elif " - " in text:
                organism = text.split(" - ")[1].split(" (")[0]
            elif " [[" in text:
                organism = text.split(" [[")[1].replace("]", "")
            elif " [" in text:
                organism = text.split(" [")[1].replace("]", "")

            if organism is not None and "=" not in organism and ";" not in organism:

                if "bacterium (" in organism:
                    organism = organism.split(" (")[1].split(") ")[0]

                organism = re.sub('\.$', '', str(organism)).strip()

                if organism not in organisms:
                    organisms[organism] = 1
                else:
                    organisms[organism] = organisms[organism] + 1

    keys = sorted(organisms.keys())

    for key in keys:
        print(key + "\t" + str(organisms[key]))



if __name__ == "__main__":

    fasta_path = None #path to public TCDB fasta file

    count_organisms_in_TCDB(fasta_path)