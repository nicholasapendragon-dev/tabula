package com.tabula.sovereign.data.db

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import com.tabula.sovereign.data.model.ZettelType

@Entity(tableName = "projects")
data class ProjectEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val name: String,
    val archived: Boolean = false,
    val createdAt: Long = System.currentTimeMillis(),
)

@Entity(
    tableName = "zettels",
    foreignKeys = [
        ForeignKey(
            entity = ProjectEntity::class,
            parentColumns = ["id"],
            childColumns = ["projectId"],
            onDelete = ForeignKey.CASCADE,
        ),
    ],
    indices = [Index("projectId")],
)
data class ZettelEntity(
    @PrimaryKey val id: String,
    val projectId: Long,
    val title: String,
    val markdown: String,
    val tagsCsv: String = "",
    val zettelType: ZettelType = ZettelType.NOTE,
    val sourceId: Long? = null,
    val pageNumber: Int? = null,
    val updatedAt: Long = System.currentTimeMillis(),
)

@Entity(tableName = "sources")
data class SourceEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val author: String,
    val publisher: String,
    val isbn: String,
    val citationRaw: String,
)

@Entity(
    tableName = "zettel_links",
    primaryKeys = ["fromId", "toId"],
)
data class ZettelLinkEntity(
    val fromId: String,
    val toId: String,
)
