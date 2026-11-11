package uz.ustago.app

import android.app.Application
import uz.ustago.app.data.AppDatabase
import uz.ustago.app.data.UstaGoRepository

class UstaGoApp : Application() {
    val database by lazy { AppDatabase.get(this) }
    val repository by lazy {
        UstaGoRepository(database, getSharedPreferences("ustago_session", MODE_PRIVATE))
    }
}
