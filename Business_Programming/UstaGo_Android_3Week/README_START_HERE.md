# UstaGo Android: three-week build kit

Start with `guide/01_WEEK1.md`. You already tested SavdoShop, so the guide's initial environment check is complete.

## What you are building

An offline car-service booking app, using Kotlin, Jetpack Compose, Material 3, Navigation, ViewModel/StateFlow and Room. A customer registers, adds a car, searches 12 services across three fictional Uzbek garages, chooses a one-hour appointment, confirms a booking and views or cancels it. Appointments are generated for the next 14 days whenever the app starts.

This is an Android coursework version of UstaGo. Your existing website/PostgreSQL/MongoDB project remains separate. Room is SQLite inside this Android app; do not enter your PostgreSQL credentials into it. Roadside assistance, car rental, reviews, remote synchronisation and online payments are later extensions. The car-service flow is complete within this scope.

## Weekly deliverables

| Week | Guide | Cumulative source snapshot | Expected result |
|---|---|---|---|
| 1 | `guide/01_WEEK1.md` | `projects/Week1` | Branded app opens; Room has 6 tables, 3 garages, 12 services, available times |
| 2 | `guide/02_WEEK2.md` | `projects/Week2` | Register/login, cars, search/filter, service detail, booking, receipt, history/cancellation |
| 3 | `guide/03_WEEK3.md` | `projects/Week3` | Same app plus 6 unit tests and 4 Room device tests; release/report/demo instructions |

Each snapshot contains the complete source for that stage. `guide/ALL_CODE_BY_WEEK.md` also prints every text source/configuration file, organised by week. No `TODO()` implementation placeholders are used. Week 3 has the same production source as Week 2; its extra code is the test suite.

## Set up the project once

1. Extract this ZIP to a short path, such as `D:\AndroidProjects\UstaGoKit`.
2. Keep your working SavdoShop untouched. Create an **Empty Activity** project named `UstaGoTemplate`, package `uz.ustago.app`, minimum SDK 24, Kotlin DSL. Run its Hello Android screen once.
3. This kit intentionally reuses the official Gradle wrapper from that locally generated template. It does not contain `gradlew`, `gradlew.bat` or `gradle-wrapper.jar`. Its wrapper configuration pins Gradle 8.13.
4. Use the manual steps in Week 1 or run this from the extracted kit folder in PowerShell (change the paths):

```powershell
.\Setup-Project.ps1 -TemplatePath "D:\AndroidProjects\UstaGoTemplate" -Week Week1 -Destination "D:\AndroidProjects\UstaGo"
```

If your computer blocks local PowerShell scripts, use the manual copy instructions in Week 1. No policy change is needed.

5. Open the resulting `UstaGo` folder in Android Studio, install Android SDK Platform 36 and choose JDK 17 under Settings > Build, Execution, Deployment > Build Tools > Gradle > Gradle JDK. Sync and run.

The helper only writes into a NEW destination and refuses an existing folder. For weekly progression use the file changes in the guides; there is no need to make three separate apps. All snapshots have the same application ID and database version, so updating the installed app preserves its data if the signing key stays the same.

## Version policy

The PDF demonstrates AGP 9.x. This kit instead consistently pins AGP 8.13.2 + Gradle 8.13 + Kotlin/Compose compiler 2.2.21 + KSP 2.2.21-2.0.4, with Room 2.8.4. This is a deliberate alternative configuration, not a request to mix Gradle files from the two versions. AGP 8 uses an explicit Kotlin Android plugin; AGP 9's built-in Kotlin setup differs.

Use ALL provided build files together. Do not accept automatic dependency upgrades during this coursework. `compileSdk`/`targetSdk` are 36 and `minSdk` is 24. Initial Gradle sync needs an internet connection.

## Validation status

The kit was checked for file structure, configuration consistency, XML/TOML syntax, source presence and SQLite transaction behaviour. Android Studio, the Android SDK/emulator and Gradle are unavailable in the authoring environment, so the app has **not been compiled or run here**. The included Kotlin/JUnit and Android Room tests are provided for you to run; they are not claimed as passing. No APK or signed release is included.

Use the checkpoints in each guide. If a build fails, send the first actual error plus the relevant file; a red editor underline alone is not enough to diagnose it.

## Important app rules

- All accounts and appointments are on this installation. Other phones do not share bookings or garage availability.
- One garage has one appointment bay. Every service reserves one hour. Dates display in the phone's local timezone.
- The price is copied into each receipt. Payment remains `UNPAID`; Cash/Card at garage only record your preference.
- Passwords use salted PBKDF2, calculated off the UI thread. This is local demonstration authentication, not a remote identity service.
- Confirmed future appointments can be cancelled. Old receipts remain visible.
- Closing the app preserves Room data and the local login session. Uninstalling or clearing app storage deletes that data.
- The demo database has no destructive-migration fallback. Keep its schema unchanged during these three weeks; real schema changes require a version increase and migration.
