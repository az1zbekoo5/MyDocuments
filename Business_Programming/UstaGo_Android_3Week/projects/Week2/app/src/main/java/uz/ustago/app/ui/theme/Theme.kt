package uz.ustago.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val Light = lightColorScheme(primary = Color(0xFF00796B),
    secondary = Color(0xFF8B5000), primaryContainer = Color(0xFFA5F2E0))
private val Dark = darkColorScheme(primary = Color(0xFF77D8C5),
    secondary = Color(0xFFFFB74D), primaryContainer = Color(0xFF005044))
@Composable
fun UstaGoTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = if (isSystemInDarkTheme()) Dark else Light, content = content)
}
