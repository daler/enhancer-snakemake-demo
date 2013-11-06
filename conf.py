# Configuration details for running the ChromHMM segmentation Snakefile.
#
# Minor changes to this file should be sufficient to customize to your
# location.


# Absolute path to where the Snakefile lives
WORKDIR = "/data/segmentation"

# Path to ChromHMM
CHROMHMM = '/tools/ChromHMM.jar'

# Numbers of states to run
STATES = [2, 3, 4, 5]

# In MB.  Generally there will be one thread per state in the STATES list.
MEM_PER_THREAD = 4000

# Binsizes to use for ChromHMM commands
BINSIZE = 200

# Genome assembly.  This should also be the name of a chromsizes file in the
# workdir.
ASSEMBLY = 'mm9'

# Map original Bowtie output on GEO to (mark, celltype) tuples.  This will take
# care of most of the messy path business.
lookup = {
    ('H3K4me1', 'embryonic-liver'):
        ('ftp://ftp.ncbi.nlm.nih.gov/geo/samples/GSM851nnn/GSM851299/suppl/'
         'GSM851299_RenLab-H3K4me1-embryonic-liver-DM623.bowtie.gz'),
    ('H3K4me3', 'embryonic-liver'):
        ('ftp://ftp.ncbi.nlm.nih.gov/geo/samples/GSM851nnn/GSM851300/suppl/'
         'GSM851300_RenLab-H3K4me3-embryonic-liver-DM590.bowtie.gz'),
    ('Pol2', 'embryonic-liver'):
        ('ftp://ftp.ncbi.nlm.nih.gov/geo/samples/GSM851nnn/GSM851301/suppl/'
         'GSM851301_RenLab-Pol2-embryonic-liver-DM743.bowtie.gz'),
    ('H3K27ac', 'embryonic-liver'):
        ('ftp://ftp.ncbi.nlm.nih.gov/geo/samples/GSM851nnn/GSM851302/suppl/'
         'GSM851302_RenLab-H3K27ac-embryonic-liver-DM749.bowtie.gz'),
    ('Input', 'embryonic-liver'):
        ('ftp://ftp.ncbi.nlm.nih.gov/geo/samples/GSM851nnn/GSM851303/suppl/'
         'GSM851303_RenLab-Input-embryonic-liver-DM573.bowtie.gz'),
}


# BED files to check for enrichment against -- whose basenames are in the
# COMPARE list -- are stored here
INPUTCOORDDIR = 'compare/links'

# BED files to check for enrichment against.  Can be gzipped or not.  To
# refresh changes after modifying this COMPARE list, run:
#
#   snakemake -R to_compare
#
TO_COMPARE = [
    'compare/links/CTCF_MEL.bed.gz',
    'compare/links/Rad21_MEL.bed.gz',
    'compare/links/c-Myc_MEL.bed.gz',
    'compare/links/Gata1_erythroblast.bed.gz',
    'compare/links/Gata1_MEL.bed.gz',
    'compare/links/P300_MEL.bed.gz',
    'compare/links/Tal1_erythroblast.bed.gz',
    'compare/links/Tal1_MEL.bed.gz',
    #'intergenic.bed',
    #'intergenic_between_genes.bed',
    'compare/links/mouse_enhancers.bed',
    os.path.join(os.path.dirname(CHROMHMM), 'COORDS', ASSEMBLY, 'RefSeqTSS.mm9.bed.gz'),
    os.path.join(os.path.dirname(CHROMHMM), 'COORDS', ASSEMBLY, 'RefSeqTES.mm9.bed.gz'),
]

# Ensures that all the files we want to use are either symlinked to the
# INPUTCOORDIR directory or are already there.
COMPARE = []
for fn in TO_COMPARE:
    basename = os.path.basename(fn)
    if fn.startswith(INPUTCOORDDIR):
        COMPARE.append(basename)
    else:
        target = fn
        linkname =  os.path.join(INPUTCOORDDIR, basename)
        print(target, linkname)
        os.system('ln -sf %s %s' % (target, linkname))
        COMPARE.append(basename)



# Automatically gets a list of marks and cells.  It's unlikely that this would
# need to be changed, but it's kept in this config file just in case.
MARKS, CELLS = zip(*lookup.keys())

# Chromosomes may need to be customized depending on what chroms are included
# in the original data.
CHROMS = [
    i.split()[0] for i in open(ASSEMBLY) if 'random' not in i and 'M' not in i
]
