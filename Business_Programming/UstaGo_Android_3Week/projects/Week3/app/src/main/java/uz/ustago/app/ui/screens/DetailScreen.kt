package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.formatSom

@Composable
fun DetailScreen(vm: UstaGoViewModel, id: Long, onBook: () -> Unit) {
    val service by remember(vm, id) { vm.service(id) }.collectAsStateWithLifecycle(initialValue = null)
    val item = service
    if (item == null) { Text("Loading service…", Modifier.padding(16.dp)); return }
    val garage by remember(vm, item.garageId) { vm.garage(item.garageId) }.collectAsStateWithLifecycle(initialValue = null)
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text(item.category, style = MaterialTheme.typography.labelLarge)
        Text(item.name, style = MaterialTheme.typography.headlineMedium)
        Text(formatSom(item.price), style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.primary)
        Text(item.description)
        HorizontalDivider()
        Text(garage?.name ?: "Loading garage…", style = MaterialTheme.typography.titleLarge)
        Text(garage?.address ?: "")
        Text(garage?.phone ?: "")
        Text("Appointment: one hour. Parts and extra repairs are excluded unless stated above.")
        Text("Demo businesses and availability. Payment is due at the garage.", style = MaterialTheme.typography.bodySmall)
        Button(onClick = onBook, enabled = garage != null, modifier = Modifier.fillMaxWidth()) { Text("Choose a time") }
    }
}
