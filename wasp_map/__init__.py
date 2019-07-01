"""Utilites for the mapping pipeline from WASP

Examples
--------

wasp.write_positions_snps(
    '~/vcf_dir/chr{}.dose.vcf',
    '~/snp_dir/snps',
    het_only=True,
    r2=0.9,
    samples=args.vcf_sample,
    keep_filtered_vcfs=True
)

wasp.find_intersecting_snps(
    '~/SAMPLE.sort.bam',
    '~/snp_dir',
    is_paired_end=False,
    is_sorted=True,
    output_dir='~/wasp_output_dir'
)

import seqalign
def merge_and_rmdup(*sequence_alignments, paired_end=False, processes=1):
    with seqalign.merge(
        *sequence_alignments,
        dedupper=wasp.RmDup(paired_end=paired_end, processes=processes)
    ) as sa:
        sa.samtools_sort()
        sa.samtools_index()
        sa.remove_duplicates()
        sa.samtools_index()
        return sa
"""

from wasp_pkg.wasp import (
    
)