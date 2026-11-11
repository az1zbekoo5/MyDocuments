# Fix the first real error

| Error | Check/fix |
|---|---|
| Wrapper jar missing / cannot load GradleWrapperMain | Copy gradlew, gradlew.bat and gradle/wrapper/gradle-wrapper.jar from your generated Empty Activity template. Keep this kit's wrapper properties. |
| Minimum supported Gradle version mismatch | Use all supplied build files together, including Gradle 8.13 wrapper properties. Do not mix the PDF's AGP 9 configuration into this AGP 8 project. |
| SDK location not found | Open the project in Android Studio and select your SDK installation. Let the IDE create local.properties. |
| SDK 36 not installed | SDK Manager > SDK Platforms > install API 36. |
| Plugin/dependency cannot resolve | Check network/proxy and Gradle offline mode. Read the actual repository/network error. Do not guess a replacement version or disable certificate validation. |
| Kotlin/Compose plugin conflict | Restore supplied root/module Gradle and version catalog together. This AGP 8 project explicitly applies Kotlin Android and Compose plugins. |
| ClassCastException to UstaGoApp | Manifest application must have android:name=".UstaGoApp". |
| Unresolved reference database in MainActivity | Week1 activity needs application.database; the supplied Week2 application retains it. Replace application files from matching snapshots. |
| Unresolved screen or AppRoot | Copy the complete Day7 UI group before replacing/running MainActivity. |
| Room SQL error | Compare property/table names with Entities.kt. Room query columns use exact Kotlin property names. |
| Schema identity/migration error | Schema was changed without a migration. Keep the supplied schema for this course; a real schema edit needs version + Migration. Clearing data is only acceptable for disposable demo data. |
| No instrumentation device | Start emulator or connect/authorise a phone before connectedDebugAndroidTest. |
| Update incompatible signature | Debug and release keys differ. Use a second device or uninstall old app (deletes local data), then install release. |
| Slow laptop/emulator | Use your Android phone for tests, close unused apps and run one emulator at a time. |

To request help, provide: first Gradle error or FATAL EXCEPTION and its first uz.ustago.app stack line; Android Studio version; which week/day; changed file. Never send passwords or private signing keys.
