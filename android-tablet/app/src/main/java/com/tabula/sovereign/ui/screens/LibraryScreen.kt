package com.tabula.sovereign.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tabula.sovereign.ui.components.VintageAction
import com.tabula.sovereign.ui.components.VintagePanel
import com.tabula.sovereign.ui.components.VintageTopBar
import com.tabula.sovereign.util.Shortcuts

@Composable
fun LibraryScreen(onBack: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize()) {
        VintageTopBar(title = "Library", left = "WriterDeck")
        Row(modifier = Modifier.fillMaxSize().padding(8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            VintagePanel("Catalog", modifier = Modifier.weight(1f)) {
                Text("All Sources")
                Text("Citation Styles")
                Text("Backups")
                Text("Restore Archive")
            }
            VintagePanel("Operations", modifier = Modifier.weight(2f)) {
                Text("Offline bibliography and manuscript export center.")
                Text("Supports Markdown, PDF, DOCX, and Plain Text export pipeline.")
                Text("Daily backup target: /storage/emulated/0/TabulaBackups")
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                    VintageAction("Backup Now", emphasis = true, onClick = {})
                    VintageAction("Return", onClick = onBack)
                }
            }
            VintagePanel("Keyboard", modifier = Modifier.weight(1f)) {
                Shortcuts.global.forEach { Text("${it.combo} → ${it.action}") }
            }
        }
    }
}
