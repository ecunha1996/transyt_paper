import requests
import time


def get_genomeid_by_patricid(patric_id):

    attempt = 0

    while attempt < 3:

        x = requests.get('https://www.patricbrc.org/api/genome/?'
                         'eq(genome_id,' + patric_id + ')&select(genome_id,genbank_accessions)&http_accept=application/json')

        if x.status_code == 200:

            if "genbank_accessions" in str(x.content):

                content = str(x.content).split("\",\"")
                accessions = content[1].split(":")[1]

                genbank = accessions.split(",")[0].replace("\"", "").replace("}]\'", "").strip()

                return genbank

            return None

        else:
            attempt += 1
            time.sleep(30)

def get_genbank_id(patric_id):

    attempt = 0

    while attempt < 3:

        x = requests.get('https://www.patricbrc.org/api/genome/?'
                         'eq(genome_id,' + patric_id + ')&select(genome_id,assembly_accession)&http_accept=application/json')

        if x.status_code == 200:

            if "assembly_accession" in str(x.content):

                content = str(x.content).split("\",\"")

                ids = content[1].split(":")[1]

                genbank = ids.split(",")[0].replace("\"", "").replace("}]\'", "").strip()

                return genbank

            return None

        else:
            attempt += 1
            time.sleep(30)
