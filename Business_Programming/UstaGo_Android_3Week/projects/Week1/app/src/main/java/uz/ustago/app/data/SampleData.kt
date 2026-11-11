package uz.ustago.app.data

import androidx.room.withTransaction
import java.util.Calendar

object SampleData {
    val garages = listOf(
        Garage(1, "Chilonzor Auto Usta", "Tashkent, Chilonzor 6, 12", "+998 90 123 45 67"),
        Garage(2, "Yunusobod Avto Servis", "Tashkent, Yunusobod 4, 28", "+998 91 234 56 78"),
        Garage(3, "Samarqand Usta Markaz", "Samarkand, Rudakiy street, 41", "+998 93 345 67 89")
    )
    // Fictional demo businesses. Prices are whole UZS; each slot reserves one hour.
    val services = listOf(
        CarService(1,1,"Oil change","Maintenance","Engine oil replacement labour. Oil and filter are charged separately at the garage.",80000),
        CarService(2,1,"Brake inspection","Safety","Inspection of brake pads, discs and fluid. Replacement parts are extra.",90000),
        CarService(3,1,"Computer diagnostics","Diagnostics","Scan fault codes and explain the results. Repairs are quoted separately.",120000),
        CarService(4,1,"Wheel balancing","Tyres","Balance four passenger-car wheels. Wheel repairs are extra.",100000),
        CarService(5,2,"Battery test","Electrical","Check battery health and charging voltage. Battery replacement is extra.",50000),
        CarService(6,2,"Air filter replacement","Maintenance","Replacement labour for an accessible engine air filter. Filter is extra.",40000),
        CarService(7,2,"Tyre pressure check","Tyres","Inspect and adjust the pressure of four tyres.",25000),
        CarService(8,2,"Headlight adjustment","Electrical","Inspect and adjust headlight alignment. New bulbs are extra.",70000),
        CarService(9,3,"Suspension inspection","Safety","Inspect shocks, joints and bushes. Repairs are quoted separately.",110000),
        CarService(10,3,"Coolant inspection","Maintenance","Inspect coolant level and visible leaks. Coolant and repairs are extra.",60000),
        CarService(11,3,"Engine health check","Diagnostics","Basic visual inspection and fault scan. Major testing is quoted separately.",150000),
        CarService(12,3,"Wiper replacement","Safety","Replacement labour for front wiper blades. Blades are extra.",30000)
    )
    suspend fun seed(db: AppDatabase) {
        db.withTransaction {
            db.catalogue().insertGarages(garages)
            db.catalogue().insertServices(services)
            val slots = garages.flatMap { garage -> (1..14).flatMap { day ->
                listOf(9,10,11,14,15,16).map { hour ->
                    val time = Calendar.getInstance().apply {
                        add(Calendar.DAY_OF_YEAR, day)
                        set(Calendar.HOUR_OF_DAY, hour); set(Calendar.MINUTE, 0)
                        set(Calendar.SECOND, 0); set(Calendar.MILLISECOND, 0)
                    }.timeInMillis
                    TimeSlot(garageId = garage.id, startsAt = time)
                }
            } }
            // Unique garage/time index + IGNORE retain previously reserved slots.
            db.catalogue().insertSlots(slots)
        }
    }
}
