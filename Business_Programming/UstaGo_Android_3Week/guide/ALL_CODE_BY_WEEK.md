# Complete UstaGo source by weekly step

All paths below are relative to the working Android project. Copy complete files. The source folders contain identical code.

## Week1

### .gitignore

```text
.gradle/
.kotlin/
**/build/
local.properties
.idea/
*.jks
*.keystore
keystore.properties
```

### app/build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.ksp)
}
android {
    namespace = "uz.ustago.app"
    compileSdk = 36
    defaultConfig {
        applicationId = "uz.ustago.app"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
    buildTypes { release { isMinifyEnabled = false } }
    testOptions { animationsDisabled = true }
}
ksp { arg("room.schemaLocation", "$projectDir/schemas") }
dependencies {
    implementation(libs.core)
    implementation(libs.activity)
    implementation(libs.lifecycle.runtime)
    implementation(libs.lifecycle.viewmodel)
    implementation(libs.navigation)
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.preview)
    implementation(libs.material3)
    debugImplementation(libs.compose.tooling)
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    ksp(libs.room.compiler)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.test.runner)
    androidTestImplementation(libs.androidx.test.ext)
    androidTestImplementation(libs.room.testing)
}
```

### app/src/main/AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application android:name=".UstaGoApp" android:allowBackup="false"
        android:label="@string/app_name" android:icon="@drawable/ic_ustago"
        android:supportsRtl="true" android:theme="@style/Theme.UstaGo">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### app/src/main/java/uz/ustago/app/MainActivity.kt

```kotlin
package uz.ustago.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.CancellationException
import uz.ustago.app.data.SampleData
import uz.ustago.app.ui.theme.UstaGoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val db = (application as UstaGoApp).database
        setContent {
            UstaGoTheme {
                val status by produceState("Preparing database…") {
                    value = try {
                        SampleData.seed(db)
                        "Database ready · ${db.catalogue().serviceCount()} services"
                    } catch (e: CancellationException) { throw e }
                    catch (e: Exception) { "Database error: ${e.message}" }
                }
                Scaffold { padding ->
                    Column(Modifier.fillMaxSize().padding(padding).padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)) {
                        Text("UstaGo", style = MaterialTheme.typography.headlineLarge)
                        Text("Week 1 · Project and Room database")
                        Text(status)
                        Text("6 tables · 3 garages · 12 services")
                        Text("Week 2 adds login, vehicles, service search and appointment booking.")
                    }
                }
            }
        }
    }
}
```

### app/src/main/java/uz/ustago/app/UstaGoApp.kt

```kotlin
package uz.ustago.app
import android.app.Application
import uz.ustago.app.data.AppDatabase
class UstaGoApp : Application() {
    val database by lazy { AppDatabase.get(this) }
}
```

### app/src/main/java/uz/ustago/app/data/AppDatabase.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/data/Daos.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/data/Entities.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/data/SampleData.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/ui/theme/Theme.kt

```kotlin
package uz.ustago.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val Light = lightColorScheme(primary = Color(0xFF00796B),
    secondary = Color(0xFF8B5000), primaryContainer = Color(0xFFA5F2E0))
private val Dark = darkColorScheme(primary = Color(0xFF77D8C5),
    secondary = Color(0xFFFFB74D), primaryContainer = Color(0xFF005044))
@Composable
fun UstaGoTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = if (isSystemInDarkTheme()) Dark else Light, content = content)
}
```

### app/src/main/java/uz/ustago/app/util/Utils.kt

```kotlin
package uz.ustago.app.util

import java.security.MessageDigest
import java.security.SecureRandom
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

fun formatSom(amount: Long): String = String.format(Locale.US, "%,d", amount).replace(',', ' ') + " so'm"
fun formatTime(value: Long): String = SimpleDateFormat("EEE, dd MMM yyyy · HH:mm", Locale.ENGLISH).format(Date(value))
fun normalEmail(value: String): String = value.trim().lowercase(Locale.ROOT)
fun validEmail(value: String): Boolean = Regex("^[A-Za-z0-9.!#%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\\.[A-Za-z0-9-]+)+$").matches(value)
fun validPassword(value: String): Boolean = value.length in 8..128
fun validPlate(value: String): Boolean = value.trim().length in 5..15 &&
    value.trim().all { it.isLetterOrDigit() || it == ' ' || it == '-' }

// PBKDF2-HMAC-SHA1 is available on API 24. A random salt prevents identical hashes.
// This is device-local coursework authentication; a real service needs server auth.
object Passwords {
    private const val iterations = 210000
    private fun hex(bytes: ByteArray) = bytes.joinToString("") { "%02x".format(it.toInt() and 255) }
    private fun unhex(text: String): ByteArray = text.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
    private fun derive(password: String, salt: ByteArray, rounds: Int): ByteArray {
        val spec = PBEKeySpec(password.toCharArray(), salt, rounds, 256)
        return try { SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1").generateSecret(spec).encoded }
        finally { spec.clearPassword() }
    }
    fun hash(password: String): String {
        val salt = ByteArray(16).also { SecureRandom().nextBytes(it) }
        return "$iterations:${hex(salt)}:${hex(derive(password, salt, iterations))}"
    }
    fun verify(password: String, encoded: String): Boolean = try {
        val parts = encoded.split(':')
        val rounds = parts[0].toInt()
        if (parts.size != 3 || rounds != iterations || parts[1].length != 32 || parts[2].length != 64) false
        else MessageDigest.isEqual(unhex(parts[2]), derive(password, unhex(parts[1]), rounds))
    } catch (_: Exception) { false }
}
```

### app/src/main/res/drawable/ic_ustago.xml

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#00796B" android:pathData="M0,0h108v108h-108z" />
    <path android:fillColor="#FFFFFF" android:pathData="M27,29h12v35c0,8 5,12 15,12s15,-4 15,-12v-35h12v35c0,16 -10,25 -27,25s-27,-9 -27,-25z" />
    <path android:fillColor="#FFB74D" android:pathData="M45,18h18v9h-18z" />
</vector>
```

### app/src/main/res/values/strings.xml

```xml
<resources><string name="app_name">UstaGo</string></resources>
```

### app/src/main/res/values/styles.xml

```xml
<resources>
    <style name="Theme.UstaGo" parent="android:style/Theme.Material.Light.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:windowLightStatusBar">true</item>
        <item name="android:colorAccent">#00796B</item>
    </style>
</resources>
```

### build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.ksp) apply false
}
```

### gradle/libs.versions.toml

```toml
[versions]
agp = "8.13.2"
kotlin = "2.2.21"
ksp = "2.2.21-2.0.4"
core = "1.17.0"
activity = "1.11.0"
lifecycle = "2.9.4"
navigation = "2.9.5"
composeBom = "2025.10.01"
room = "2.8.4"

[libraries]
core = { module = "androidx.core:core-ktx", version.ref = "core" }
activity = { module = "androidx.activity:activity-compose", version.ref = "activity" }
lifecycle-runtime = { module = "androidx.lifecycle:lifecycle-runtime-compose", version.ref = "lifecycle" }
lifecycle-viewmodel = { module = "androidx.lifecycle:lifecycle-viewmodel-compose", version.ref = "lifecycle" }
navigation = { module = "androidx.navigation:navigation-compose", version.ref = "navigation" }
compose-bom = { module = "androidx.compose:compose-bom", version.ref = "composeBom" }
compose-ui = { module = "androidx.compose.ui:ui" }
compose-preview = { module = "androidx.compose.ui:ui-tooling-preview" }
compose-tooling = { module = "androidx.compose.ui:ui-tooling" }
material3 = { module = "androidx.compose.material3:material3" }
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }
junit = { module = "junit:junit", version = "4.13.2" }
androidx-test-runner = { module = "androidx.test:runner", version = "1.6.2" }
androidx-test-ext = { module = "androidx.test.ext:junit", version = "1.2.1" }
room-testing = { module = "androidx.room:room-testing", version.ref = "room" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
```

### gradle/wrapper/gradle-wrapper.properties

```text
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.13-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
```

### gradle.properties

```text
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
```

### settings.gradle.kts

```kotlin
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "UstaGo"
include(":app")
```

## Week2

### app/src/main/java/uz/ustago/app/MainActivity.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/UstaGoApp.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/data/UstaGoRepository.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/ui/AppNavHost.kt

```kotlin
package uz.ustago.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavType
import androidx.navigation.compose.*
import androidx.navigation.navArgument
import uz.ustago.app.ui.screens.*

@Composable
fun AppRoot(vm: UstaGoViewModel) {
    val ready by vm.ready.collectAsStateWithLifecycle()
    val user by vm.currentUser.collectAsStateWithLifecycle()
    val message by vm.message.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    if (!ready) {
        Scaffold { padding ->
            Column(Modifier.padding(padding).padding(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("Preparing UstaGo…", style = MaterialTheme.typography.headlineSmall)
                if (busy) CircularProgressIndicator()
                message?.let { Text(it, color = MaterialTheme.colorScheme.error) }
                if (!busy) Button(onClick = { vm.retryStartup() }) { Text("Retry") }
            }
        }
        return
    }
    // A different account receives a new navigation tree, including saved form state.
    key(user?.id) {
        if (user == null) AuthNavigation(vm) else MainNavigation(vm)
    }
}

@Composable
private fun StatusMessage(vm: UstaGoViewModel) {
    val message by vm.message.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    if (busy) LinearProgressIndicator(Modifier.fillMaxWidth())
    message?.let { text ->
        Surface(color = MaterialTheme.colorScheme.secondaryContainer) {
            Row(Modifier.fillMaxWidth().padding(start = 16.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(text, Modifier.weight(1f).padding(vertical = 12.dp))
                TextButton(onClick = vm::dismiss) { Text("Dismiss") }
            }
        }
    }
}

@Composable
private fun AuthNavigation(vm: UstaGoViewModel) {
    val nav = rememberNavController()
    Scaffold { padding ->
        Column(Modifier.padding(padding).imePadding()) {
            StatusMessage(vm)
            NavHost(nav, startDestination = "login", modifier = Modifier.weight(1f)) {
                composable("login") { AuthScreen(vm, false) { vm.dismiss(); nav.navigate("register") } }
                composable("register") { AuthScreen(vm, true) { vm.dismiss(); nav.popBackStack() } }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MainNavigation(vm: UstaGoViewModel) {
    val nav = rememberNavController()
    val entry by nav.currentBackStackEntryAsState()
    val route = entry?.destination?.route ?: "home"
    val busy by vm.busy.collectAsStateWithLifecycle()
    val rootRoutes = listOf("home", "bookings", "vehicles")
    val title = when (route) {
        "home" -> "UstaGo · Car services"
        "bookings" -> "My bookings"
        "vehicles" -> "My vehicles"
        "detail/{id}" -> "Service details"
        "book/{id}" -> "Choose your appointment"
        else -> "Booking receipt"
    }
    Scaffold(
        topBar = { TopAppBar(title = { Text(title) }, navigationIcon = {
            if (route !in rootRoutes) TextButton(enabled = !busy, onClick = { nav.popBackStack() }) { Text("Back") }
        }) },
        bottomBar = {
            NavigationBar {
                rootRoutes.zip(listOf("Services", "Bookings", "Vehicles")).forEach { (destination, label) ->
                    NavigationBarItem(selected = route == destination, enabled = !busy,
                        onClick = {
                            vm.dismiss()
                            nav.navigate(destination) { popUpTo("home"); launchSingleTop = true }
                        }, icon = { Text(label.take(1)) }, label = { Text(label) })
                }
            }
        }
    ) { padding ->
        Column(Modifier.fillMaxSize().padding(padding).imePadding()) {
            StatusMessage(vm)
            NavHost(nav, startDestination = "home", modifier = Modifier.weight(1f)) {
                composable("home") { HomeScreen(vm) { nav.navigate("detail/$it") } }
                composable("detail/{id}", arguments = listOf(navArgument("id") { type = NavType.LongType })) { back ->
                    val id = back.arguments!!.getLong("id")
                    DetailScreen(vm, id) { nav.navigate("book/$id") }
                }
                composable("book/{id}", arguments = listOf(navArgument("id") { type = NavType.LongType })) { back ->
                    BookScreen(vm, back.arguments!!.getLong("id"),
                        onVehicles = { nav.navigate("vehicles") },
                        onBooked = { id -> nav.navigate("receipt/$id") { popUpTo("home") } })
                }
                composable("vehicles") { VehiclesScreen(vm) }
                composable("bookings") { BookingsScreen(vm) { nav.navigate("receipt/$it") } }
                composable("receipt/{id}", arguments = listOf(navArgument("id") { type = NavType.LongType })) { back ->
                    ReceiptScreen(vm, back.arguments!!.getLong("id"))
                }
            }
        }
    }
}
```

### app/src/main/java/uz/ustago/app/ui/UstaGoViewModel.kt

```kotlin
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
```

### app/src/main/java/uz/ustago/app/ui/screens/AuthScreen.kt

```kotlin
package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel

@Composable
fun AuthScreen(vm: UstaGoViewModel, register: Boolean, switch: () -> Unit) {
    var name by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }
    // Password is intentionally not stored in saved instance state.
    var password by remember { mutableStateOf("") }
    val busy by vm.busy.collectAsStateWithLifecycle()
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text("UstaGo", style = MaterialTheme.typography.displaySmall)
        Text("Your next car service, organised.", style = MaterialTheme.typography.titleMedium)
        Text(if (register) "Create your account" else "Welcome back", style = MaterialTheme.typography.headlineSmall)
        if (register) OutlinedTextField(name, { name = it.take(80) }, label = { Text("Full name") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy)
        OutlinedTextField(email, { email = it.take(150) }, label = { Text("Email") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email))
        OutlinedTextField(password, { password = it.take(128) }, label = { Text("Password (8+ characters)") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy,
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password))
        Button(enabled = !busy, modifier = Modifier.fillMaxWidth(), onClick = {
            if (register) vm.register(name, email, password) else vm.login(email, password)
        }) { Text(if (register) "Create account" else "Log in") }
        TextButton(enabled = !busy, onClick = switch) {
            Text(if (register) "Already registered? Log in" else "New here? Create an account")
        }
        Text("Coursework demo: accounts and bookings are stored on this phone.", style = MaterialTheme.typography.bodySmall)
    }
}
```

### app/src/main/java/uz/ustago/app/ui/screens/BookScreen.kt

```kotlin
package uz.ustago.app.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.data.CarService
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.*
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun BookScreen(vm: UstaGoViewModel, id: Long, onVehicles: () -> Unit, onBooked: (Long) -> Unit) {
    val service by remember(vm, id) { vm.service(id) }.collectAsStateWithLifecycle(initialValue = null)
    val item = service
    if (item == null) { Text("Loading service…", Modifier.padding(16.dp)); return }
    BookingForm(vm, item, onVehicles, onBooked)
}

@Composable
private fun BookingForm(vm: UstaGoViewModel, service: CarService, onVehicles: () -> Unit, onBooked: (Long) -> Unit) {
    val slots by remember(vm, service.garageId) { vm.slots(service.garageId) }
        .collectAsStateWithLifecycle(initialValue = emptyList())
    val vehicles by vm.vehicles.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    var day by rememberSaveable(service.id) { mutableStateOf("") }
    var slotId by rememberSaveable(service.id) { mutableLongStateOf(0) }
    var vehicleId by rememberSaveable(service.id) { mutableLongStateOf(0) }
    var payment by rememberSaveable(service.id) { mutableStateOf("Cash") }
    var note by rememberSaveable(service.id) { mutableStateOf("") }
    var confirm by rememberSaveable { mutableStateOf(false) }
    val groups = slots.groupBy { SimpleDateFormat("EEE dd MMM yyyy", Locale.ENGLISH).format(Date(it.startsAt)) }
    val selectedDay = day.takeIf { it in groups } ?: groups.keys.firstOrNull()
    val selectedSlot = slots.firstOrNull { it.id == slotId }
    val selectedVehicle = vehicles.firstOrNull { it.id == vehicleId }
    val canBook = selectedSlot != null && selectedVehicle != null && !busy
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 20.dp)) {
        item {
            Text(service.name, style = MaterialTheme.typography.headlineSmall)
            Text(formatSom(service.price), style = MaterialTheme.typography.titleLarge)
            Text("1. Select a date", style = MaterialTheme.typography.titleMedium)
        }
        item {
            if (groups.isEmpty()) Text("No available times. Return to Services and choose another service.")
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                groups.keys.forEach { value ->
                    FilterChip(selectedDay == value, { day = value; slotId = 0 }, label = { Text(value) }, enabled = !busy)
                }
            }
        }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                groups[selectedDay].orEmpty().forEach { slot ->
                    FilterChip(slotId == slot.id, { slotId = slot.id }, label = {
                        Text(SimpleDateFormat("HH:mm", Locale.ENGLISH).format(Date(slot.startsAt)))
                    }, enabled = !busy)
                }
            }
        }
        item {
            Text("2. Select your vehicle", style = MaterialTheme.typography.titleMedium)
            if (vehicles.isEmpty()) Text("Add a vehicle first, then return here and select it.")
            vehicles.forEach { vehicle ->
                Row {
                    RadioButton(vehicleId == vehicle.id, { vehicleId = vehicle.id }, enabled = !busy)
                    Text("${vehicle.model} · ${vehicle.plate}", Modifier.padding(top = 12.dp))
                }
            }
            TextButton(enabled = !busy, onClick = onVehicles) { Text("Manage vehicles") }
        }
        item {
            Text("3. Payment at the garage", style = MaterialTheme.typography.titleMedium)
            listOf("Cash", "Card at garage").forEach { value ->
                Row {
                    RadioButton(payment == value, { payment = value }, enabled = !busy)
                    Text(value, Modifier.padding(top = 12.dp))
                }
            }
            Text("No money is charged in this app.", style = MaterialTheme.typography.bodySmall)
        }
        item { OutlinedTextField(note, { note = it.take(300) }, label = { Text("Optional note (max 300 characters)") },
            modifier = Modifier.fillMaxWidth(), enabled = !busy, minLines = 2) }
        item {
            selectedSlot?.let { Text("Appointment: ${formatTime(it.startsAt)}") }
            Text("Total: ${formatSom(service.price)}", style = MaterialTheme.typography.titleLarge)
            Button(enabled = canBook, onClick = { confirm = true }, modifier = Modifier.fillMaxWidth()) { Text("Review booking") }
        }
    }
    if (confirm) AlertDialog(onDismissRequest = { if (!busy) confirm = false },
        title = { Text("Confirm your appointment") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(service.name)
                Text(selectedSlot?.let { formatTime(it.startsAt) } ?: "Time no longer available. Please choose again.")
                Text(selectedVehicle?.let { "${it.model} · ${it.plate}" } ?: "Select a vehicle.")
                Text("${formatSom(service.price)} · $payment · unpaid")
            }
        },
        confirmButton = { TextButton(enabled = canBook, onClick = {
            vm.place(service.id, slotId, vehicleId, payment, note) { id -> confirm = false; onBooked(id) }
        }) { Text("Confirm booking") } },
        dismissButton = { TextButton(enabled = !busy, onClick = { confirm = false }) { Text("Edit") } })
}
```

### app/src/main/java/uz/ustago/app/ui/screens/BookingsScreen.kt

```kotlin
package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.*

@Composable
fun BookingsScreen(vm: UstaGoViewModel, onReceipt: (Long) -> Unit) {
    val bookings by vm.bookings.collectAsStateWithLifecycle()
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 16.dp)) {
        if (bookings.isEmpty()) item { Text("No bookings yet. Choose a service to make your first appointment.") }
        items(bookings, key = { it.id }) { booking ->
            Card(onClick = { onReceipt(booking.id) }, modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("#${booking.id} · ${booking.serviceName}", style = MaterialTheme.typography.titleMedium)
                    Text(booking.garageName)
                    Text(formatTime(booking.startsAt))
                    Text("${formatSom(booking.total)} · ${booking.status}")
                    Text("View receipt →")
                }
            }
        }
    }
}

@Composable
fun ReceiptScreen(vm: UstaGoViewModel, id: Long) {
    val booking by remember(vm, id) { vm.booking(id) }.collectAsStateWithLifecycle(initialValue = null)
    val busy by vm.busy.collectAsStateWithLifecycle()
    val now by vm.clock.collectAsStateWithLifecycle()
    var confirmCancel by rememberSaveable { mutableStateOf(false) }
    val item = booking
    if (item == null) { Text("Loading booking…", Modifier.padding(16.dp)); return }
    LazyColumn(Modifier.fillMaxSize().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item { Text("Booking #${item.id}", style = MaterialTheme.typography.headlineMedium) }
        item { Text(item.status, color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.titleMedium) }
        item { Text(item.serviceName, style = MaterialTheme.typography.titleLarge) }
        item { Text("${item.garageName}\n${item.garageAddress}") }
        item { Text(formatTime(item.startsAt) + " · 1 hour") }
        item { Text(item.vehicleLabel) }
        item { HorizontalDivider() }
        item { Text("Total: ${formatSom(item.total)}", style = MaterialTheme.typography.titleLarge) }
        item { Text("${item.paymentMethod} · ${item.paymentStatus}") }
        item { Text("Payment is due at the garage. This demo does not process payments.") }
        if (item.note.isNotBlank()) item { Text("Note: ${item.note}") }
        if (item.status == "CONFIRMED" && item.startsAt > now) item {
            OutlinedButton(enabled = !busy, onClick = { confirmCancel = true }) { Text("Cancel booking") }
        }
    }
    if (confirmCancel) AlertDialog(onDismissRequest = { confirmCancel = false },
        title = { Text("Cancel this booking?") }, text = { Text("The appointment time will become available again.") },
        confirmButton = { TextButton(enabled = !busy, onClick = { confirmCancel = false; vm.cancel(id) }) { Text("Cancel booking") } },
        dismissButton = { TextButton(onClick = { confirmCancel = false }) { Text("Keep booking") } })
}
```

### app/src/main/java/uz/ustago/app/ui/screens/DetailScreen.kt

```kotlin
package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.formatSom

@Composable
fun DetailScreen(vm: UstaGoViewModel, id: Long, onBook: () -> Unit) {
    val service by remember(vm, id) { vm.service(id) }.collectAsStateWithLifecycle(initialValue = null)
    val item = service
    if (item == null) { Text("Loading service…", Modifier.padding(16.dp)); return }
    val garage by remember(vm, item.garageId) { vm.garage(item.garageId) }.collectAsStateWithLifecycle(initialValue = null)
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Text(item.category, style = MaterialTheme.typography.labelLarge)
        Text(item.name, style = MaterialTheme.typography.headlineMedium)
        Text(formatSom(item.price), style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.primary)
        Text(item.description)
        HorizontalDivider()
        Text(garage?.name ?: "Loading garage…", style = MaterialTheme.typography.titleLarge)
        Text(garage?.address ?: "")
        Text(garage?.phone ?: "")
        Text("Appointment: one hour. Parts and extra repairs are excluded unless stated above.")
        Text("Demo businesses and availability. Payment is due at the garage.", style = MaterialTheme.typography.bodySmall)
        Button(onClick = onBook, enabled = garage != null, modifier = Modifier.fillMaxWidth()) { Text("Choose a time") }
    }
}
```

### app/src/main/java/uz/ustago/app/ui/screens/HomeScreen.kt

```kotlin
package uz.ustago.app.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel
import uz.ustago.app.util.formatSom

@Composable
fun HomeScreen(vm: UstaGoViewModel, onDetail: (Long) -> Unit) {
    val services by vm.services.collectAsStateWithLifecycle()
    val categories by vm.categories.collectAsStateWithLifecycle()
    val query by vm.query.collectAsStateWithLifecycle()
    val category by vm.category.collectAsStateWithLifecycle()
    Column(Modifier.fillMaxSize().padding(horizontal = 16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedTextField(query, { vm.query.value = it }, label = { Text("Search car services") },
            modifier = Modifier.fillMaxWidth(), singleLine = true)
        Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            (listOf("All") + categories).forEach { value ->
                FilterChip(category == value, { vm.category.value = value }, label = { Text(value) })
            }
        }
        Text("${services.size} services · prices in UZS", style = MaterialTheme.typography.labelLarge)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 16.dp)) {
            if (services.isEmpty()) item { Text("No matching services. Try another search or category.") }
            items(services, key = { it.id }) { service ->
                Card(onClick = { onDetail(service.id) }, modifier = Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(service.category, style = MaterialTheme.typography.labelMedium)
                        Text(service.name, style = MaterialTheme.typography.titleLarge)
                        Text(service.description, maxLines = 2)
                        Text(formatSom(service.price), style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.primary)
                        Text("View garage and available times →")
                    }
                }
            }
        }
    }
}
```

### app/src/main/java/uz/ustago/app/ui/screens/VehiclesScreen.kt

```kotlin
package uz.ustago.app.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import uz.ustago.app.ui.UstaGoViewModel

@Composable
fun VehiclesScreen(vm: UstaGoViewModel) {
    val vehicles by vm.vehicles.collectAsStateWithLifecycle()
    val busy by vm.busy.collectAsStateWithLifecycle()
    val user by vm.currentUser.collectAsStateWithLifecycle()
    var model by rememberSaveable { mutableStateOf("") }
    var plate by rememberSaveable { mutableStateOf("") }
    LazyColumn(Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(bottom = 20.dp)) {
        item {
            Text(user?.fullName ?: "", style = MaterialTheme.typography.titleLarge)
            Text(user?.email ?: "")
            TextButton(enabled = !busy, onClick = vm::logout) { Text("Log out") }
            Text("Add a vehicle", style = MaterialTheme.typography.titleMedium)
        }
        item { OutlinedTextField(model, { model = it.take(60) }, label = { Text("Model, e.g. Chevrolet Cobalt") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy) }
        item { OutlinedTextField(plate, { plate = it.take(15) }, label = { Text("Plate, e.g. 01 A 123 BC") },
            modifier = Modifier.fillMaxWidth(), singleLine = true, enabled = !busy) }
        item { Button(enabled = !busy, onClick = { vm.addVehicle(model, plate) { model = ""; plate = "" } }) { Text("Save vehicle") } }
        if (vehicles.isEmpty()) item { Text("No vehicles yet. Add your car before booking a service.") }
        items(vehicles, key = { it.id }) { vehicle ->
            OutlinedCard(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp)) {
                    Text(vehicle.model, style = MaterialTheme.typography.titleMedium)
                    Text(vehicle.plate)
                }
            }
        }
    }
}
```

## Week3

### app/src/androidTest/java/uz/ustago/app/BookingTransactionTest.kt

```kotlin
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
```

### app/src/test/java/uz/ustago/app/UtilsTest.kt

```kotlin
package uz.ustago.app

import org.junit.Assert.*
import org.junit.Test
import uz.ustago.app.util.*

class UtilsTest {
    @Test fun moneyUsesWholeSomAndSpaces() {
        assertEquals("80 000 so'm", formatSom(80000))
        assertEquals("1 250 000 so'm", formatSom(1250000))
    }
    @Test fun emailIsTrimmedAndCaseNormalised() {
        assertEquals("airen@example.com", normalEmail("  Airen@Example.COM  "))
    }
    @Test fun emailRequiresDomain() {
        assertTrue(validEmail("airen@example.com"))
        assertFalse(validEmail("airen@"))
        assertFalse(validEmail("airen example.com"))
    }
    @Test fun passwordLengthHasBounds() {
        assertFalse(validPassword("short"))
        assertTrue(validPassword("GoodPass123"))
        assertFalse(validPassword("x".repeat(129)))
    }
    @Test fun plateRejectsBlankAndPunctuation() {
        assertTrue(validPlate("01 A 123 BC"))
        assertFalse(validPlate("   "))
        assertFalse(validPlate("01@123"))
    }
    @Test fun saltedPasswordsVerifyAndRejectWrongPassword() {
        val first = Passwords.hash("GoodPass123")
        val second = Passwords.hash("GoodPass123")
        assertNotEquals(first, second)
        assertTrue(Passwords.verify("GoodPass123", first))
        assertFalse(Passwords.verify("WrongPass", first))
        assertFalse(Passwords.verify("GoodPass123", "broken"))
    }
}
```
