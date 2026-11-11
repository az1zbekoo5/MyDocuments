package uz.ustago.app.data

import androidx.room.*

@Entity(tableName = "users", indices = [Index(value = ["email"], unique = true)])
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val fullName: String,
    val email: String,
    val passwordHash: String
)

@Entity(tableName = "garages")
data class Garage(
    @PrimaryKey val id: Long,
    val name: String,
    val address: String,
    val phone: String
)

@Entity(tableName = "services", foreignKeys = [
    ForeignKey(entity = Garage::class, parentColumns = ["id"], childColumns = ["garageId"])
], indices = [Index("garageId")])
data class CarService(
    @PrimaryKey val id: Long,
    val garageId: Long,
    val name: String,
    val category: String,
    val description: String,
    val price: Long
)

@Entity(tableName = "vehicles", foreignKeys = [
    ForeignKey(entity = User::class, parentColumns = ["id"], childColumns = ["userId"], onDelete = ForeignKey.CASCADE)
], indices = [Index("userId"), Index(value = ["userId", "plate"], unique = true)])
data class Vehicle(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val userId: Long,
    val model: String,
    val plate: String
)

// A garage has ONE appointment bay. Every appointment occupies one hour.
@Entity(tableName = "slots", foreignKeys = [
    ForeignKey(entity = Garage::class, parentColumns = ["id"], childColumns = ["garageId"])
], indices = [Index(value = ["garageId", "startsAt"], unique = true)])
data class TimeSlot(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val garageId: Long,
    val startsAt: Long,
    val booked: Boolean = false
)

@Entity(tableName = "bookings", foreignKeys = [
    ForeignKey(entity = User::class, parentColumns = ["id"], childColumns = ["userId"]),
    ForeignKey(entity = CarService::class, parentColumns = ["id"], childColumns = ["serviceId"]),
    ForeignKey(entity = TimeSlot::class, parentColumns = ["id"], childColumns = ["slotId"]),
    ForeignKey(entity = Vehicle::class, parentColumns = ["id"], childColumns = ["vehicleId"])
], indices = [Index("userId"), Index("serviceId"), Index("slotId"), Index("vehicleId")])
data class Booking(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val userId: Long,
    val serviceId: Long,
    val slotId: Long,
    val vehicleId: Long,
    // Snapshots preserve the receipt if catalogue information changes later.
    val serviceName: String,
    val garageName: String,
    val garageAddress: String,
    val vehicleLabel: String,
    val startsAt: Long,
    val total: Long,
    val paymentMethod: String,
    val note: String,
    val status: String = "CONFIRMED",
    val paymentStatus: String = "UNPAID",
    val createdAt: Long = System.currentTimeMillis()
)
