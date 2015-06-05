
This repo is part of a project to use natural language processing to automatically repair transcription gaps in old books.
The python file TranscriptionRepair.py takes a folder of XML files (formatted as in the included emdabbotized folder), parses them
into plain text, builds an n-gram language model from them, and uses these n-grams to find the most likely correction (as implied by the
language model and n-gram frequencies) for any transcription gaps, indicated by the ● character. The ngram-counts function from the SRILM
toolkit is used - included here is a precompiled .exe; as of yet this hasn't been tested on machines other than Windows.

USAGE:
Run TranscriptionRepair.py, and input the name of a folder containing xml files to be processed. The simplest method is to just put files in the
Test folder in this local directory, and then at the prompt enter "Test" (quotes included).

THINGS TO WATCH OUT FOR:
- Unicode formatting: the SRILM ngram-counts script by default accepts ASCII. Included characters in the book corpi (most frequently ● and ſ)
are not part of the standard ASCII library, and instead require UTF-8 encoding. UTF-8 is meant to be backwards compatible with ASCII, but this
requires some fiddling around with the encoding in Python, and if done improperly this leads to errors.
- Memory: The language models built by SRILM ngram-counts can run into memory problems if excessively large corpi of texts are analyzed. If ngram-counts
crashes at runtime, try again with less files. The Python module is built to accept folders of files instead of individual files - with great power
comes great responsibility.

Developed by Michael Kushnir, michaelkushnir2015@u.northwestern.edu
With help from Doug Downey and Martin Mueller