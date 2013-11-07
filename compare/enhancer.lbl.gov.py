import pybedtools
import os
_tmp = pybedtools.BedTool._tmp
fasta = 'enhancer.lbl.gov.fa'
if not os.path.exists(fasta):
    os.system('wget -O enhancer.lbl.gov.fa "http://enhancer.lbl.gov/cgi-bin/imagedb3.pl?page_size=100;show=1;search.result=yes;form=search;search.form=no;action=search;search.sequence=1"')

if not os.path.exists('hg19ToMm9.over.chain.gz'):
    os.system('wget http://hgdownload.cse.ucsc.edu/goldenPath/hg19/liftOver/hg19ToMm9.over.chain.gz')


def gen():
    for line in open(fasta):
        if not line.startswith('>'):
            continue
        toks = line.strip().split('|')
        toks = [i.strip() for i in toks]
        genome, coords, element, result = toks[:4]
        if result != 'positive':
            continue
        if len(toks) > 4:
            name = "|".join(toks[4:] + [genome])
        else:
            name = '.'
        chrom, startstop = coords.split(':')
        start, stop = startstop.split('-')
        yield pybedtools.create_interval_from_list([chrom, start, stop, name])

x = pybedtools.BedTool(gen()).saveas()

human = open(_tmp(), 'w')
mouse = open(_tmp(), 'w')
for i in x:
    if 'Human' in i[-1]:
        human.write(str(i))
    elif 'Mouse' in i[-1]:
        mouse.write(str(i))
human.close()
mouse.close()

os.system('liftOver -bedPlus=4 %s hg19ToMm9.over.chain.gz human-lifted-to-mm9 unmapped' % human.name)
os.system('cat mouse.tmp human-lifted-to-mm9 > enhancer.lbl.gov_positive.bed')
os.system('rm unmapped human-lifted-to-mm9')
