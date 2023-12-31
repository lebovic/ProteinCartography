#!/usr/bin/env python
import pandas as pd
import re
import argparse
import os

# only import these functions when using import *
__all__ = ["extract_foldseekhits"]

# default column names for a Foldseek run in this pipeline
FOLDSEEK_NAMES = [
    "query",
    "target",
    "fident",
    "alnlen",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "tstart",
    "tend",
    "prob",
    "evalue",
    "bits",
    "qcov",
    "tcov",
    "qlan",
    "taln",
    "coord",
    "tseq",
    "taxid",
    "taxname",
]


# parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", nargs="+", required=True, help="Takes .m8 file paths as input."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Returns a .txt file as output."
    )
    parser.add_argument(
        "-e", "--evalue", default="0.01", help="Sets maximum evalue for filtering."
    )
    args = parser.parse_args()

    return args


def extract_foldseekhits(input_files: list, output_file: str, evalue=0.01):
    """
    Takes a list of input tabular Foldseek results files from the API query (ending in .m8).
    Generates a .txt file containing a list of unique accessions across all the .m8 files.

    Args:
        input_files (list): list of string paths to input files.
        output_file (str): path of destination file.
    """

    # empty df for collecting results
    dummy_df = pd.DataFrame()

    # iterate through results files, reading them
    for i, file in enumerate(input_files):
        # load the file
        file_df = pd.read_csv(file, sep="\t", names=FOLDSEEK_NAMES)

        if os.path.getsize(file) == 0:
            continue

        # extract the model ID from the results target column
        file_df["modelid"] = file_df["target"].str.split(" ", expand=True)[0]

        # extract only models that contain AF model string
        # this will need to be changed in the future
        file_df = file_df[file_df["modelid"].str.contains("-F1-model_v4")]

        # filter by evalue
        file_df = file_df[file_df["evalue"] < evalue]

        # get the uniprot ID out from that target
        file_df["uniprotid"] = file_df["modelid"].apply(
            lambda x: re.findall("AF-(.*)-F1-model_v4", x)[0]
        )

        # if it's the first results file, fill the dummy_df
        if i == 0:
            dummy_df = file_df
        # otherwise, add to the df
        else:
            dummy_df = pd.concat([dummy_df, file_df], axis=0)

    # extract unique uniprot IDs
    hits = dummy_df["uniprotid"].unique()

    # save to a .txt file
    with open(output_file, "w+") as f:
        f.writelines(hit + "\n" for hit in hits)


# run this if called from the interpreter
def main():
    # parse arguments
    args = parse_args()

    # collect arguments individually
    input_files = args.input
    output_file = args.output
    evalue = float(args.evalue)

    # send to map_refseqids
    extract_foldseekhits(input_files, output_file, evalue=evalue)


# check if called from interpreter
if __name__ == "__main__":
    main()
