# linnaeus-corpus

Work related to the LINNAEUS corpus.

## Converting LINNAEUS to standoff

Download `manual-corpus-species-1.0.tar.gz` from http://linnaeus.sourceforge.net/

Unpack, convert to standoff, and create copies of standoff split to train, devel and test subdirectories:

    tar xzf manual-corpus-species-1.0.tar.gz
    mkdir standoff
    python tools/linnaeus2ann.py manual-corpus-species-1.0/{tags.tsv,txt} standoff
    for s in train devel test; do
        mkdir -p split-standoff/$s
        cat split/${s}.txt | while read f; do
            cp standoff/${f}.* split-standoff/$s
        done
    done
