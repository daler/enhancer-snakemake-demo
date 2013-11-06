import os

# read config info into this namespace
include: "conf.py"
workdir: WORKDIR

# In case this is being run on a cluster and only the head node has internet
# access
localrules: download_data


# Construct all the files we're eventually expecting to have.
FINAL_FILES = []

# Results from bowtie -> bed conversion
FINAL_FILES.extend(
    expand(
        'bed/{mark}_{cell}.bed',
        mark=[i[0] for i in lookup.keys()],
        cell=[i[1] for i in lookup.keys()])
)


# Results from BinarizeBed
FINAL_FILES.extend(
    expand(
        'binary/{cell}_{chrom}_binary.txt',
        cell=CELLS,
        chrom=CHROMS)
)


# Results from LearnModel
FINAL_FILES.extend(
    expand(
        'output/{states}-state/{cell}_{states}_segments.bed',
        cell=CELLS,
        states=STATES)
)

# Results from OverlapEnrichment
FINAL_FILES.extend(
    expand(
         'output/{states}-state/{cell}_{states}_enrichment.txt',
         cell=CELLS,
         states=STATES)
)

# Some intermediate files that need to be created
FINAL_FILES.extend(['filetable.txt', 'files_to_compare.txt'])

# These are the files that will be downloaded
FINAL_FILES.extend([os.path.basename(i) for i in lookup.values()])



rule target:
    input: FINAL_FILES


# Get Bowtie files from GEO.
rule download_data:
    output: [os.path.basename(i) for i in lookup.values()]
    run:
        rev_lookup = dict((os.path.basename(i), i) for i in lookup.values())
        for o in output:
            ro = rev_lookup[o]
            shell("wget {ro}")


# Constructs a list of files to use for the enrichment, based on current
# contents of the COMPARE list in config.py.
rule to_compare:
    input: [os.path.join('compare/links/', i) for i in COMPARE]
    output: 'files_to_compare.txt'
    run:
        with open(output[0], 'w') as coordlistfile:
            for c in COMPARE:
                coordlistfile.write(c + '\n')



def inputs(wildcards):
    """
    figure out input files based on the simplified output filename
    """
    return os.path.basename(lookup[wildcards.mark, wildcards.cell])


# Convert Bowtie files to BED4
rule bowtie2bed:
    input: inputs
    output: 'bed/{mark}_{cell}.bed'
    shell: """
    zcat {input} | awk -F "\\t" '{{OFS="\\t"; print $3, $4, $4 + length($5), $2}}' > {output}
    """


# Construct the table that will be provided to BinarizeBed, along with
# corresponding controls
rule make_filetable:
    output: 'filetable.txt'
    run:
        with open(output[0], 'w') as fout:
            for mark, cell in lookup.keys():
                if mark == 'Input':
                    continue

                fout.write('\t'.join([
                    cell,
                    mark,
                    'bed/{mark}_{cell}.bed'.format(**locals()),
                    'bed/Input_{cell}.bed'.format(**locals())]) + '\n')


# Run BinarizeBed.  This will aggregate BED files for different marks, but
# split the aggregate into separate files for each chromosome.
rule binarizebed:
    input: orig=expand('bed/{mark}_{cell}.bed', mark=MARKS, cell=CELLS),
           filetable='filetable.txt'
    output: expand('binary/{{cell}}_{chrom}_binary.txt', chrom=CHROMS)
    shell: """
    java -jar -mx{MEM_PER_THREAD}M {CHROMHMM} BinarizeBed \
        -b {BINSIZE} \
        {ASSEMBLY} bed {input.filetable} binary"""


# Run LearnModel for each of the specified states.  The enrichment step is
# skipped because it is separated out into another rule below.
rule learnmodel:
    input: expand('binary/{cell}_{chrom}_binary.txt', cell=CELLS, chrom=CHROMS)
    output: 'output/{states}-state/{cell}_{states}_segments.bed'
    params: states="{states}"
    log: 'output/{states}-state/{cell}_{states}.log'
    shell: """
    java -jar -mx{MEM_PER_THREAD}M {CHROMHMM} LearnModel \
        -b {BINSIZE} \
        -noenrich \
        binary output/{params.states}-state {params.states} {ASSEMBLY} > {log} 2> {log}"""


# For each model, evaluate enrichment over all states with the files provided
# in COMPARE list in config.py
rule enrichment:
    input: segments='output/{states}-state/{cell}_{states}_segments.bed',
           coordlistfile='files_to_compare.txt'
    output: 'output/{states}-state/{cell}_{states}_enrichment.txt'
    log: 'output/{states}-state/{cell}_{states}_enrichment.log'
    params: prefix='output/{states}-state/{cell}_{states}_enrichment', cell='{cell}'
    shell: """
    java -jar -mx{MEM_PER_THREAD}M {CHROMHMM} OverlapEnrichment \
        -a {params.cell} \
        -f {input.coordlistfile} \
        -b {BINSIZE} \
        -colfields 0,1,2 \
        {input.segments} \
        {INPUTCOORDDIR} \
        {params.prefix} \
    > {log} 2> {log}
    """
