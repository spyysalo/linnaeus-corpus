import io

from os import path

class FormatError(Exception):
    pass

class Annotation(object):
    def __init__(self, docid, start, end, text, norm, code):
        self.docid = docid
        self.start = start
        self.end = end
        self.text = text
        self.norm = norm
        self.code = code

    def verify(self, text):
        if text[self.start:self.end] != self.text:
            raise FormatError(
                'text mismatch: annotation "%s", document "%s"' %
                (self.text, text[self.start:self.end]))

    def to_standoff(self, idx):
        """Return list of annotation strings in the .ann standoff format."""
        anns = []
        anns.append(u'T%d\tSpecies %d %d\t%s' %
                    (idx, self.start, self.end, self.text))
        anns.append(u'N%d\tReference T%d %s' % (idx, idx, self.norm))
        # TODO: add Attribute for code
        return anns

class Document(object):
    def __init__(self, id_, text, annotations=None):
        if annotations is None:
            annotations = []
        self.id = id_
        self.text = text
        self.annotations = annotations

    def verify_annotations(self):
        for a in self.annotations:
            a.verify(self.text)

    def to_standoff(self):
        """Return list of annotation strings in the .ann standoff format."""
        anns = []
        for idx, a in enumerate(self.annotations, start=1):
            anns.extend(a.to_standoff(idx))
        return anns
        
def read_linnaeus_annotations(flo):
    """Read LINNAEUS annotations from file-like object, return list of
    Annotation objects.
    
    The format consists of a header line and TAB-separated fields

        SPECIES-ID DOC-ID START END TEXT CODE

    where SPECIES-ID is the NCBI Taxonomy identifier of the annotated
    species mention, DOC-ID is the PMC identifier of the document,
    START and END are the span of the annotation in the document, TEXT
    is the annotated text and CODE identifies special types of
    mentions such as misspellings.
    """

    # Confirm and discard header
    header = next(flo)
    if not header.startswith('#'):
        raise FormatError('missing header')

    annotations = []
    for ln, line in enumerate(flo, start=1):
        line = line.rstrip('\n')
        fields = line.split('\t')
        if len(fields) != 6:
            raise FormatError('expected 6 fields, got %d: %s' %
                              (len(fields), line))
        species, docid, start, end, text, code = fields
        try:
            start = int(start)
            end = int(end)
        except:
            raise FormatError('Failed to parse line %d: %s' % (ln, line))
        if len(text) != end-start:
            raise FormatError('Text "%s" length %d, end-start (%d-%d) is %s' %
                              (text, len(text), end, start, end-start))
        annotations.append(Annotation(docid, start, end, text, species, code))
    return annotations
        
def load_annotations(fn):
    with io.open(fn, encoding='utf-8') as f:
        return read_linnaeus_annotations(f)

def load_document(fn):
    # LINNAEUS documents basenames (without extension) are their IDs.
    docid = path.basename(path.splitext(fn)[0])
    with io.open(fn, encoding='utf-8') as f:
        text = f.read()
    return Document(docid, text)

def uniq(iterable):
    # http://stackoverflow.com/a/480227
    seen = set()
    return [i for i in iterable if not (i in seen or seen.add(i))]

def load_linnaeus(annfn, docdir):
    """Read LINNAEUS corpus data from given annotation file and directory
    containing the corpus document texts, return list of Document objects.
    """
    annotations = load_annotations(annfn)
    docids = uniq(sorted([a.docid for a in annotations]))
    doc = { d: load_document(path.join(docdir, d+'.txt')) for d in docids }
    for a in annotations:
        doc[a.docid].annotations.append(a)
    for d in doc.values():
        d.verify_annotations()
    return doc.values()
