package uz.ustago.app.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.formatSom

@Composable
fun HomeScreen(vm: UstaGoViewModel, onDetail: (Long) -> Unit) {
    val services by vm.services.collectAsStateWithLifecycle()
    val categories by vm.categories.collectAsStateWithLifecycle()
    val query by vm.query.collectAsStateWithLifecycle()
    val category by vm.category.collectAsStateWithLifecycle()
    Column(Modifier.fillMaxSize().padding(horizontal = 16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedTextField(query, { vm.query.value = it }, label = { Text("Search car services") },
            modifier = Modifier.fillMaxWidth(), singleLine = true)
        Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            (listOf("All") + categories).forEach { value ->
                FilterChip(category == value, { vm.category.value = value }, label = { Text(value) })
            }
        }
        Text("${services.size} services · prices in UZS", style = MaterialTheme.typography.labelLarge)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 16.dp)) {
            if (services.isEmpty()) item { Text("No matching services. Try another search or category.") }
            items(services, key = { it.id }) { service ->
                Card(onClick = { onDetail(service.id) }, modifier = Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(service.category, style = MaterialTheme.typography.labelMedium)
                        Text(service.name, style = MaterialTheme.typography.titleLarge)
                        Text(service.description, maxLines = 2)
                        Text(formatSom(service.price), style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.primary)
                        Text("View garage and available times →")
                    }
                }
            }
        }
    }
}
