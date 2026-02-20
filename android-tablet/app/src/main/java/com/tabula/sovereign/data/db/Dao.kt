package com.tabula.sovereign.data.db

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface TabulaDao {
    @Query("SELECT * FROM projects WHERE archived = 0 ORDER BY createdAt DESC")
    fun observeActiveProjects(): Flow<List<ProjectEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertProject(project: ProjectEntity): Long

    @Query("UPDATE projects SET archived = 1 WHERE id = :projectId")
    suspend fun archiveProject(projectId: Long)

    @Query("SELECT * FROM zettels WHERE projectId = :projectId ORDER BY updatedAt DESC")
    fun observeProjectZettels(projectId: Long): Flow<List<ZettelEntity>>

    @Query("SELECT * FROM zettels ORDER BY updatedAt DESC")
    fun observeAllZettels(): Flow<List<ZettelEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertZettel(zettel: ZettelEntity)

    @Query("SELECT * FROM zettels WHERE markdown LIKE '%' || :query || '%' OR title LIKE '%' || :query || '%'")
    suspend fun globalSearch(query: String): List<ZettelEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertSource(source: SourceEntity): Long

    @Query("SELECT * FROM sources ORDER BY id DESC")
    fun observeSources(): Flow<List<SourceEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun linkZettels(link: ZettelLinkEntity)

    @Query("SELECT fromId FROM zettel_links WHERE toId = :zettelId")
    suspend fun backlinksFor(zettelId: String): List<String>
}
