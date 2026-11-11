# Week 2 — Full customer journey

Goal: register → add a vehicle → search service → detail → choose time → review/confirm → receipt/history. The PDF permits a booking flow instead of a cart.

## Before changing files

Commit Week1. Keep the installed app and its data. These are cumulative sources, so you can apply the changes below into your existing UstaGo project.

Every path below is relative to `app/src/main/java/uz/ustago/app/`. Copy the **whole indicated file**, preserving its package line. Complete code is in `projects/Week2` and printed in `ALL_CODE_BY_WEEK.md`. No Gradle/schema changes are required between Week1 and Week2.

## Day 6 — Repository and ViewModel

Copy these Week2 files into your working project:

1. `util/Utils.kt` (same utility API as Week1).
2. `data/UstaGoRepository.kt` (new).
3. `ui/UstaGoViewModel.kt` (new).
4. `UstaGoApp.kt` (replace with Week2 version).

The Week2 application retains its `database` property so the Week1 MainActivity still compiles at this intermediate checkpoint. It adds `repository` alongside it.

Read the repository functions:

| Function | What happens |
|---|---|
| initialize | Seed missing demo data, restore saved user ID |
| register | Validate input, normalise email, salt/hash password on IO thread, insert user, start session |
| login | Find email, verify hash off main thread, start session |
| addVehicle | Validate model/plate and insert a car owned by current user |
| place | Ask DAO to atomically claim time and write receipt |
| cancel | Ask DAO to cancel and release time atomically |
| logout | Remove saved user ID and publish a signed-out state |

The ViewModel publishes StateFlow values for current user, search query, selected category, services, cars, bookings, busy and messages. Its action helper prevents duplicate submissions, handles ordinary failures and rethrows coroutine cancellation.

Why the layers matter: a screen never performs SQL. A screen sends an event to the ViewModel, which calls the repository, which calls the DAO.

Checkpoint: Build > Make Project; the old Week1 diagnostic screen should still run. Commit: `Add local auth repository and reactive ViewModel`.

## Day 7 — Install all UI files and wire navigation

Copy from Week2:

- `ui/AppNavHost.kt`.
- The complete `ui/screens` folder: AuthScreen, HomeScreen, DetailScreen, VehiclesScreen, BookScreen and BookingsScreen.
- Replace `MainActivity.kt` last.

Copy this group together before building; navigation refers to all the screens. This avoids leaving unresolved placeholder screens. Day 8–10 then walk through and verify each flow.

MainActivity obtains the repository from UstaGoApp and creates a ViewModel using its Factory. AppRoot waits for seed/session restoration before showing a login screen or the signed-in navigation graph.

| Route | Purpose |
|---|---|
| login | Sign in |
| register | Create account |
| home | Search/filter services |
| detail/{id} | Service + garage details |
| book/{id} | Select time, car and payment preference |
| vehicles | Add/list own cars and log out |
| bookings | Own booking history |
| receipt/{id} | Booking details and cancellation |

There are eight routes, including arguments and three bottom tabs. A booking receipt is the post-confirmation screen. The booking form's review dialog is the checkout confirmation.

Checkpoint: app opens at login without a saved session; Create account opens registration; Back works. Commit: `Connect UstaGo screens and navigation`.

## Day 8 — Test registration, session and cars

1. Open Create account. Submit a one-letter name, invalid email or short password: friendly validation should appear.
2. Register `Airen`, `airen@example.com`, `GoodPass123` (demo credentials, not a password used elsewhere).
3. Confirm Services opens. Go to Vehicles; check the account name/email.
4. Save model `Chevrolet Cobalt`, plate `01 A 123 BC`. Verify its card appears.
5. Add the same plate again: a duplicate message should appear.
6. Close and reopen the app. It should restore the local login session and vehicle.
7. Log out from Vehicles, try a wrong password, then log back in correctly.
8. Register a second account and confirm its Vehicles and Bookings screens are empty. Return to your first account.

Read `AuthScreen.kt`: name/email survive rotation using rememberSaveable. Password deliberately uses remember, so rotation clears it rather than serialising it into saved instance state. Read `Passwords` in Utils.kt: the stored value contains iterations, random salt and derived hash; the raw password is never stored.

Database Inspector:

```sql
SELECT id, fullName, email FROM users;
SELECT id, userId, model, plate FROM vehicles;
```

Do not include password hashes in public report screenshots. Checkpoint: register, wrong-password handling, session restoration and account scoping all work. Commit: `Verify account and vehicle flows`.

## Day 9 — Test service search and details

1. Confirm Home shows 12 services on a fresh database.
2. Search `oil`: Oil change appears.
3. Clear search and select Electrical: Battery test and Headlight adjustment appear.
4. Enter an unmatched query: the empty message appears.
5. Open Oil change. Verify 80 000 so'm, Chilonzor Auto Usta and its address.
6. Press Choose a time. Return with Back, then open a different service and confirm its own details.
7. Rotate with a typed search term; the ViewModel keeps it during rotation.

Read `HomeScreen.kt` and `DetailScreen.kt`: screens collect Flow/StateFlow with `collectAsStateWithLifecycle`. Changing search/category switches the DAO query. IDs are passed with NavType.LongType, not by copying the entire service object into the route.

The catalogue text states whether parts are extra. Do not describe the sample price as an all-inclusive repair quote.

Checkpoint: searches, categories, correct ID routing and Back work. Commit: `Verify service catalogue and details`.

## Day 10 — Book, cancel and record the whole flow

1. Log in with your first account and make sure its vehicle exists.
2. Open Oil change > Choose a time.
3. Select one of the next 14 dates and a displayed hour. Times are local to the phone.
4. Select your vehicle. Choose Cash or Card at garage. Add an optional note.
5. Review booking. Confirm the service, appointment, car, price and payment preference.
6. Confirm booking. Verify the receipt contains status CONFIRMED, payment UNPAID and the exact snapshot details.
7. Open Bookings and verify the new row appears.
8. Return to the same garage/service: that exact appointment should be absent.
9. Open the receipt > Cancel booking > confirm. Verify CANCELLED remains in history and the time becomes available again.
10. Rebook that released time and confirm a new receipt is created.
11. Restart and verify history persists. Try another account: it must not show your receipt.

All services in the same garage share one appointment bay, so a time reserved for Oil change is also unavailable for Brake inspection at that garage. Other garages retain their own times.

The confirm button is disabled without both a vehicle and an available time. A periodic clock removes expired choices; the DAO checks the real time again when confirming. The database transaction remains the final authority, even if a displayed list becomes stale.

Inspect:

```sql
SELECT id, userId, serviceName, startsAt, total, status, paymentStatus FROM bookings;
SELECT id, garageId, startsAt, booked FROM slots WHERE booked = 1;
```

Final Week2 checkpoint: all eight routes work, bottom tabs and Back work, no crash on rotation, clear empty/error states, duplicate tapping does not create a second booking. Record a two-minute journey: register → car → search → detail → appointment → receipt → history. Submission: GitHub link + recording. Week2 is worth 35 points.

No Payme/Click charge is performed. For the demonstration say “payment preference recorded, payment due at the garage.”
