#!/usr/bin/env python3
#===============================================================================
# wasp.py
#===============================================================================

# Imports ======================================================================

import gzip
import os
import os.path
import subprocess
import tempfile

from wasp_map.env import ANACONDA_DIR, DIR




# Constants ====================================================================

ANACONDA_PATH = os.path.join(ANACONDA_DIR, 'bin', 'python')




# Classes ======================================================================

class RmDup():
    """Remove duplicates with WASP's rmdup script
    
    Instances of this class are callable objects for use with SequenceAlignment
    objects from the seqalign module. Specifically, they should be provided as
    the ``dedupper`` argument.
    
    Attributes
    ----------
    anaconda_path : str
        Path to the python executable of an Anaconda installation
    wasp_dir : str
        Dirname for a WASP repository
    paired_end : bool
        If True, rmdup_pe.py will be used, if False, rmdup.py will be used
    processes : int
        maximum number of processes for samtools view
    """
    
    def __init__(
        self,
        anaconda_path: str = ANACONDA_PATH,
        wasp_dir: str = DIR,
        paired_end: bool = False,
        processes: int = 1,
        temp_dir=None
    ):
        """Settings for the rmdup call
        
        Parameters
        ----------
        anaconda_path : str
            Path to the python executable of an Anaconda installation
        wasp_dir : str
            Dirname for a WASP repository
        paired_end : bool
            If True, rmdup_pe.py will be used, if False, rmdup.py will be used
        processes : int
            maximum number of processes for samtools view
        temp_dir
            directory to use for temporary files
        """
        
        self.anaconda_path = anaconda_path
        self.wasp_dir = wasp_dir
        self.paired_end = paired_end
        self.processes = processes
        self.temp_dir = temp_dir
    
    def __call__(self, bam, log=None):
        """Dedup a BAM file
        
        The bam attribute of the associated SequenceAlignment is written to
        disk, dedupped, and read back into memory
        
        Parameters
        ----------
        bam : bytes
            BAM file in the form of a bytes object
        log : file object
            File where logging information will be written
        temp_dir
            directory for temporary files
        """
        
        with tempfile.NamedTemporaryFile(dir=self.temp_dir) as (
            temp_bam
        ), tempfile.NamedTemporaryFile(dir=self.temp_dir, suffix='.bam') as (
            temp_dedupped
        ):
            temp_bam.write(bam)
            subprocess.call(
                (
                    self.anaconda_path,
                    os.path.join(
                        self.wasp_dir,
                        'mapping/rmdup{}.py'.format('_pe' * self.paired_end)
                    ),
                    temp_bam.name,
                    temp_dedupped.name
                )
            )
            with subprocess.Popen(
                (
                    'samtools',
                    'view',
                    '-bh',
                    '-@', str(self.processes),
                    temp_dedupped.name
                ),
                stdout=subprocess.PIPE,
                stderr=log
            ) as samtools_view:
                return samtools_view.communicate()[0]




# Functions ====================================================================

def get_vcf_sample_indices(sample_ids, ids_to_include=None):
    """Get the indices of the samples to be included in the analysis
    
    Parameters
    ----------
    sample_ids : list, tuple
        All sample IDs in the input VCF file
    ids_to_include : set
        All sample IDs to be included in the analysis. If not provided, all
        samples will be included.
    
    Returns
    -------
    tuple
        Indices for all sample IDs indicated for inclusion in downstream
        analysis
    """
    
    return tuple(
        i
        for i in range(len(sample_ids))
        if ((sample_ids[i] in ids_to_include) if ids_to_include else True)
    )


def get_vcf_column_headers(line, sample_ids, sample_indices):
    """Get VCF column headers, including only relevant samples
    
    Parameters
    ----------
    line : str
        A line from a vcf file (e.g. from an open file descriptor)
    sample_ids : list, tuple
        All sample IDs in the input VCF file
    sample_indices : container
        Indices indicating which samples from sample_ids should be kept
    
    Returns
    -------
    list
        Column headers for the output VCF file
    """
    
    return line.split()[:9] + [sample_ids[i] for i in sample_indices]


def any_heterozygous(genotypes):
    """Determine if any of the genotypes are heterozygous
    
    Parameters
    ----------
    genoytypes : container
        Genotype for each sample of the variant being considered
    
    Returns
    -------
    bool
        True if at least one sample is heterozygous at the variant being
        considered, otherwise False
    """
    
    return bool(
        {'0|1', '1|0', '0/1'}
        & {genotype.split(':')[0] for genotype in genotypes}
    )


def is_genotyped_or_well_imputed(filter, info, r2=0):
    """Determine if the current variant was genotyped or was well-imputed
    
    Parameters
    ----------
    filter : str
        Data from the FILTER column of an imputed VCF file
    info : str
        Data from the INFO column of an imputed VCF file
    r2 : float
        R-squared threshold for inclusion based on imputation quality
    
    Returns
    -------
    bool
        True if the current variant either was genotyped or was well-imputed,
        (i.e. imputation quality exceeds threshold) False otherwise.
    """
    
    return bool(
        ({'GENOTYPED', 'GENOTYPED_ONLY'} & set(filter.split(';')))
        or (
            float(
                dict(tuple(pair.split('=')) for pair in info.split(';')).get(
                    'R2', 0
                )
            )
            > r2
        )
    )


def generate_filtered_vcf(
    vcf,
    het_only: bool = False,
    r2: float = 0,
    samples=None
):
    """Loop over the variants and yield those that pass filters
    
    Parameters
    ----------
    vcf : file object
        A VCF file
    het_only : bool
        If True, only heterozygous variants are included in the output
    r2 : float
        R-squared threshold for inclusion based on imputation quality
    samples
        Samples from the VCF to be included in analysis
    
    Yields
    -------
    str
        A line of the output VCF file
    """
    
    for line in vcf:
        if line.startswith('##'):
            yield line.rstrip()
            continue
        if line.startswith('#CHROM'):
            sample_ids = line.split()[9:]
            sample_indices = get_vcf_sample_indices(sample_ids, samples)
            yield '\t'.join(
                get_vcf_column_headers(line, sample_ids, sample_indices)
            )
            continue
        
        (
            chrom, pos, id, ref, alt, qual, filter, info, format, *genotypes
        ) = line.split()
        genotypes = tuple(genotypes[i] for i in sample_indices)
        if het_only and not any_heterozygous(genotypes):
            continue
        if r2 > 0 and (not is_genotyped_or_well_imputed(filter, info, r2)):
            continue
        
        yield '\t'.join(
            (chrom, pos, id, ref, alt, qual, filter, info, format, *genotypes)
        )


def generate_positions_from_vcf(vcf):
    """From a VCF file, generate a positions file for use with samtools mpileup
    
    Parameters
    ----------
    vcf : file object
        A VCF file
    
    Yields
    ------
    str
        A line of the output positions file (``chr{chromosome}\t{position}``)
    """
    
    yield from (
        'chr{}\t{}'.format(chr, pos)
        for chr, pos
        in (line.split()[:2] for line in vcf if not line.startswith('#'))
    )


def write_positions_and_filtered_vcfs(
    input_format: str,
    output_prefix: str,
    het_only: bool = False,
    r2: float = 0,
    samples=None
):
    """Write a positions file and filtered VCF files for use with WASP
    
    Parameters
    ----------
    input_format : str
        A format string for the input VCF files (which are split by chromosome).
        ``{}`` will be replaced by a chromosome number or character.
    output_prefix : str
        Prefix for output files
    het_only : bool
        If True, only heterozygous variants will be included in the output
    r2 : float
        R-squared threshold for inclusion based on imputation quality
    samples
        Samples from the VCF file to be included in the output
    """
    
    positions = []
    for chr in range(1, 23):
        try:
            with gzip.open(input_format.format(chr), 'rt') as f_in:
                with gzip.open(
                    '{}.chr{}.vcf.gz'.format(output_prefix, chr),
                    'wt'
                ) as f_out:
                    filtered_vcf = tuple(
                        generate_filtered_vcf(
                            f_in, het_only=het_only, r2=r2, samples=samples
                        )
                    )
                    positions.extend(
                        list(generate_positions_from_vcf(filtered_vcf))
                    )
                    f_out.write('\n'.join(filtered_vcf) + '\n')
        except FileNotFoundError:
            print(f'File for chr{chr} not found, skipping')
    if len(positions) < 1:
        raise Exception(
            'No SNPs passed filtering - did you forget to set --r2 0 ?'
        )
    with open('{}.positions.txt'.format(output_prefix), 'w') as f:
        f.write('\n'.join(positions) + '\n')
    

def get_snps_from_vcfs(vcf_dir: str, snp_dir: str, wasp_dir: str = DIR):
    """Use WASP's `extract_vcf_snps.sh` script to create SNP files from VCFs
    
    Parameters
    ----------
    vcf_dir : str
        Path to directory containing input VCFs
    snp_dir : str
        Directory for output files
    wasp_dir : str
        Directory containing WASP repo
    """

    subprocess.call(
        (
            os.path.join(wasp_dir, 'mapping/extract_vcf_snps.sh'),
            vcf_dir,
            snp_dir
        )
    )


def write_positions_snps(
    vcf_format: str,
    output_prefix: str,
    het_only: bool = False,
    r2: float = 0,
    samples=None,
    wasp_dir: str = DIR,
    keep_filtered_vcfs: bool = False
):
    """Write the SNP files and position file required for WASP and mpileup
    
    Parameters
    ----------
    vcf_format : str
        A format string for the input VCF files (which are split by chromosome).
        ``{}`` will be replaced by a chromosome number or character.
    output_prefix : str
        Prefix for output files
    het_only : bool
        If True, only heterozygous variants will be included in the output
    r2 : float
        R-squared threshold for inclusion based on imputation quality
    samples : set
        Samples from the VCF file to be included in the output
    wasp_dir : str
        Directory containing WASP repo
    keep_filtered_vcfs : bool
        If True, filtered VCF files will not be removed after SNP files have
        been written
    """
    
    write_positions_and_filtered_vcfs(
        vcf_format,
        output_prefix,
        het_only=het_only,
        r2=r2,
        samples=samples
    )
    output_dir = os.path.dirname(output_prefix)
    get_snps_from_vcfs(
        output_dir,
        output_dir,
        wasp_dir=wasp_dir
    )
    if not keep_filtered_vcfs:
        for chr in range(1, 23):
            os.remove('{}.chr{}.vcf.gz'.format(output_prefix, chr))


def find_intersecting_snps(
    bam_filename,
    snp_dir,
    anaconda_path: str = ANACONDA_PATH,
    wasp_dir: str = DIR,
    is_paired_end=False,
    is_sorted=False,
    output_dir=None,
    temp_dir=None
):
    """Run WASP's `find_intersecting_snps.py` script
    
    Parameters
    ----------
    bam_filename : str, bytes
        Path to input BAM file on disk, or BAM file as a bytes object
    snp_dir
        Directory containing SNP files
    anaconda_path : str
            Path to the python executable of an Anaconda installation
    wasp_dir : str
        Dirname for a WASP repository
    is_paired_end : bool
        if True, the --is_paired_end flag will be passed
    is_sorted : bool
        if True, the --is_sorted flag will be passed
    output_dir : str
        Directory for output files
    temp_dir
        directory for temporary files
    """
    
    bam_in_memory = isinstance(bam_filename, bytes)
    if bam_in_memory:
        temp_bam = tempfile.NamedTemporaryFile(dir=temp_dir)
        temp_bam.write(bam_filename)
        bam_filename = temp_bam.name
    
    subprocess.run(
        (
            anaconda_path,
            os.path.join(wasp_dir, 'mapping/find_intersecting_snps.py'),
            bam_filename,
            '--snp_dir', snp_dir,
        )
        + ('--is_paired_end',) * is_paired_end
        + ('--is_sorted',) * is_sorted
        + ('--output_dir', output_dir,) * bool(output_dir)
    )
    
    if bam_in_memory:
        temp_bam.close()


def filter_remapped_reads(
    to_remap_bam: str,
    remap_bam: str,
    keep_bam: str,
    anaconda_path: str = ANACONDA_PATH,
    wasp_dir: str = DIR,
):
    """Run WASP's `filter_remapped_reads` script
    
    Parameters
    ----------
    to_remap_bam : str
        path to .to.remap.bam file on disk
    remap_bam : str
        path to remapped BAM file on disk
    keep_bam : str
        path to .keep.bam file on disk
    anaconda_path : str
        Path to the python executable of an Anaconda installation
    wasp_dir : str
        Dirname for a WASP repository
    """
    
    subprocess.run(
        (
            anaconda_path,
            os.path.join(wasp_dir, 'mapping/filter_remapped_reads.py'),
            to_remap_bam,
            remap_bam,
            keep_bam
        )
    )
