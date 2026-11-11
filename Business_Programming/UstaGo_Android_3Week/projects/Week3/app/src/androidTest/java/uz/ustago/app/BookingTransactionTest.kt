package uz.ustago.app

import android.content.Context
import androidx.room.Room
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import uz.ustago.app.data.*

@RunWith(AndroidJUnit4::class)
class BookingTransactionTest {
    private lateinit var db: AppDatabase
    private var user = 0L
    private var vehicle = 0L
    private var slot = 0L
    @Before fun setup() = runBlocking {
        val context: Context = InstrumentationRegistry.getInstrumentation().targetContext
        db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
        SampleData.seed(db)
        user = db.users().insert(User(fullName = "Test User", email = "test@example.com", passwordHash = "test-only"))
        vehicle = db.vehicles().insert(Vehicle(userId = user, model = "Cobalt", plate = "01 A 123 BC"))
        slot = db.catalogue().slots(1, System.currentTimeMillis()).first().first().id
    }
    @After fun close() { db.close() }
    private suspend fun place() = db.bookings().place(user, 1, slot, vehicle, "Cash", "")
    private fun reserved(): Int = db.openHelper.readableDatabase
        .query("SELECT booked FROM slots WHERE id = $slot").use { it.moveToFirst(); it.getInt(0) }

    @Test fun secondBookingCannotTakeReservedSlot() = runBlocking {
        place()
        var rejected = false
        try { place() } catch (_: IllegalStateException) { rejected = true }
        assertTrue(rejected)
        assertEquals(1, db.bookings().observe(user).first().size)
        assertEquals(1, reserved())
    }
    @Test fun cancellationReleasesSlotAndKeepsReceipt() = runBlocking {
        val id = place()
        db.bookings().cancel(id, user)
        assertEquals(0, reserved())
        assertEquals("CANCELLED", db.bookings().observeOne(id, user).first()!!.status)
        assertTrue(place() > id)
    }
    @Test fun failedReceiptInsertRollsBackSlotClaim() = runBlocking {
        // Force failure AFTER claim(), inside the same Room transaction.
        db.openHelper.writableDatabase.execSQL("""CREATE TRIGGER fail_receipt BEFORE INSERT ON bookings
            BEGIN SELECT RAISE(ABORT, 'forced receipt failure'); END""")
        var rejected = false
        try { place() } catch (_: android.database.sqlite.SQLiteException) { rejected = true }
        assertTrue(rejected)
        assertEquals(0, reserved())
        assertTrue(db.bookings().observe(user).first().isEmpty())
    }
    @Test fun anotherUserCannotUseYourVehicleOrCancelYourBooking() = runBlocking {
        val id = place()
        val other = db.users().insert(User(fullName = "Other", email = "other@example.com", passwordHash = "test-only"))
        var cancelRejected = false
        try { db.bookings().cancel(id, other) } catch (_: IllegalArgumentException) { cancelRejected = true }
        assertTrue(cancelRejected)
        val next = db.catalogue().slots(1, System.currentTimeMillis()).first().first().id
        var vehicleRejected = false
        try { db.bookings().place(other, 1, next, vehicle, "Cash", "") }
        catch (_: IllegalArgumentException) { vehicleRejected = true }
        assertTrue(vehicleRejected)
        assertTrue(db.bookings().observe(other).first().isEmpty())
        assertEquals(1, reserved())
    }
}
