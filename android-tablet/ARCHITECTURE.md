# Architecture Map: WriterDeck + ScholarDeck

## 1. Unified storage

1. Room database for relational state:
   - projects
   - zettels
   - sources
   - zettel_links
2. Markdown file mirror for durability and external export friendliness.
3. Backup service creates compressed archives with both DB and markdown tree.

## 2. Module boundaries

### WriterDeck

- `WriteScreen` is a three-pane landscape layout:
  - left: projects, notes, tags
  - center: markdown composition area
  - right: backlinks, outline, timer, shortcut hints
- Typewriter/focus/distraction features represented in settings/domain model.

### ScholarDeck

- OCR pipeline boundary: `OcrEngine`
- Citation formatting boundary: `CitationEngine`
- Scan flow expected:
  1. capture source cover/page
  2. run OCR locally
  3. allow correction
  4. generate quote/summary/question zettels
  5. write zettels to shared repository, immediately visible in WriterDeck

### Library

- Bibliography control point.
- Export and backup actions.

## 3. Performance posture (old tablet safe defaults)

- No heavy animations.
- Lightweight compose screens.
- Minimal dependencies.
- Database indexes on hot foreign key fields.
- No network calls in core loop.

## 4. Security posture

- Local-only data model.
- Optional encrypted DB can be layered by replacing Room open helper.
- Optional passcode lock can be layered in `MainActivity` gate.

## 5. Next implementation steps

1. Add real OCR adapter (ML Kit or Tesseract).
2. Add WorkManager daily auto-backup.
3. Add export pipeline (md/pdf/docx/txt).
4. Add drag-and-drop outline ordering + backlinks graph.
5. Add full keyboard event routing and command dispatcher.
