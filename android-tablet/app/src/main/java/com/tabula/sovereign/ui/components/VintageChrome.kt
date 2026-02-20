package com.tabula.sovereign.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

private val TopBar = Color(0xFF6A6156)
private val Panel = Color(0xFFF3EEE2)
private val Border = Color(0xFFA49884)

@Composable
fun VintageTopBar(title: String, left: String, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(TopBar)
            .padding(horizontal = 14.dp, vertical = 10.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(left, color = Color(0xFFF0E8DA), style = MaterialTheme.typography.titleMedium)
        Text("— $title —", color = Color(0xFFF5EFE4), style = MaterialTheme.typography.titleLarge)
        Text("☰", color = Color(0xFFEADFCF), style = MaterialTheme.typography.titleLarge)
    }
}

@Composable
fun VintagePanel(title: String, modifier: Modifier = Modifier, body: @Composable () -> Unit) {
    Column(
        modifier = modifier
            .background(Panel)
            .border(1.dp, Border)
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(title, style = MaterialTheme.typography.titleMedium)
        body()
    }
}

@Composable
fun VintageAction(label: String, emphasis: Boolean = false, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        shape = RoundedCornerShape(4.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = if (emphasis) Color(0xFF6B5E4D) else Color(0xFFEDE4D3),
            contentColor = if (emphasis) Color(0xFFF7F0E4) else Color(0xFF2F2A23),
        ),
    ) {
        Text(label)
    }
}

@Composable
fun VintageContainer(modifier: Modifier = Modifier, content: @Composable () -> Unit) {
    Box(
        modifier = modifier
            .background(Color(0xFFF6F2E8))
            .border(1.dp, Border)
            .padding(10.dp),
    ) {
        content()
    }
}
