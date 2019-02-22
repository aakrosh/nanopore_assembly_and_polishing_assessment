from handlers.BamHandler import BamHandler
from handlers.FastaHandler import FastaHandler
from handlers.FileManager import FileManager
from summarize_contig_identities_and_alignments import parse_reads, export_summaries_to_csv
import argparse


'''
Generate stats/plots on contig identity and alignment given a BAM of contigs VS true reference
'''

# read data indexes
READ_ID = 0
REVERSAL_STATUS = 1
REF_ALIGNMENT_START = 2
REF_ALIGNMENT_STOP = 3
ALIGNMENT_LENGTH = 4
READ_LENGTH = 5
CONTIG_LENGTH = 6
N_INITIAL_CLIPPED_BASES = 7
N_MATCHES = 8
N_TOTAL_MISMATCHES = 9
N_TOTAL_DELETES = 10
N_TOTAL_INSERTS = 11
IDENTITY = 12


def process_bam(bam_path, reference_path, output_dir=None):
    """
    Find useful summary data from a bam that can be represented as a table of identities, and a plot of alignments
    :param bam_path: path to a bam containing contigs aligned to a true reference
    :param reference_path: the true reference that contigs were aligned to
    :param output_dir: where to save plots
    :return:
    """

    if output_dir is None:
        output_dir = "plots/"

    FileManager.ensure_directory_exists(output_dir)

    bam_handler = BamHandler(bam_file_path=bam_path)
    fasta_handler = FastaHandler(reference_path)

    chromosome_names = fasta_handler.get_contig_names()

    for chromosome_name in chromosome_names:
        chromosome_length = fasta_handler.get_chr_sequence_length(chromosome_name)

        start = 0
        stop = chromosome_length

        reads = bam_handler.get_reads(chromosome_name=chromosome_name, start=start, stop=stop)

        read_data = parse_reads(reads=reads, fasta_handler=fasta_handler, chromosome_name=chromosome_name)

        total_weighted_identity = sum([x[ALIGNMENT_LENGTH] * x[IDENTITY] for x in read_data])
        total_alignment_bases = sum([x[ALIGNMENT_LENGTH] for x in read_data])

        # Calculate total identity, and approximate 0 if denominator is zero
        total_identity = total_weighted_identity / max(1e-9, total_alignment_bases)
        total_identity = round(total_identity, 6)

        export_summaries_to_csv(read_data=read_data,
                                total_identity=total_identity,
                                chromosome_length=chromosome_length,
                                output_dir=output_dir,
                                bam_path=bam_path,
                                chromosome_name=chromosome_name)


def main(bam_path, reference_path, output_dir):
    process_bam(bam_path=bam_path,
                reference_path=reference_path,
                output_dir=output_dir)


if __name__ == "__main__":
    '''
    Processes arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bam",
        type=str,
        required=True,
        help="BAM file path of contigs aligned to true reference"
    )
    parser.add_argument(
        "--ref",
        type=str,
        required=True,
        help="FASTA file path of true reference to be compared against"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=False,
        help="desired output directory path (will be created during run time if doesn't exist)"
    )

    args = parser.parse_args()

    main(bam_path=args.bam, reference_path=args.ref, output_dir=args.output_dir)
