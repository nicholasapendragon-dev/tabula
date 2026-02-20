package com.tabula.sovereign.util

import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

object IdGenerator {
    private val formatter = DateTimeFormatter.ofPattern("yyyyMMddHHmm")

    fun newZettelId(now: LocalDateTime = LocalDateTime.now()): String = now.format(formatter)
}
