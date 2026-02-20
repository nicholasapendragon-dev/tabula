package com.tabula.sovereign.domain

import com.tabula.sovereign.data.db.SourceEntity
import com.tabula.sovereign.data.model.CitationStyle
import com.tabula.sovereign.data.model.SourceScanResult

interface OcrEngine {
    suspend fun extractText(imagePath: String): String
}

class LightweightStubOcrEngine : OcrEngine {
    override suspend fun extractText(imagePath: String): String {
        return "[offline OCR placeholder] source=$imagePath"
    }
}

class CitationEngine {
    fun format(source: SourceEntity, style: CitationStyle): String {
        return when (style) {
            CitationStyle.CHICAGO -> "${source.author}. ${source.title}. ${source.publisher}."
            CitationStyle.TURABIAN -> "${source.author}. ${source.title}. (${source.publisher})."
            CitationStyle.MLA -> "${source.author}. ${source.title}. ${source.publisher}."
            CitationStyle.APA -> "${source.author} (${source.publisher}). ${source.title}."
        }
    }

    fun fromCover(scan: SourceScanResult): SourceEntity {
        return SourceEntity(
            title = scan.title,
            author = scan.author,
            publisher = scan.publisher,
            isbn = scan.isbn,
            citationRaw = "${scan.author} — ${scan.title}",
        )
    }
}
