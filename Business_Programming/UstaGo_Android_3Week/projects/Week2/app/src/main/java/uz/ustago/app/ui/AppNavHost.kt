package uz.ustago.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavType
import androidx.navigation.compose.*
import androidx.navigation.navArgument
import uz.ustago.app.ui.screens.*

@Composable
fun AppRoot(vm: UstaGoViewModel) {
    val ready by vm.ready.collectAsStateWithLifecycle()
    val user by vm.currentUser.collectAsStateWithLifecycle()
    val message by vm.message.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    if (!ready) {
        Scaffold { padding ->
            Column(Modifier.padding(padding).padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("Preparing UstaGo…", style = MaterialTheme.typography.headlineSmall)
                if (busy) CircularProgressIndicator()
                message?.let { Text(it, color = MaterialTheme.colorScheme.error) }
                if (!busy) Button(onClick = { vm.retryStartup() }) { Text("Retry") }
            }
        }
        return
    }
    // A different account receives a new navigation tree, including saved form state.
    key(user?.id) {
        if (user == null) AuthNavigation(vm) else MainNavigation(vm)
    }
}

@Composable
private fun StatusMessage(vm: UstaGoViewModel) {
    val message by vm.message.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
    message?.let { text ->
        Surface(color = MaterialTheme.colorScheme.secondaryContainer) {
            Row(Modifier.fillMaxWidth().padding(start = 16.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(text, Modifier.weight(1f).padding(vertical = 12.dp))
                TextButton(onClick = vm::dismiss) { Text("Dismiss") }
            }
        }
    }
}

@Composable
private fun AuthNavigation(vm: UstaGoViewModel) {
    val nav = rememberNavController()
    Scaffold { padding ->
        Column(Modifier.padding(padding).imePadding()) {
            StatusMessage(vm)
            NavHost(nav, startDestination = "login", modifier = Modifier.weight(1f)) {
                composable("login") { AuthScreen(vm, false) { vm.dismiss(); nav.navigate("register") } }
                composable("register") { AuthScreen(vm, true) { vm.dismiss(); nav.popBackStack() } }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MainNavigation(vm: UstaGoViewModel) {
    val nav = rememberNavController()
    val entry by nav.currentBackStackEntryAsState()
    val route = entry?.destination?.route ?: "home"
    val busy by vm.busy.collectAsStateWithLifecycle()
    val rootRoutes = listOf("home", "bookings", "vehicles")
    val title = when (route) {
        "home" -> "UstaGo · Car services"
        "bookings" -> "My bookings"
        "vehicles" -> "My vehicles"
        "detail/{id}" -> "Service details"
        "book/{id}" -> "Choose your appointment"
        else -> "Booking receipt"
    }
    Scaffold(
        topBar = { TopAppBar(title = { Text(title) }, navigationIcon = {
            if (route !in rootRoutes) TextButton(enabled = !busy, onClick = { nav.popBackStack() }) { Text("Back") }
        }) },
        bottomBar = {
            NavigationBar {
                rootRoutes.zip(listOf("Services", "Bookings", "Vehicles")).forEach { (destination, label) ->
                    NavigationBarItem(selected = route == destination, enabled = !busy,
                        onClick = {
                            vm.dismiss()
                            nav.navigate(destination) { popUpTo("home"); launchSingleTop = true }
                        }, icon = { Text(label.take(1)) }, label = { Text(label) })
                }
            }
        }
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding).imePadding()) {
            StatusMessage(vm)
            NavHost(nav, startDestination = "home", modifier = Modifier.weight(1f)) {
                composable("home") { HomeScreen(vm) { nav.navigate("detail/$it") } }
                composable("detail/{id}", arguments = listOf(navArgument("id") { type = NavType.LongType })) { back ->
                    val id = back.arguments!!.getLong("id")
                    DetailScreen(vm, id) { nav.navigate("book/$id") }
                }
                composable("book/{id}", arguments = listOf(navArgument("id") { type = NavType.LongType })) { back ->
                    BookScreen(vm, back.arguments!!.getLong("id"),
                        onVehicles = { nav.navigate("vehicles") },
                        onBooked = { id -> nav.navigate("receipt/$id") { popUpTo("home") } })
                }
                composable("vehicles") { VehiclesScreen(vm) }
                composable("bookings") { BookingsScreen(vm) { nav.navigate("receipt/$it") } }
                composable("receipt/{id}", arguments = listOf(navArgument("id") { type = NavType.LongType })) { back ->
                    ReceiptScreen(vm, back.arguments!!.getLong("id"))
                }
            }
        }
    }
}
