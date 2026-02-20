package com.tabula.sovereign.data.repo

import android.content.Context
import com.tabula.sovereign.data.db.ProjectEntity
import com.tabula.sovereign.data.db.SourceEntity
import com.tabula.sovereign.data.db.TabulaDao
import com.tabula.sovereign.data.db.ZettelEntity
import com.tabula.sovereign.data.model.ZettelType
import com.tabula.sovereign.util.IdGenerator
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class OfflineRepository(
    private val context: Context,
    private val dao: TabulaDao,
) {
    val projects: Flow<List<ProjectEntity>> = dao.observeActiveProjects()
    val sources: Flow<List<SourceEntity>> = dao.observeSources()

    suspend fun createProject(name: String): Long = dao.upsertProject(ProjectEntity(name = name))

    suspend fun createZettel(projectId: Long, title: String, content: String, type: ZettelType = ZettelType.NOTE): String {
        val id = IdGenerator.newZettelId()
        dao.upsertZettel(
            ZettelEntity(
                id = id,
                projectId = projectId,
                title = title,
                markdown = content,
                zettelType = type,
            ),
        )
        persistMarkdown(projectId, id, content)
        return id
    }

    suspend fun upsertSource(source: SourceEntity): Long = dao.upsertSource(source)

    fun zettels(projectId: Long): Flow<List<ZettelEntity>> = dao.observeProjectZettels(projectId)

    suspend fun globalSearch(query: String): List<ZettelEntity> = dao.globalSearch(query)

    suspend fun backupNow(targetFolderName: String = "tabula_backups"): File = withContext(Dispatchers.IO) {
        val backupRoot = File(context.filesDir, targetFolderName).apply { mkdirs() }
        val archive = File(backupRoot, "tabula-${System.currentTimeMillis()}.zip")
        ZipOutputStream(archive.outputStream().buffered()).use { zip ->
            val markdownDir = File(context.filesDir, "markdown")
            markdownDir.walkTopDown().filter { it.isFile }.forEach { file ->
                val relative = markdownDir.toPath().relativize(file.toPath()).toString()
                zip.putNextEntry(ZipEntry("markdown/$relative"))
                file.inputStream().copyTo(zip)
                zip.closeEntry()
            }
            val dbFile = context.getDatabasePath("tabula_offline.db")
            if (dbFile.exists()) {
                zip.putNextEntry(ZipEntry("db/tabula_offline.db"))
                dbFile.inputStream().copyTo(zip)
                zip.closeEntry()
            }
        }
        archive
    }

    private suspend fun persistMarkdown(projectId: Long, zettelId: String, markdown: String) = withContext(Dispatchers.IO) {
        val folder = File(context.filesDir, "markdown/project_$projectId").apply { mkdirs() }
        File(folder, "$zettelId.md").writeText(markdown)
    }
}
