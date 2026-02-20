package com.tabula.sovereign.util

import com.tabula.sovereign.data.model.Shortcut

object Shortcuts {
    val global = listOf(
        Shortcut("Ctrl+N", "New Note"),
        Shortcut("Ctrl+Shift+N", "New Project"),
        Shortcut("Ctrl+S", "Save"),
        Shortcut("Ctrl+F", "Search"),
        Shortcut("Ctrl+Shift+F", "Global Search"),
        Shortcut("Ctrl+P", "Export"),
    )

    val writing = listOf(
        Shortcut("Ctrl+B", "Bold"),
        Shortcut("Ctrl+I", "Italic"),
        Shortcut("Ctrl+H", "Heading"),
        Shortcut("Ctrl+L", "Link note"),
        Shortcut("Ctrl+Shift+L", "View backlinks"),
        Shortcut("Ctrl+T", "Toggle typewriter mode"),
        Shortcut("Ctrl+Shift+D", "Distraction mode"),
        Shortcut("Ctrl+Shift+R", "Start/Stop timer"),
    )

    val scholar = listOf(
        Shortcut("Ctrl+Shift+C", "Scan cover"),
        Shortcut("Ctrl+Shift+P", "Scan page"),
        Shortcut("Ctrl+Enter", "Process OCR"),
        Shortcut("Alt+Q", "Create quote zettel"),
        Shortcut("Alt+S", "Create summary zettel"),
        Shortcut("Alt+T", "Add tags"),
    )
}
