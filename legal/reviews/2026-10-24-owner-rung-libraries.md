# Owner-name rung libraries: install audit, Oct 24, 2026

Scope: the libraries Todd approved for the free owner-name rung (coo/DECISIONS-2026-10-24.md, item 1): extruct 0.18.0, spaCy 3.8.16 with the en_core_web_sm 3.8.0 model, probablepeople 0.5.6. Done in a live chat before anything was added to the repo. Pinned in tools/requirements-owner-rung.txt (64 packages, Python 3.13, ubuntu x86_64).

## What was checked

- Origin: all 63 PyPI files match the sha256 PyPI publishes for that exact file. The model wheel matches the checksum on its GitHub release page (1932429d...fb85).
- Integrity: every installed file (8,029) checked against its package's own hash manifest. 0 mismatches.
- Install hooks: one startup file, setuptools' stock distutils shim (distutils-precedence.pth). One package builds from source (jstyleson); its setup.py is plain metadata. The runner builds it with the pinned setuptools, so no build tool is fetched unchecked.
- Full read, the three libraries and the model: all 690 code files (116,792 lines) read start to end, in eight parts. The other 202,225 lines in those packages are word lists and tables; a parser confirmed they hold only literal data and no logic.
- The 60 packages they pull in (numpy, lxml, pydantic, requests and so on): every file hash-checked and scanned for network, process, dynamic-code, deserializing and environment calls; 1,390 hits triaged, the riskiest opened in context; every module-level call listed with a parser; the small helper packages read in full. Not read line by line: the large well-known ones, and compiled parts (.so files) in any package, which were hash-checked only.

## Findings

- No telemetry, no hidden network calls, nothing obfuscated, no credential reads at import, anywhere.
- Network and process code exists only behind commands the rung never calls: spaCy's command line (download, validate, package, project), displaCy serve, `nlp.pipe` with more than one process, extruct's URL fetcher (`extruct.tool`), RDFa and microformat extraction, the test suites.
- Unpickling exists only in explicit load functions the rung never calls on outside data.

## How the rung uses them

- extruct: only `JsonLdExtractor` and `MicrodataExtractor`, on HTML strings our own code fetched.
- spaCy: `spacy.load("en_core_web_sm")` from the installed package, then `nlp.pipe(texts)` in one process.
- probablepeople: `tag()` on a short candidate name.
- Every parse runs inside `site_owners.no_network()`, which refuses any socket the parsing code opens; the selftest checks it.

## Rule for changes

A version changes only after the same read and a new hash list. The install keeps `--require-hashes`.
