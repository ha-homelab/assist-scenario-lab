# Contributing

Use Python 3.11+, install editable with `python3 -m pip install -e .`, run `python3 -m unittest discover -s tests -v` and `python3 tools/render_docs.py`. Submit a pull request; preserve synthetic labels and stable schema/exit codes.

## Translation coverage

English, Russian, German and Spanish catalogs cover CLI help, diagnostics and HTML/text labels. All four have runnable README introductions. Full technical guides and wiki reference pages are English/Russian. Machine keys and codes deliberately remain English. Add every new catalog key to all four files; tests enforce key parity. Keep examples identical across languages and disclose untranslated sections. Native-speaker review is welcome; no professional translation certification is claimed.

## Privacy and evidence

Use invented identifiers and synthetic trials in fixtures. Do not upload raw recordings, transcripts, HA snapshots, audio URLs/tokens or deployment configuration. Keep observation method and unknown results intact. A passing declared input is not hardware certification. Fixes should include a counterexample proving the previous incorrect result, not tests that simply mirror code.

## Documentation

`docs/en/guide.md` and `docs/ru/guide.md` are canonical. Their wiki copies replace image paths with public URLs. Keep both synchronized. SVGs come from `tools/render_docs.py`; edit the generator, regenerate, and review the image. MIT applies to original code, docs and diagrams.
