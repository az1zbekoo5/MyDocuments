package uz.ustago.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.CancellationException
import uz.ustago.app.data.SampleData
import uz.ustago.app.ui.theme.UstaGoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val db = (application as UstaGoApp).database
        setContent {
            UstaGoTheme {
                val status by produceState("Preparing database…") {
                    value = try {
                        SampleData.seed(db)
                        "Database ready · ${db.catalogue().serviceCount()} services"
                    } catch (e: CancellationException) { throw e }
                    catch (e: Exception) { "Database error: ${e.message}" }
                }
                Scaffold { padding ->
                    Column(Modifier.fillMaxSize().padding(padding).padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        Text("UstaGo", style = MaterialTheme.typography.headlineLarge)
                        Text("Week 1 · Project and Room database")
                        Text(status)
                        Text("6 tables · 3 garages · 12 services")
                        Text("Week 2 adds login, vehicles, service search and appointment booking.")
                    }
                }
            }
        }
    }
}
