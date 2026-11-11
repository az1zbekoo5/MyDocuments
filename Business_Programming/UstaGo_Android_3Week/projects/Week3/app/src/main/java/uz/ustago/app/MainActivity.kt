package uz.ustago.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.viewmodel.compose.viewModel
import uz.ustago.app.ui.AppRoot
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.ui.theme.UstaGoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val repo = (application as UstaGoApp).repository
        setContent {
            UstaGoTheme {
                val vm: UstaGoViewModel = viewModel(factory = UstaGoViewModel.Factory(repo))
                AppRoot(vm)
            }
        }
    }
}
