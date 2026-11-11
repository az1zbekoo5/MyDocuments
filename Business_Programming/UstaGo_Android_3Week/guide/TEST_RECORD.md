# UstaGo test record — fill with actual results

Student: __________  Date: __________  Device/API: __________
Android Studio version: __________  Git commit: __________

| Check | Expected result | Actual result / evidence |
|---|---|---|
| Gradle sync/build | No errors | Not run |
| Six JVM tests | All green | Not run |
| Four Room device tests | All green | Not run |
| Lint/debug assemble | Completes; assess warnings | Not run |
| Register/duplicate email | Valid account works; duplicate rejected | Not run |
| Login/wrong password | Correct accepted; incorrect rejected | Not run |
| Session restart | Same local account restored | Not run |
| Add vehicle/duplicate plate | Valid saved; duplicate rejected | Not run |
| Search/category/empty search | Correct list and empty text | Not run |
| Booking incomplete | Confirmation disabled | Not run |
| Confirm booking | Receipt and reserved slot saved | Not run |
| Repeat same time | Time absent/rejected | Not run |
| Cancel/rebook | Cancelled receipt remains; time released | Not run |
| Other account | No other user's cars/bookings | Not run |
| Rotation/form | Ordinary fields survive; password clears | Not run |
| Dark mode/large text | Readable; controls reachable | Not run |
| Airplane mode | Local flows work | Not run |
| Signed APK on phone | Installs and all flows work | Not run |

Known issues and fixes:

| Problem | Cause | Fix | Retest result |
|---|---|---|---|
| Fill after testing | | | |

Never replace Not run with Passed without performing the check.
