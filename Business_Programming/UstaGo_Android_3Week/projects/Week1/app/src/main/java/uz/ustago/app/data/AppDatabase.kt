package uz.ustago.app.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [User::class, Garage::class, CarService::class, Vehicle::class,
    TimeSlot::class, Booking::class], version = 1, exportSchema = true)
abstract class AppDatabase : RoomDatabase() {
    abstract fun users(): UserDao
    abstract fun catalogue(): CatalogueDao
    abstract fun vehicles(): VehicleDao
    abstract fun bookings(): BookingDao
    companion object {
        @Volatile private var instance: AppDatabase? = null
        fun get(context: Context): AppDatabase = instance ?: synchronized(this) {
            instance ?: Room.databaseBuilder(context.applicationContext,
                AppDatabase::class.java, "ustago.db").build().also { instance = it }
        }
    }
}
