import pybedtools
import os
fasta = 'enhancer.lbl.gov.fa'
if not os.path.exists(fasta):
    os.system('wget -O enhancer.lbl.gov.fa "http://enhancer.lbl.gov/cgi-bin/imagedb3.pl?page_size=100;show=1;search.result=yes;form=search;search.form=no;action=search;search.sequence=1"')


def gen():
    for line in open(fasta):

        if not line.startswith('>Mouse'):
            continue
        toks = line.strip().split('|')
        toks = [i.strip() for i in toks]
        _, coords, element, result = toks[:4]
        if result != 'positive':
            continue
        if len(toks) > 4:
            tissues = "|".join(toks[4:])
        else:
            tissues = '.'
        chrom, startstop = coords.split(':')
        start, stop = startstop.split('-')
        yield pybedtools.create_interval_from_list([chrom, start, stop, tissues])

x = pybedtools.BedTool(gen()).saveas('enhancer.lbl.gov_mouse_positive.bed')
