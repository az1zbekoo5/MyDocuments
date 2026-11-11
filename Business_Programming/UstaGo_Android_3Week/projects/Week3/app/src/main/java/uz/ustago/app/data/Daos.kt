package uz.ustago.app.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface UserDao {
    @Insert suspend fun insert(user: User): Long
    @Query("SELECT * FROM users WHERE email = :email LIMIT 1")
    suspend fun byEmail(email: String): User?
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun byId(id: Long): User?
}

@Dao
interface CatalogueDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertGarages(items: List<Garage>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertServices(items: List<CarService>)
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertSlots(items: List<TimeSlot>)
    @Query("SELECT * FROM garages WHERE id = :id")
    fun garage(id: Long): Flow<Garage?>
    @Query("SELECT * FROM services WHERE id = :id")
    fun service(id: Long): Flow<CarService?>
    @Query("""SELECT * FROM services WHERE
        (name LIKE '%' || :query || '%' OR description LIKE '%' || :query || '%')
        AND (:category = 'All' OR category = :category) ORDER BY name""")
    fun search(query: String, category: String): Flow<List<CarService>>
    @Query("SELECT DISTINCT category FROM services ORDER BY category")
    fun categories(): Flow<List<String>>
    @Query("SELECT * FROM slots WHERE garageId = :garageId AND startsAt > :now AND booked = 0 ORDER BY startsAt")
    fun slots(garageId: Long, now: Long): Flow<List<TimeSlot>>
    @Query("SELECT COUNT(*) FROM services") suspend fun serviceCount(): Int
}

@Dao
interface VehicleDao {
    @Insert suspend fun insert(vehicle: Vehicle): Long
    @Query("SELECT * FROM vehicles WHERE userId = :userId ORDER BY id DESC")
    fun observe(userId: Long): Flow<List<Vehicle>>
}

@Dao
abstract class BookingDao {
    @Query("SELECT * FROM bookings WHERE userId = :userId ORDER BY createdAt DESC, id DESC")
    abstract fun observe(userId: Long): Flow<List<Booking>>
    @Query("SELECT * FROM bookings WHERE id = :id AND userId = :userId")
    abstract fun observeOne(id: Long, userId: Long): Flow<Booking?>
    @Query("SELECT * FROM services WHERE id = :id")
    protected abstract suspend fun service(id: Long): CarService?
    @Query("SELECT * FROM garages WHERE id = :id")
    protected abstract suspend fun garage(id: Long): Garage?
    @Query("SELECT * FROM slots WHERE id = :id")
    protected abstract suspend fun slot(id: Long): TimeSlot?
    @Query("SELECT * FROM vehicles WHERE id = :id AND userId = :userId")
    protected abstract suspend fun ownedVehicle(id: Long, userId: Long): Vehicle?
    @Query("UPDATE slots SET booked = 1 WHERE id = :id AND booked = 0 AND startsAt > :now")
    protected abstract suspend fun claim(id: Long, now: Long): Int
    @Insert protected abstract suspend fun insert(booking: Booking): Long

    // The claim and receipt insert either BOTH commit or BOTH roll back.
    @Transaction
    open suspend fun place(userId: Long, serviceId: Long, slotId: Long, vehicleId: Long,
        payment: String, note: String, now: Long = System.currentTimeMillis()): Long {
        require(payment in listOf("Cash", "Card at garage")) { "Choose a payment method." }
        require(note.length <= 300) { "Keep your note within 300 characters." }
        val service = requireNotNull(service(serviceId)) { "Service no longer exists." }
        val garage = requireNotNull(garage(service.garageId)) { "Garage no longer exists." }
        val vehicle = requireNotNull(ownedVehicle(vehicleId, userId)) { "Choose one of your vehicles." }
        val slot = requireNotNull(slot(slotId)) { "Choose an appointment time." }
        require(slot.garageId == service.garageId) { "This time belongs to another garage." }
        check(claim(slotId, now) == 1) { "This time is unavailable. Choose another time." }
        return insert(Booking(userId = userId, serviceId = serviceId, slotId = slotId,
            vehicleId = vehicleId, serviceName = service.name, garageName = garage.name,
            garageAddress = garage.address, vehicleLabel = "${vehicle.model} · ${vehicle.plate}",
            startsAt = slot.startsAt, total = service.price, paymentMethod = payment, note = note.trim()))
    }

    @Query("SELECT * FROM bookings WHERE id = :id AND userId = :userId")
    protected abstract suspend fun ownedBooking(id: Long, userId: Long): Booking?
    @Query("UPDATE bookings SET status = 'CANCELLED' WHERE id = :id AND status = 'CONFIRMED'")
    protected abstract suspend fun markCancelled(id: Long): Int
    @Query("UPDATE slots SET booked = 0 WHERE id = :id")
    protected abstract suspend fun release(id: Long)

    @Transaction
    open suspend fun cancel(id: Long, userId: Long, now: Long = System.currentTimeMillis()) {
        val booking = requireNotNull(ownedBooking(id, userId)) { "Booking not found." }
        check(booking.status == "CONFIRMED" && booking.startsAt > now) { "Only upcoming confirmed bookings can be cancelled." }
        check(markCancelled(id) == 1) { "Booking has already changed." }
        release(booking.slotId)
    }
}
