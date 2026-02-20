package com.tabula.sovereign

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.tabula.sovereign.ui.TabulaApp
import com.tabula.sovereign.ui.theme.TabulaTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            TabulaTheme {
                TabulaApp()
            }
        }
    }
}
