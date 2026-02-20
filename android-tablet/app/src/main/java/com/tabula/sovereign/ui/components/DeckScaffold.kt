package com.tabula.sovereign.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun ThreePaneDeck(
    leftTitle: String,
    centerTitle: String,
    rightTitle: String,
    leftBody: @Composable () -> Unit,
    centerBody: @Composable () -> Unit,
    rightBody: @Composable () -> Unit,
) {
    Row(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Column(
            modifier = Modifier.fillMaxHeight().weight(1f).padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(leftTitle, style = MaterialTheme.typography.titleMedium)
            leftBody()
        }
        Column(
            modifier = Modifier.fillMaxHeight().weight(2.5f).padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(centerTitle, style = MaterialTheme.typography.titleMedium)
            centerBody()
        }
        Column(
            modifier = Modifier.fillMaxHeight().weight(1f).padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(rightTitle, style = MaterialTheme.typography.titleMedium)
            rightBody()
        }
    }
}

@Composable
fun SectionTitle(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleSmall,
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
    )
}
