from Bio import Entrez
from Bio import SeqIO
import os
import urllib

def retrieve_genbank_files(email, identifier, save_path):

    Entrez.email = email

    handle = Entrez.efetch(db="nucleotide", rettype="gb", id=identifier)
    seq_record = SeqIO.read(handle, "genbank")
    SeqIO.write(seq_record, save_path, 'genbank')


def get_assembly_summary(id):
    """Get esummary for an entrez id"""
    from Bio import Entrez
    esummary_handle = Entrez.esummary(db="assembly", id=id, report="full")
    esummary_record = Entrez.read(esummary_handle)
    return esummary_record

def get_assemblies(term, path, download=True):


    """Download genbank assemblies for a given search term.
    Args:
        term: search term, usually organism name
        download: whether to download the results
        path: folder to save to
    """

    from Bio import Entrez
    #provide your own mail here
    Entrez.email = None #provide email here
    handle = Entrez.esearch(db="assembly", term=term, retmax='200')
    record = Entrez.read(handle)
    ids = record['IdList']
    links = []
    for id in ids:
        #get summary
        summary = get_assembly_summary(id)
        #get ftp link
        url = summary['DocumentSummarySet']['DocumentSummary'][0]['FtpPath_RefSeq']
        if url == '':
            continue
        label = os.path.basename(url)
        #get the fasta link - change this to get other formats
        link = os.path.join(url,label+'_genomic.gbff.gz')
        links.append(link)
        if download == True:
            #download link
            urllib.request.urlretrieve(link, f'{path + "/" + term}.gbff.gz')
    return links

def download_multiple_gbff_files(ids, path):

    i = 0
    previous = 0

    print("0 %")

    for identifier in ids:
        get_assemblies(identifier, path, download=True)

        current = int((i * 100) / len(ids))
        if current > previous:
            previous = current
            print(str(current) + " %")

        i += 1

    print("100 %")

if __name__ == '__main__':

    email = None #provide email here
    path = "/reference_data/refseq"

    #retrieve_genbank_files(email, "79781", path)
    #links = get_assemblies("GCF_000005845.2", path, download=True)