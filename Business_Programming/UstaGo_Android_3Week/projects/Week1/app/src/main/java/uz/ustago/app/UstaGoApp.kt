package uz.ustago.app
import android.app.Application
import uz.ustago.app.data.AppDatabase
class UstaGoApp : Application() {
    val database by lazy { AppDatabase.get(this) }
}
