# Maintaining guide translations

The full guide is available in the 24 languages from
[`languages.json`](languages.json), following the
[ha-homelab documentation catalog](https://github.com/ha-homelab/.github/blob/main/languages.json).
CLI and README language coverage remains English, Russian, German and Spanish.

Edit `docs/en/guide.md` and update the complete guide in every `docs/<language>/guide.md`.
Keep instructions, limitations, evidence interpretation and troubleshooting in
parity, including the difference between protocol completion and audible sound.
Commands, inline identifiers and external references remain exact. Each page's
navigation links to every language of the same guide.

Arabic, Persian and Hebrew prose uses explicit right-to-left containers. Code
blocks and language navigation stay left-to-right. Leave a blank line after HTML
containers so GitHub renders the enclosed Markdown.

After translation review, update the English digest in
[`translations.json`](translations.json). It is SHA-256 of the UTF-8 source with
the language-navigation block and its adjacent newlines replaced by one blank
line, then surrounding whitespace stripped. All other whitespace, including
blank lines inside executable examples, remains significant. A changed English source therefore
cannot silently leave the translation set stale.

The checked-in wiki guides are generated mirrors, not separately maintained
translations. Run `python3 tools/sync_wiki_guides.py` after editing guides. The
script changes only language-navigation targets and the architecture image URL
for the wiki location. Run `python3 tools/sync_wiki_guides.py --check` to detect
stale mirrors without writing files. Publishing these pages to GitHub's separate
wiki remains a separate operation.

Stage new files and run `python3 tools/check_docs.py`. The existing CI checks all
24 pages, source digest, complete navigation and direction, fenced code, inline
literals, headings and list structure, links, wiki parity and SVG XML. Structural
checks do not prove linguistic accuracy; request review and preview representative
GitHub pages, including a right-to-left page with a code block.
