# Release notes

Turn the newest released changelog version into notes a reader with no technical background understands and cares about. The changelog stays technical; the notes translate it.

## Discover the convention first

Find how this repository publishes notes before writing: a `RELEASE_NOTES.md`, a `docs/releases/` folder, GitHub or GitLab releases, or nothing yet. Read one existing entry and follow its structure. With no established destination, ask the user where the notes go and do not invent one.

## Dated release-notes feed (RELEASE_NOTES.md)

Use this format when the destination is a `RELEASE_NOTES.md` that holds dated sections. The app's parser rejects any other shape, so follow it exactly.

- Section heading: `## YYYY-MM-DD`, the date the version was released (the release tag's date). Never put a version number in the heading.
- First non-empty line under the heading: `Requires: launcher >=X.Y.Z, runtime >=A.B.C`. Use three-part versions, name each component at most once, and separate them with a comma and a space. Name the minimum launcher and runtime versions the entry covers. One component may be left out, but at least one must be named.
- Then the notes: a short opening prose paragraph, then `- ` bullets for changes that matter to users. Separate blocks with a blank line.
- No Markdown headings inside a section. A line starting with `#` is read as plain text. Group labels are plain lines such as `What is new:`, as in the existing entries.
- Newest section first. Dates never increase down the file; several sections may share a date.
- Add new entries at the top. Never remove or edit an older entry on the same date, because entry ids are counted from the bottom of the file and removing one renumbers the entries above it.

Example (invented content):

```markdown
## 2031-06-02
Requires: launcher >=2.7.1

Your zibble lists now sort by the time each zibble was added, so the newest one sits at the top.

- Flonker exports keep their column headings when you open them in a spreadsheet.
- The zibble sorter no longer stops when a list has a blank row.
```

## Source of truth

Work only from the changelog section for the version being released. Every claim in the notes traces to a line in it. No invented features, no numbers the changelog does not contain, no promises about the future.

## Voice

Write to "you". Warm, plain words, no hype, no superlatives, no jargon. Say what the reader can now do, not what the code does. A sentence the reader cannot act on or picture does not belong.

## Shape

Open with two or three sentences of prose carrying the release's point. Group the rest under plain labels the reader recognizes (what is new, what changed, what got fixed), each followed by its bullets. End with a "Good to know" label for behavior changes, requirements and caveats the reader must act on. In a dated feed, use these labels as plain lines, not Markdown headings.

## Translate

Each technical change becomes the reader's outcome. Use the project's own words for features. When a term cannot be avoided, give it one plain sentence of meaning in place, the first time it appears. Check that every sentence traces to a changelog line and that each term has its one-sentence meaning where it first appears.
