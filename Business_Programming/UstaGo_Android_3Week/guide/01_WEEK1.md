# Week 1 — Project, design and Room

Goal: UstaGo builds and displays `Database ready · 12 services`. This follows the PDF's Week 1 requirements: at least four entities, at least two relations, Flow reads, suspend writes, a transaction, realistic sample items, branding and GitHub.

## Day 1 — Create and prove your own project

You have run SavdoShop. Now create a separate **Empty Activity** project:

| Setting | Value |
|---|---|
| Name | UstaGoTemplate |
| Package | uz.ustago.app |
| Language/build | Kotlin / Kotlin DSL |
| Minimum SDK | 24 |
| Location example | D:\AndroidProjects\UstaGoTemplate |

Run the generated Hello Android app. This verifies the template before replacing its files. Keep it as the wrapper source for the setup script.

Read `README_START_HERE.md`, then use its script to prepare `D:\AndroidProjects\UstaGo`.

Manual alternative:

1. Copy the entire `projects/Week1` folder to a new `D:\AndroidProjects\UstaGo` folder.
2. From `UstaGoTemplate`, copy `gradlew` and `gradlew.bat` to the new project's root. Copy `gradle/wrapper/gradle-wrapper.jar` to the identical relative path in the new project.
3. Keep the kit's `gradle/wrapper/gradle-wrapper.properties`. It specifies Gradle 8.13. Do not copy the template's wrapper properties over it.
4. Open the new UstaGo folder through File > Open. If Android Studio asks where the SDK is, select your installed SDK. Let it create `local.properties`; do not commit that machine-specific file.
5. Select JDK 17 in Gradle settings and install SDK Platform 36 through SDK Manager. Sync.

Checkpoint: configuration is loaded, Gradle sync has no errors. Commit: `Create UstaGo Android project`.

## Day 2 — Understand the UstaGo plan

Use `guide/DESIGN.md` for the screen map and ER diagram. You can draw the same map on paper for your teacher.

| SavdoShop concept | UstaGo equivalent |
|---|---|
| Product | CarService, belonging to a Garage |
| Stock | Unbooked TimeSlot |
| Shopping cart | Appointment form with service, time and vehicle |
| Checkout | Confirm booking |
| Order | Booking receipt |
| Order history | My bookings |

The six Room tables are defined in `app/src/main/java/uz/ustago/app/data/Entities.kt`:

- `users`: generated ID, full name, unique email, salted password hash.
- `garages`: ID, name, address, phone.
- `services`: ID, garage FK, name/category/description/whole-so'm price.
- `vehicles`: generated ID, user FK, model, plate; plate unique within each user.
- `slots`: generated ID, garage FK, start timestamp, booked flag; garage/time unique.
- `bookings`: generated ID, four FKs, receipt snapshots, payment/status/note/timestamps.

Open the exact file above in the Week1 snapshot. It is the complete code for this step; do not make a second class named User or Booking in another package.

Checkpoint: explain `@Entity`, `@PrimaryKey`, `ForeignKey` and `Index`, and why money uses `Long`. Commit: `Model UstaGo garages services vehicles and bookings`.

## Day 3 — Read and verify the database code

Open these files, in this order. The Week1 snapshot contains their complete contents.

1. `data/Daos.kt`: UserDao, CatalogueDao, VehicleDao and BookingDao.
2. `data/AppDatabase.kt`: six entities, four DAO accessors, singleton, schema version 1.
3. `data/SampleData.kt`: three fictional garages, 12 services and 14 days of times.

Paths are relative to `app/src/main/java/uz/ustago/app/`.

Understand the SQL:

- `CatalogueDao.search()` combines a search term and category, returning `Flow<List<CarService>>`.
- `CatalogueDao.slots()` exposes unbooked future times only.
- `VehicleDao.observe()` only lists the selected user's cars.
- `BookingDao.place()` validates the car owner and matching garage, conditionally reserves the slot, then inserts a price/vehicle/garage snapshot.
- `@Transaction` rolls back the slot reservation if inserting the receipt fails.
- `BookingDao.cancel()` changes the receipt status and releases the slot together.

Room generates the implementation during KSP compilation. Never create a manual `AppDatabase_Impl` file.

Checkpoint: Build > Make Project. Resolve the first build error before proceeding. Commit: `Add Room queries and atomic booking transaction`.

## Day 4 — Start the database and brand the app

Read the remaining Week1 files:

| File | Purpose |
|---|---|
| `UstaGoApp.kt` | Owns the Room singleton for the application |
| `MainActivity.kt` | Seeds sample data and displays the Week1 diagnostic screen |
| `ui/theme/Theme.kt` | Teal/orange theme; light and dark palettes |
| `util/Utils.kt` | Money/date formatting, validation, salted password helpers for Week2 |
| `app/src/main/AndroidManifest.xml` | Registers `.UstaGoApp` and launcher activity |
| `app/src/main/res/values/strings.xml` | App name UstaGo |
| `app/src/main/res/values/styles.xml` | Activity window theme |
| `app/src/main/res/drawable/ic_ustago.xml` | Offline vector app icon |

Run. Expected: **UstaGo / Week 1 · Project and Room database / Database ready · 12 services**.

`produceState` launches a coroutine. Room's suspend calls do not run database work on the main thread. Seeding is idempotent: `IGNORE` preserves existing garage/service rows and already-booked slots, using their unique keys. Restarting the app adds missing future days rather than resetting reservations.

Open View > Tool Windows > App Inspection > Database Inspector while this debug app is running. Select `ustago.db`.

Run:

```sql
SELECT COUNT(*) FROM services; -- 12
SELECT COUNT(*) FROM garages; -- 3
SELECT COUNT(*) FROM slots; -- normally 252 on a fresh first run
SELECT name, price FROM services ORDER BY id;
```

There are 3 garages × 14 days × 6 one-hour slots = 252 initial times. More rows after later-day launches are expected because history is preserved. The users/vehicles/bookings tables are empty until Week2.

Checkpoint: save a screenshot showing the running app and another of Database Inspector. Commit: `Seed sample services and apply UstaGo brand`.

## Day 5 — Review and submit Week 1

- Explain the six tables and at least two relations without reading the answer.
- Explain why one slot cannot be reserved twice on this phone.
- Switch system light/dark mode and rotate the diagnostic screen.
- Restart and confirm 12 services still exist.
- Capture a successful build screenshot after the actual build finishes.
- Save the screen map, ER diagram and source in GitHub; do not commit keys, build folders or local.properties.

Use Android Studio Git > Enable Version Control Integration if necessary, then Commit and Push. Submission: GitHub link + screen map image + successful build screenshot. Week1 is worth 25 points in the PDF.

Do not change the entity schema before Week2; the weekly snapshots deliberately share version 1.
