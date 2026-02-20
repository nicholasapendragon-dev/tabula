package com.tabula.sovereign.data.model

import java.time.Instant

enum class DeckScreen { DASHBOARD, WRITE, STUDY, LIBRARY }
enum class CitationStyle { CHICAGO, TURABIAN, MLA, APA }
enum class ZettelType { QUOTE, SUMMARY, QUESTION, NOTE }

data class Shortcut(val combo: String, val action: String)

data class FocusSettings(
    val typewriterMode: Boolean = true,
    val distractionFree: Boolean = true,
    val focusParagraphFade: Boolean = true,
    val timerMinutes: Int = 25,
)

data class SourceScanResult(
    val title: String,
    val author: String,
    val publisher: String,
    val isbn: String,
    val extractedAt: Instant = Instant.now(),
)
