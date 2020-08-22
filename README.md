# LINNAEUS corpus tools

Work related to the LINNAEUS corpus.

## Converting LINNAEUS to standoff

Download `manual-corpus-species-1.1.tar.gz` from http://linnaeus.sourceforge.net/ and unpack with `tar xzf manual-corpus-species-1.1.tar.gz` or

```
wget https://github.com/spyysalo/linnaeus-corpus-data/archive/v1.1.tar.gz \
    -O manual-corpus-species-1.1.tar.gz
tar xvzf manual-corpus-species-1.1.tar.gz
mv linnaeus-corpus-data-1.1 manual-corpus-species-1.1
```

Convert to standoff and create copies of standoff split to train, devel and test subdirectories:

```
mkdir standoff
python tools/linnaeus2ann.py manual-corpus-species-1.1/{tags.tsv,txt} standoff
for s in train devel test; do
    mkdir -p split-standoff/$s
    cat split/${s}.txt | while read f; do
        cp standoff/${f}.* split-standoff/$s
    done
done
```

Convert to CoNLL format (NOTE: does not preserve original annotation offsets that do not match token boundaries)

```
git clone https://github.com/spyysalo/standoff2conll
mkdir conll
for s in train devel test; do
    python3 standoff2conll/standoff2conll.py split-standoff/$s > conll/$s.tsv
done
```
