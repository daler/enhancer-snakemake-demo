import os
if not os.path.exists('links'):
    os.makedirs('links')
for line in open('lookup.txt'):
    if line.startswith('#'):
        continue
    toks = line.strip().split()
    if len(toks) == 0:
        continue
    label, url = toks
    basename = os.path.basename(url)
    os.system('wget %s -O %s' % (url, basename))
    os.system('cd links && ln -sf ../%s %s' % (basename, label + '.gz'))
