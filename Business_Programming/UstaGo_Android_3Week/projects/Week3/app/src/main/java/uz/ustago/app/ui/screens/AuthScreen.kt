package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel

@Composable
fun AuthScreen(vm: UstaGoViewModel, register: Boolean, switch: () -> Unit) {
    var name by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    // Password is intentionally not stored in saved instance state.
    var password by remember { mutableStateOf("") }
    val busy by vm.busy.collectAsStateWithLifecycle()
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text("UstaGo", style = MaterialTheme.typography.displaySmall)
        Text("Your next car service, organised.", style = MaterialTheme.typography.titleMedium)
        Text(if (register) "Create your account" else "Welcome back", style = MaterialTheme.typography.headlineSmall)
        if (register) OutlinedTextField(name, { name = it.take(80) }, label = { Text("Full name") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy)
        OutlinedTextField(email, { email = it.take(150) }, label = { Text("Email") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email))
        OutlinedTextField(password, { password = it.take(128) }, label = { Text("Password (8+ characters)") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy,
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password))
        Button(enabled = !busy, modifier = Modifier.fillMaxWidth(), onClick = {
            if (register) vm.register(name, email, password) else vm.login(email, password)
        }) { Text(if (register) "Create account" else "Log in") }
        TextButton(enabled = !busy, onClick = switch) {
            Text(if (register) "Already registered? Log in" else "New here? Create an account")
        }
        Text("Coursework demo: accounts and bookings are stored on this phone.", style = MaterialTheme.typography.bodySmall)
    }
}
