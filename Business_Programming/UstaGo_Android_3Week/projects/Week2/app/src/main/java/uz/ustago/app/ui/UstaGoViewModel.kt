package uz.ustago.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import uz.ustago.app.data.*

@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class UstaGoViewModel(private val repo: UstaGoRepository) : ViewModel() {
    val currentUser = repo.currentUser
    val ready = MutableStateFlow(false)
    val busy = MutableStateFlow(false)
    val message = MutableStateFlow<String?>(null)
    val query = MutableStateFlow("")
    val category = MutableStateFlow("All")
    // Refresh the available-slot time boundary while the app remains open.
    val clock = flow { while (true) { emit(System.currentTimeMillis()); delay(30000) } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), System.currentTimeMillis())
    val services = combine(query, category) { q, c -> q to c }
        .flatMapLatest { (q, c) -> repo.search(q, c) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
    val categories = repo.categories().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
    val vehicles = currentUser.flatMapLatest { user ->
        if (user == null) flowOf(emptyList()) else repo.vehicles(user.id)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
    val bookings = currentUser.flatMapLatest { user ->
        if (user == null) flowOf(emptyList()) else repo.bookings(user.id)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
    init { retryStartup() }
    fun retryStartup() = action {
        repo.initialize()
        ready.value = true
    }
    fun dismiss() { message.value = null }
    private fun action(block: suspend () -> Unit) {
        if (busy.value) return
        busy.value = true
        message.value = null
        viewModelScope.launch {
            try { block() }
            catch (e: CancellationException) { throw e }
            catch (e: Exception) { message.value = e.message ?: "Something went wrong. Please try again." }
            finally { busy.value = false }
        }
    }
    fun register(name: String, email: String, password: String) = action { repo.register(name, email, password) }
    fun login(email: String, password: String) = action { repo.login(email, password) }
    fun logout() { if (!busy.value) { repo.logout(); dismiss(); query.value = ""; category.value = "All" } }
    fun addVehicle(model: String, plate: String, done: () -> Unit) = action {
        repo.addVehicle(model, plate); done()
    }
    fun place(serviceId: Long, slotId: Long, vehicleId: Long, payment: String, note: String, done: (Long) -> Unit) = action {
        val id = repo.place(serviceId, slotId, vehicleId, payment, note); done(id)
    }
    fun cancel(id: Long) = action { repo.cancel(id); message.value = "Booking cancelled. The time is available again." }
    fun service(id: Long) = repo.service(id)
    fun garage(id: Long) = repo.garage(id)
    fun slots(garageId: Long) = clock.flatMapLatest { repo.slots(garageId, it) }
    fun booking(id: Long) = currentUser.flatMapLatest { user ->
        if (user == null) flowOf(null) else repo.booking(id, user.id)
    }
    class Factory(private val repo: UstaGoRepository) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(UstaGoViewModel::class.java))
            return UstaGoViewModel(repo) as T
        }
    }
}
