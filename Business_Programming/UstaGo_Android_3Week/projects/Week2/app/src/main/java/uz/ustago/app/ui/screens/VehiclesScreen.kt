package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel

@Composable
fun VehiclesScreen(vm: UstaGoViewModel) {
    val vehicles by vm.vehicles.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    val user by vm.currentUser.collectAsStateWithLifecycle()
    var model by rememberSaveable { mutableStateOf("") }
    var plate by rememberSaveable { mutableStateOf("") }
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 20.dp)) {
        item {
            Text(user?.fullName ?: "", style = MaterialTheme.typography.titleLarge)
            Text(user?.email ?: "")
            TextButton(enabled = !busy, onClick = vm::logout) { Text("Log out") }
            Text("Add a vehicle", style = MaterialTheme.typography.titleMedium)
        }
        item { OutlinedTextField(model, { model = it.take(60) }, label = { Text("Model, e.g. Chevrolet Cobalt") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy) }
        item { OutlinedTextField(plate, { plate = it.take(15) }, label = { Text("Plate, e.g. 01 A 123 BC") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy) }
        item { Button(enabled = !busy, onClick = { vm.addVehicle(model, plate) { model = ""; plate = "" } }) { Text("Save vehicle") } }
        if (vehicles.isEmpty()) item { Text("No vehicles yet. Add your car before booking a service.") }
        items(vehicles, key = { it.id }) { vehicle ->
            OutlinedCard(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp)) {
                    Text(vehicle.model, style = MaterialTheme.typography.titleMedium)
                    Text(vehicle.plate)
                }
            }
        }
    }
}
