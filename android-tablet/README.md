# Tabula Scriptorium (Android Tablet)

Offline-first Android tablet blueprint and implementation scaffold for a unified WriterDeck + ScholarDeck workflow.

## Principles implemented

- Offline-first by default (Room + local markdown files).
- Minimal Compose UI optimized for landscape tablets.
- Keyboard-first workflow with explicit shortcut maps.
- Zero cloud requirement for core writing/research loop.
- Resource-conscious defaults for older 2-4GB tablets.

## Included modules

- **WriterDeck**: distraction-free markdown editor shell, project sidebar, backlinks/outline/timer area.
- **ScholarDeck**: source capture flow shell, OCR processing boundary, auto-zettel generation lanes.
- **Library**: citation/export/backup center.

## Technical architecture

- Kotlin + Jetpack Compose UI
- Room SQLite persistence (`tabula_offline.db`)
- File markdown persistence in app files directory (`files/markdown`)
- Backup archive (`zip`) generation of DB + markdown
- Citation engine abstraction
- Local OCR interface abstraction with lightweight stub implementation

## Notes on OCR

The `LightweightStubOcrEngine` is a placeholder boundary so you can wire either:

1. ML Kit on-device text recognition, or
2. Tesseract packaged for offline use.

## Build

```bash
cd android-tablet
./gradlew assembleDebug
```

(Gradle wrapper is not committed in this scaffold; initialize wrapper in your Android environment if needed.)

## Package as a single ZIP

```bash
cd /workspace/tabula
./scripts/package_android_tablet.sh
```

Output archive:

- `dist/tabula-android-tablet.zip`
