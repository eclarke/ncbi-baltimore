import os
import sys
import time
import pprint
import itertools
import functools
import subprocess
import csv
import yaml
import argparse

from urllib.error import HTTPError

from Bio import Entrez



## Replace this!
try:
    Entrez.email = subprocess.getoutput("git config --get user.email")
except subprocess.CalledProcessError:
    pass

Taxonomy = yaml.load(open('taxa.yaml'))
TaxRanks = Taxonomy['Ranks']
Baltimore = Taxonomy['Baltimore']

def get_baltimore_group(LineageEx):
    for r in LineageEx:
        if r['Rank'] == 'no rank' and r['ScientificName'] in Baltimore:
            return r['ScientificName']

        
def get_taxa(tax_ids, out_filename):
    """Write table with reads and full tax. info for a list of taxids."""
    # Post list to NCBI
    tax_info = list(itertools.chain.from_iterable(_ncbi_get_many_taxa(tax_ids)))
    lineages = []
    for t in tax_info:
        LineageEx = t.get('LineageEx', ())
        _lineage = {r['Rank']: r['ScientificName'] for r in LineageEx}
        _lineage['baltimore'] = get_baltimore_group(LineageEx)
        _lineage['name'] = t.get('ScientificName', 'NA')
        lineages.append(_lineage)
    assert(len(lineages) == len(tax_ids))
    with open(out_filename, 'w') as out:
        writer = csv.DictWriter(
            out,
            fieldnames=TaxRanks + ['tax_id'],
            delimiter='\t',
            quoting=csv.QUOTE_MINIMAL,
            extrasaction='ignore',
            restval='NA'
        )
        writer.writeheader()
        rows = ({"tax_id":x, **y} for x, y in zip(tax_ids, lineages))
        writer.writerows(rows)


def _ncbi_get_many_taxa(ids, batch_size=5000):
    saved = Entrez.read(Entrez.epost('taxonomy', id=','.join(map(str, ids))))
    webenv = saved['WebEnv']
    query_key = saved['QueryKey']
    for start in range(0, len(ids), batch_size):
        end = min(len(ids), start + batch_size)
        attempt = 1
        while attempt <= 3:
            try:
                handle = Entrez.efetch(
                    db='taxonomy', retstart=start, retmax=batch_size,
                    webenv=webenv, query_key=query_key)
                break
            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print("NCBI server error ({}); retrying ({}/3)".format(err.code, attempt))
                    attempt += 1
                    time.sleep(15)
                else:
                    raise
        yield(Entrez.read(handle))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        type=argparse.FileType('r'),
        help="Input list of taxids, one per line",
        default=None)
    parser.add_argument(
        "-o", "--output",
        help="Name of output file",
        default="lineages.txt")

    args = parser.parse_args()

    _input = args.input if args.input else sys.stdin
    
    tax_ids = [t.strip() for t in _input.readlines()]
    get_taxa(tax_ids, args.output)
