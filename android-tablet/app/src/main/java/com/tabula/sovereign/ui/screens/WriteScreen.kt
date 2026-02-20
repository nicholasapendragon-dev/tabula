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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.tabula.sovereign.ui.components.VintageAction
import com.tabula.sovereign.ui.components.VintageContainer
import com.tabula.sovereign.ui.components.VintagePanel
import com.tabula.sovereign.ui.components.VintageTopBar

@Composable
fun WriteScreen(onBack: () -> Unit) {
    val markdown = remember {
        mutableStateOf(
            "I sat alone in the study, the soft glow of the lamp casting shadows across the desk.\n\n" +
                "To write was not merely to record, but to wrestle meaning from chaos.\n\n" +
                "— Draft —",
        )
    }

    Column(modifier = Modifier.fillMaxSize()) {
        VintageTopBar(title = "Slope", left = "WriterDeck")
        Row(modifier = Modifier.fillMaxSize().padding(8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            VintagePanel(title = "Ledger", modifier = Modifier.weight(0.95f)) {
                Text("• Manuscript")
                Text("  = Chapter 12")
                Text("  = Literary Themes")
                Text("• Vault")
                Text("  □ Alchizea Notes")
                Text("  □ Finished Works")
                Text("\nSession: 1:42 elapsed")
                Text("Commitment: 13 min remaining")
            }
            VintagePanel(title = "Draft", modifier = Modifier.weight(2.6f)) {
                Text(markdown.value, modifier = Modifier.height(420.dp).verticalScroll(rememberScrollState()))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                    VintageAction("Seal & File", onClick = {})
                    VintageAction("Export", emphasis = true, onClick = onBack)
                }
                Text("Words: 752")
            }
            VintagePanel(title = "References", modifier = Modifier.weight(0.9f)) {
                Text("• Notes")
                Text("  = On Symbolism")
                Text("  = Cognitive Dissonance")
                Text("• Links")
                Text("  = Johann Huizings")
                Text("  = Rituals of Time")
            }
        }
    }
}
