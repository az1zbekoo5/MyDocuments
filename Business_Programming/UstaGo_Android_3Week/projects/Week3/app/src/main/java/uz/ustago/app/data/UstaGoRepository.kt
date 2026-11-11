package uz.ustago.app.data

import android.content.SharedPreferences
import android.database.sqlite.SQLiteConstraintException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import uz.ustago.app.util.*
import java.util.Locale

class UstaGoRepository(private val db: AppDatabase, private val prefs: SharedPreferences) {
    private val mutableUser = MutableStateFlow<User?>(null)
    val currentUser = mutableUser.asStateFlow()
    suspend fun initialize() = withContext(Dispatchers.IO) {
        SampleData.seed(db)
        val id = prefs.getLong("userId", 0)
        mutableUser.value = if (id > 0) db.users().byId(id) else null
    }
    private fun session(user: User) {
        prefs.edit().putLong("userId", user.id).apply()
        mutableUser.value = user
    }
    suspend fun register(name: String, emailInput: String, password: String) = withContext(Dispatchers.IO) {
        val email = normalEmail(emailInput)
        require(name.trim().length in 2..80) { "Enter a name with 2–80 characters." }
        require(validEmail(email)) { "Enter a valid email address." }
        require(validPassword(password)) { "Use a password with 8–128 characters." }
        require(db.users().byEmail(email) == null) { "This email is already registered." }
        val user = User(fullName = name.trim(), email = email, passwordHash = Passwords.hash(password))
        val id = try { db.users().insert(user) } catch (_: SQLiteConstraintException) {
            throw IllegalArgumentException("This email is already registered.")
        }
        session(user.copy(id = id))
    }
    suspend fun login(email: String, password: String) = withContext(Dispatchers.IO) {
        val user = db.users().byEmail(normalEmail(email))
        require(user != null && Passwords.verify(password, user.passwordHash)) { "Email or password is incorrect." }
        session(user)
    }
    fun logout() { prefs.edit().remove("userId").apply(); mutableUser.value = null }
    private fun userId() = checkNotNull(mutableUser.value) { "Please log in again." }.id
    fun search(query: String, category: String) = db.catalogue().search(query.trim(), category)
    fun categories() = db.catalogue().categories()
    fun service(id: Long) = db.catalogue().service(id)
    fun garage(id: Long) = db.catalogue().garage(id)
    fun slots(garageId: Long, now: Long) = db.catalogue().slots(garageId, now)
    fun vehicles(userId: Long) = db.vehicles().observe(userId)
    fun bookings(userId: Long) = db.bookings().observe(userId)
    fun booking(id: Long, userId: Long) = db.bookings().observeOne(id, userId)
    suspend fun addVehicle(model: String, plate: String) {
        require(model.trim().length in 2..60) { "Enter a model with 2–60 characters." }
        require(validPlate(plate)) { "Enter a plate with 5–15 letters, digits, spaces or hyphens." }
        try {
            db.vehicles().insert(Vehicle(userId = userId(), model = model.trim(), plate = plate.trim().uppercase(Locale.ROOT)))
        } catch (_: SQLiteConstraintException) { throw IllegalArgumentException("You already added this plate.") }
    }
    suspend fun place(serviceId: Long, slotId: Long, vehicleId: Long, payment: String, note: String) =
        db.bookings().place(userId(), serviceId, slotId, vehicleId, payment, note)
    suspend fun cancel(id: Long) = db.bookings().cancel(id, userId())
}
