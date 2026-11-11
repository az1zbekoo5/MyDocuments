# Week 3 — Tests, polish, APK and presentation

Goal: run tests on your machine, verify a phone build, produce your signed APK, and prepare evidence/report/demo. This kit cannot sign on your behalf or invent screenshots/results.

## Day 11 — Add and run the test code

Keep Week2 production source. Copy these two new files from `projects/Week3`:

- `app/src/test/java/uz/ustago/app/UtilsTest.kt`.
- `app/src/androidTest/java/uz/ustago/app/BookingTransactionTest.kt`.

The test dependencies and instrumentation runner were already included in Week1's Gradle files.

Six JVM tests cover money formatting, email normalisation, invalid emails, password bounds, plate validation and salted password verification. Run by right-clicking UtilsTest > Run.

Four Android Room tests use an in-memory database, isolated from your real app data:

1. A second booking cannot take the same time.
2. Cancellation releases the time while retaining a cancelled receipt.
3. A forced receipt insert failure rolls back the earlier slot reservation.
4. Another account cannot use your car or cancel your booking.

Connect an emulator/phone and right-click BookingTransactionTest > Run. Alternatively, from your project's root in PowerShell:

```powershell
.\gradlew.bat testDebugUnitTest
.\gradlew.bat connectedDebugAndroidTest
.\gradlew.bat lintDebug assembleDebug
```

`testDebugUnitTest` does not need a device. `connectedDebugAndroidTest` does. If you see `No connected devices`, start the emulator or authorise USB debugging; do not count that as a test result.

Expected results when successful: six JVM tests and four device tests green. Record actual results in `TEST_RECORD.md`; this kit does not claim those tests have run. Check HTML reports under `app/build/reports/tests/` and `app/build/reports/androidTests/connected/`.

Use Database Inspector to capture a new booking, its reserved slot and its total. Explain that @Transaction saves both changes together.

Checkpoint: fix actual failures and rerun relevant checks. Commit: `Add validation and booking transaction tests`.

## Day 12 — Phone testing and polish

Use `TEST_RECORD.md`. At minimum, manually check:

- Fresh install: register and add a car.
- Wrong password and duplicate email/plate.
- Empty searches, no cars, no bookings.
- Time and car are required before confirmation.
- Cancellation/rebooking and app restart persistence.
- Two accounts keep cars and receipts separate.
- Rotate Home, Vehicles, the appointment form and the receipt.
- Dark mode and 200% system font size. Horizontally scroll date/time chips where needed.
- Long model names, long notes and keyboard visibility.
- Android Back never returns a logged-out user to the previous account's screens.
- Airplane mode after installation: the local app still works.

Name, vector icon and colours are already provided. To customise colours, edit `ui/theme/Theme.kt`. For a final adaptive icon, right-click app/src/main/res > New > Image Asset, choose Launcher Icons (Adaptive and Legacy), create `ic_launcher`, and change the manifest's application icon to `@mipmap/ic_launcher`. This generated asset is optional; the supplied vector icon already works as the launcher icon.

Test on a real phone: enable Developer options, USB debugging, use a data cable, accept the RSA authorisation prompt, select the phone in Android Studio and Run. A phone can reduce your laptop's emulator memory load.

Checkpoint: record the actual device model/API and any known issues. Commit: `Polish UstaGo and verify on real device`.

## Day 13 — Build your signed APK

Firebase is optional in the PDF and intentionally deferred here. Adding it during release preparation would change the app's authentication/database architecture. Your required offline flow is already implemented.

1. Run the tests and debug build checks first.
2. Android Studio > Build > Generate Signed App Bundle / APK > APK > Next.
3. Create a new keystore outside your Git repository. Choose your own alias/password; keep a private backup.
4. Select release and finish the wizard. Menu wording may differ slightly by Android Studio version.
5. Locate `app/build/outputs/apk/release/` or the destination shown by the wizard.
6. Install that APK on your phone and retest login, booking, cancellation and restart.

Release and debug signing differ. If the phone reports an incompatible signature, either use a second test device or uninstall the debug app first. Uninstalling deletes its local data, so re-create demo accounts/bookings and screenshots afterwards. Future signed updates must use the same release key.

Command-line debug install, if adb is on PATH:

```powershell
.\gradlew.bat assembleDebug
adb install -r .\app\build\outputs\apk\debug\app-debug.apk
```

This command produces/installs a DEBUG build; it does not replace the signed-release requirement. Do not publish keystore files or passwords.

Checkpoint: signed APK installs and its full journey works on a physical phone. Commit source changes, not private signing materials.

## Day 14 — Report, slides and backup video

Use `REPORT_AND_DEMO.md` for the detailed outline. Create an 8–12 page report with your own screenshots, tests, code explanations and results. Prepare 8–10 slides and a three-minute backup video.

The report needs your student name, group, actual GitHub URL and APK link; these are intentionally not invented. Describe the system as a device-local booking prototype. Do not claim shared real garage availability, online payments or production security.

Explain three pieces of code in your own words:

1. The conditional slot UPDATE + @Transaction.
2. Search/category StateFlow → DAO Flow → Compose UI.
3. Password salt/hash verification and local session restoration.

Checkpoint: report contains the screen map, six-entity diagram, database screenshot, actual tests and installation guide. Commit: `Document UstaGo architecture testing and demo`.

## Day 15 — Rehearse and submit

Rehearse the seven-minute script in `REPORT_AND_DEMO.md`. Charge the phone, install the release, prepare a spare account, and check that tomorrow's appointment times exist by launching the app.

Final deliverables from the PDF:

- Signed release APK.
- GitHub project with README and commits on at least five days.
- 8–12 page report PDF.
- 8–10 presentation slides.
- Three-minute backup video.
- `submission.txt` with all working links.

Week3 is worth 40 points. Do not tick an item until you have actually produced and checked it.
