package com.tabula.sovereign.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tabula.sovereign.ui.components.VintageAction
import com.tabula.sovereign.ui.components.VintagePanel
import com.tabula.sovereign.ui.components.VintageTopBar

@Composable
fun StudyScreen(onBack: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize()) {
        VintageTopBar(title = "ScholarDeck", left = "ScholarDeck")
        Row(modifier = Modifier.fillMaxSize().padding(8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            VintagePanel(title = "Sources", modifier = Modifier.weight(0.95f)) {
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    VintageAction("+ Add Source", onClick = {})
                    VintageAction("Scan New Page", onClick = {})
                }
                Text("• Confessions")
                Text("  + Augustine, 397")
                Text("• Thomas Theologica")
                Text("• Democracy in America")
                Text("\nLibrary")
                Text("= All Sources")
                Text("= Citation Styles")
                Text("\nStats")
                Text("Zettels today: 12")
            }
            VintagePanel(title = "Confessions (p.114)", modifier = Modifier.weight(2.3f)) {
                Text(
                    "You have made us for yourself, O Lord, and our heart is restless until it rests in You.\n\n" +
                        "Grant me, O Lord, to know which is the more first: to call upon You or to praise You?\n\n" +
                        "— feceriusti nos ad te et inquietum est cor nostrum donec requiescat in te.",
                    modifier = Modifier.height(430.dp).verticalScroll(rememberScrollState()),
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                    VintageAction("Create Quote", onClick = {})
                    VintageAction("Create Summary", onClick = {})
                    VintageAction("Create Question", onClick = {})
                    VintageAction("Edit", onClick = {})
                }
            }
            VintagePanel(title = "Generated Zettel", modifier = Modifier.weight(1f)) {
                Text("ZID: 2026-02-19-1453")
                Text("Source: Augustine, Confessions, p.114")
                Text("Tags: theology, memory, anthropology")
                Text("\nYou have made us for yourself...\n\n— Augustine, Confessions")
                Text("\nCommentary: core line on anthropological longing.")
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    VintageAction("File Zettel", emphasis = true, onClick = {})
                    VintageAction("Discard", onClick = onBack)
                }
            }
        }
    }
}
