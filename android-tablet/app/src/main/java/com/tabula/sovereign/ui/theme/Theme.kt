package com.tabula.sovereign.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.sp

private val SepiaLight = lightColorScheme(
    background = Color(0xFFF1ECE3),
    surface = Color(0xFFF6F1E7),
    primary = Color(0xFF6B5E4E),
    onPrimary = Color(0xFFF6EEE0),
    onSurface = Color(0xFF2C2720),
)

private val InkDark = darkColorScheme(
    background = Color(0xFF121212),
    surface = Color(0xFF1A1A1A),
    onSurface = Color(0xFFD9D9D9),
)

private val ScriptoriumTypography = Typography(
    headlineLarge = TextStyle(fontFamily = FontFamily.Serif, fontSize = 42.sp),
    headlineMedium = TextStyle(fontFamily = FontFamily.Serif, fontSize = 34.sp),
    headlineSmall = TextStyle(fontFamily = FontFamily.Serif, fontSize = 24.sp),
    titleLarge = TextStyle(fontFamily = FontFamily.Serif, fontSize = 28.sp),
    titleMedium = TextStyle(fontFamily = FontFamily.Serif, fontSize = 22.sp),
    bodyLarge = TextStyle(fontFamily = FontFamily.Serif, fontSize = 19.sp),
    bodyMedium = TextStyle(fontFamily = FontFamily.Serif, fontSize = 17.sp),
)

@Composable
fun TabulaTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) InkDark else SepiaLight,
        typography = ScriptoriumTypography,
        content = content,
    )
}
