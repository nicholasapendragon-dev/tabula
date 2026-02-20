package com.tabula.sovereign.data.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverter
import androidx.room.TypeConverters
import com.tabula.sovereign.data.model.ZettelType

@Database(
    entities = [ProjectEntity::class, ZettelEntity::class, SourceEntity::class, ZettelLinkEntity::class],
    version = 1,
    exportSchema = false,
)
@TypeConverters(TabulaConverters::class)
abstract class TabulaDatabase : RoomDatabase() {
    abstract fun dao(): TabulaDao

    companion object {
        @Volatile
        private var INSTANCE: TabulaDatabase? = null

        fun get(context: Context): TabulaDatabase = INSTANCE ?: synchronized(this) {
            INSTANCE ?: Room.databaseBuilder(
                context,
                TabulaDatabase::class.java,
                "tabula_offline.db",
            ).fallbackToDestructiveMigration().build().also { INSTANCE = it }
        }
    }
}

class TabulaConverters {
    @TypeConverter
    fun toZettelType(value: String): ZettelType = ZettelType.valueOf(value)

    @TypeConverter
    fun fromZettelType(value: ZettelType): String = value.name
}
