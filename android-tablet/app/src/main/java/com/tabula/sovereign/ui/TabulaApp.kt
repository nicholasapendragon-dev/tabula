package com.tabula.sovereign.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.tabula.sovereign.data.model.DeckScreen
import com.tabula.sovereign.ui.components.VintageAction
import com.tabula.sovereign.ui.components.VintageContainer
import com.tabula.sovereign.ui.screens.LibraryScreen
import com.tabula.sovereign.ui.screens.StudyScreen
import com.tabula.sovereign.ui.screens.WriteScreen

@Composable
fun TabulaApp() {
    val screen = remember { mutableStateOf(DeckScreen.DASHBOARD) }
    when (screen.value) {
        DeckScreen.DASHBOARD -> Dashboard(
            onWrite = { screen.value = DeckScreen.WRITE },
            onStudy = { screen.value = DeckScreen.STUDY },
            onLibrary = { screen.value = DeckScreen.LIBRARY },
        )

        DeckScreen.WRITE -> WriteScreen(onBack = { screen.value = DeckScreen.DASHBOARD })
        DeckScreen.STUDY -> StudyScreen(onBack = { screen.value = DeckScreen.DASHBOARD })
        DeckScreen.LIBRARY -> LibraryScreen(onBack = { screen.value = DeckScreen.DASHBOARD })
    }
}

@Composable
private fun Dashboard(onWrite: () -> Unit, onStudy: () -> Unit, onLibrary: () -> Unit) {
    VintageContainer(modifier = Modifier.fillMaxSize().padding(18.dp)) {
        Column(
            modifier = Modifier.fillMaxSize().padding(18.dp),
            verticalArrangement = Arrangement.SpaceBetween,
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                Text("— WriterDeck ✒ —", style = MaterialTheme.typography.headlineMedium)
                Text("Select Your Threshold", style = MaterialTheme.typography.titleMedium)
                Text("Begin the Work", style = MaterialTheme.typography.headlineLarge)
                Text("How will you approach the page today?", style = MaterialTheme.typography.bodyLarge)
            }

            Row(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxWidth()) {
                ThresholdCard("Flow", "Write freely,\nfind your rhythm.", Modifier.weight(1f), onWrite)
                ThresholdCard("Workshop", "Refine drafts,\nreorganize, cut.", Modifier.weight(1f), onWrite)
                ThresholdCard("Peruse", "Read over pages,\ngather materials.", Modifier.weight(1f), onStudy)
                ThresholdCard("Hardware / Network", "Manage tools,\norganize files.", Modifier.weight(1f), onLibrary)
            }

            Row(
                modifier = Modifier.fillMaxWidth().border(1.dp, Color(0xFFC7BDAA)).padding(8.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("Progress: Chapter 5 · Manuscript in Progress")
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    VintageAction("Seal & File", onClick = onWrite)
                    VintageAction("Export", emphasis = true, onClick = onLibrary)
                }
            }
        }
    }
}

@Composable
private fun ThresholdCard(title: String, subtitle: String, modifier: Modifier, onClick: () -> Unit) {
    Column(
        modifier = modifier
            .background(Color(0xFFF2EBDE), RoundedCornerShape(8.dp))
            .border(1.dp, Color(0xFFCEC3B1), RoundedCornerShape(8.dp))
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(title, style = MaterialTheme.typography.headlineSmall)
        Text(subtitle, style = MaterialTheme.typography.bodyLarge)
        VintageAction("Open", onClick = onClick)
    }
}
