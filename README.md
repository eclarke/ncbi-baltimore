# ncbi-baltimore
Gets the Baltimore ranks (if applicable) from NCBI taxa IDs

## Requirements

Requires: 

- Python 3
- BioPython
- PyYaml

If you're using Sunbeam, these requirements are already met, so I'd suggest simply switching to the `sunbeam` conda environment to run.

## Usage

**Step 1** Get a list of NCBI Taxonomy IDs, one per line. 

### Sunbeam users:
If you're using Sunbeam, these can be found in the `classify/all_samples.tsv` in the first column.

Extract to a file using the following:
```shell
cut -f1 all_samples.tsv | tail -n +3 > taxids.txt
```

**Step 2** Run `get_lineages.py`

```shell
python get_lineages.py -o lineages.txt < taxids.txt
```

## Results

Your output file should be a tab-delimited list with standard taxonomic ranks + Baltimore class for all tax ids passed in.

To check and confirm, run `grep 'Viruses' lineages.txt` and ensure the Baltimore class is shown immediately after 'Viruses'.

