package uz.ustago.app.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.data.CarService
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.*
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun BookScreen(vm: UstaGoViewModel, id: Long, onVehicles: () -> Unit, onBooked: (Long) -> Unit) {
    val service by remember(vm, id) { vm.service(id) }.collectAsStateWithLifecycle(initialValue = null)
    val item = service
    if (item == null) { Text("Loading service…", Modifier.padding(16.dp)); return }
    BookingForm(vm, item, onVehicles, onBooked)
}

@Composable
private fun BookingForm(vm: UstaGoViewModel, service: CarService, onVehicles: () -> Unit, onBooked: (Long) -> Unit) {
    val slots by remember(vm, service.garageId) { vm.slots(service.garageId) }
        .collectAsStateWithLifecycle(initialValue = emptyList())
    val vehicles by vm.vehicles.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    var day by rememberSaveable(service.id) { mutableStateOf("") }
    var slotId by rememberSaveable(service.id) { mutableLongStateOf(0) }
    var vehicleId by rememberSaveable(service.id) { mutableLongStateOf(0) }
    var payment by rememberSaveable(service.id) { mutableStateOf("Cash") }
    var note by rememberSaveable(service.id) { mutableStateOf("") }
    var confirm by rememberSaveable { mutableStateOf(false) }
    val groups = slots.groupBy { SimpleDateFormat("EEE dd MMM yyyy", Locale.ENGLISH).format(Date(it.startsAt)) }
    val selectedDay = day.takeIf { it in groups } ?: groups.keys.firstOrNull()
    val selectedSlot = slots.firstOrNull { it.id == slotId }
    val selectedVehicle = vehicles.firstOrNull { it.id == vehicleId }
    val canBook = selectedSlot != null && selectedVehicle != null && !busy
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 20.dp)) {
        item {
            Text(service.name, style = MaterialTheme.typography.headlineSmall)
            Text(formatSom(service.price), style = MaterialTheme.typography.titleLarge)
            Text("1. Select a date", style = MaterialTheme.typography.titleMedium)
        }
        item {
            if (groups.isEmpty()) Text("No available times. Return to Services and choose another service.")
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                groups.keys.forEach { value ->
                    FilterChip(selectedDay == value, { day = value; slotId = 0 }, label = { Text(value) }, enabled = !busy)
                }
            }
        }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                groups[selectedDay].orEmpty().forEach { slot ->
                    FilterChip(slotId == slot.id, { slotId = slot.id }, label = {
                        Text(SimpleDateFormat("HH:mm", Locale.ENGLISH).format(Date(slot.startsAt)))
                    }, enabled = !busy)
                }
            }
        }
        item {
            Text("2. Select your vehicle", style = MaterialTheme.typography.titleMedium)
            if (vehicles.isEmpty()) Text("Add a vehicle first, then return here and select it.")
            vehicles.forEach { vehicle ->
                Row {
                    RadioButton(vehicleId == vehicle.id, { vehicleId = vehicle.id }, enabled = !busy)
                    Text("${vehicle.model} · ${vehicle.plate}", Modifier.padding(top = 12.dp))
                }
            }
            TextButton(enabled = !busy, onClick = onVehicles) { Text("Manage vehicles") }
        }
        item {
            Text("3. Payment at the garage", style = MaterialTheme.typography.titleMedium)
            listOf("Cash", "Card at garage").forEach { value ->
                Row {
                    RadioButton(payment == value, { payment = value }, enabled = !busy)
                    Text(value, Modifier.padding(top = 12.dp))
                }
            }
            Text("No money is charged in this app.", style = MaterialTheme.typography.bodySmall)
        }
        item { OutlinedTextField(note, { note = it.take(300) }, label = { Text("Optional note (max 300 characters)") },
            modifier = Modifier.fillMaxWidth(), enabled = !busy, minLines = 2) }
        item {
            selectedSlot?.let { Text("Appointment: ${formatTime(it.startsAt)}") }
            Text("Total: ${formatSom(service.price)}", style = MaterialTheme.typography.titleLarge)
            Button(enabled = canBook, onClick = { confirm = true }, modifier = Modifier.fillMaxWidth()) { Text("Review booking") }
        }
    }
    if (confirm) AlertDialog(onDismissRequest = { if (!busy) confirm = false },
        title = { Text("Confirm your appointment") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(service.name)
                Text(selectedSlot?.let { formatTime(it.startsAt) } ?: "Time no longer available. Please choose again.")
                Text(selectedVehicle?.let { "${it.model} · ${it.plate}" } ?: "Select a vehicle.")
                Text("${formatSom(service.price)} · $payment · unpaid")
            }
        },
        confirmButton = { TextButton(enabled = canBook, onClick = {
            vm.place(service.id, slotId, vehicleId, payment, note) { id -> confirm = false; onBooked(id) }
        }) { Text("Confirm booking") } },
        dismissButton = { TextButton(enabled = !busy, onClick = { confirm = false }) { Text("Edit") } })
}
