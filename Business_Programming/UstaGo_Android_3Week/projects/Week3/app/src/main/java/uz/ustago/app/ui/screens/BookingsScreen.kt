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
import uz.ustago.app.util.*

@Composable
fun BookingsScreen(vm: UstaGoViewModel, onReceipt: (Long) -> Unit) {
    val bookings by vm.bookings.collectAsStateWithLifecycle()
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 16.dp)) {
        if (bookings.isEmpty()) item { Text("No bookings yet. Choose a service to make your first appointment.") }
        items(bookings, key = { it.id }) { booking ->
            Card(onClick = { onReceipt(booking.id) }, modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("#${booking.id} · ${booking.serviceName}", style = MaterialTheme.typography.titleMedium)
                    Text(booking.garageName)
                    Text(formatTime(booking.startsAt))
                    Text("${formatSom(booking.total)} · ${booking.status}")
                    Text("View receipt →")
                }
            }
        }
    }
}

@Composable
fun ReceiptScreen(vm: UstaGoViewModel, id: Long) {
    val booking by remember(vm, id) { vm.booking(id) }.collectAsStateWithLifecycle(initialValue = null)
    val busy by vm.busy.collectAsStateWithLifecycle()
    val now by vm.clock.collectAsStateWithLifecycle()
    var confirmCancel by rememberSaveable { mutableStateOf(false) }
    val item = booking
    if (item == null) { Text("Loading booking…", Modifier.padding(16.dp)); return }
    LazyColumn(Modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item { Text("Booking #${item.id}", style = MaterialTheme.typography.headlineMedium) }
        item { Text(item.status, color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.titleMedium) }
        item { Text(item.serviceName, style = MaterialTheme.typography.titleLarge) }
        item { Text("${item.garageName}\n${item.garageAddress}") }
        item { Text(formatTime(item.startsAt) + " · 1 hour") }
        item { Text(item.vehicleLabel) }
        item { HorizontalDivider() }
        item { Text("Total: ${formatSom(item.total)}", style = MaterialTheme.typography.titleLarge) }
        item { Text("${item.paymentMethod} · ${item.paymentStatus}") }
        item { Text("Payment is due at the garage. This demo does not process payments.") }
        if (item.note.isNotBlank()) item { Text("Note: ${item.note}") }
        if (item.status == "CONFIRMED" && item.startsAt > now) item {
            OutlinedButton(enabled = !busy, onClick = { confirmCancel = true }) { Text("Cancel booking") }
        }
    }
    if (confirmCancel) AlertDialog(onDismissRequest = { confirmCancel = false },
        title = { Text("Cancel this booking?") }, text = { Text("The appointment time will become available again.") },
        confirmButton = { TextButton(enabled = !busy, onClick = { confirmCancel = false; vm.cancel(id) }) { Text("Cancel booking") } },
        dismissButton = { TextButton(onClick = { confirmCancel = false }) { Text("Keep booking") } })
}
