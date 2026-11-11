# Report, presentation and defence preparation

## 8–12 page report

1. Title: UstaGo, student/group/date, real GitHub link, real APK link or QR.
2. Business case: drivers need a clear way to organise car service; target local drivers and garages. Proposed future revenue: garage subscription or fee per completed booking. These are ideas, not implemented payments.
3. Design: screen map and 3–4 sketches beside actual final screenshots; explain teal/orange and offline catalogue.
4. Data model: six entities, FK relationships, unique indices; explain whole-so'm prices and receipt snapshots.
5. Architecture/code: describe MVVM; explain three code fragments in your own words. Include conditional claim, transaction rollback, reactive search or session restoration.
6. Testing: actual unit/device test output, Database Inspector screenshot, phone test matrix and bugs fixed.
7. User guide: install APK, register, add vehicle, search, select appointment, confirm, view/cancel. Explain local data and payment at garage.
8. Roadmap: backend and server-side appointment rules; garage dashboard; roadside assistance; car rental; notifications/real payment integration. Give your own realistic next steps rather than asserting these features already exist.

## 8–10 slides

1. UstaGo and the driver problem.
2. Target users and proposed business model.
3. Main journey and screenshots.
4. Data model.
5. MVVM structure.
6. Atomic appointment reservation.
7. Test evidence and phone demonstration.
8. Current limits and next features.
9. Optional lessons learned.
10. Optional final contact/questions slide.

## Seven-minute live demo

| Time | Action |
|---|---|
| 0:00–0:45 | Explain the problem: arranging car service can take several calls; UstaGo makes the choice and appointment visible. |
| 0:45–1:30 | Target drivers/garages and proposed revenue. Say this version is an offline prototype. |
| 1:30–3:30 | Register or log in; add a car; search service; open details; choose time; review and confirm; show history. |
| 3:30–4:15 | Demonstrate wrong password or unavailable time; cancel and show time released. |
| 4:15–5:15 | Show the database receipt and reserved slot; explain MVVM. |
| 5:15–6:00 | Explain the conditional UPDATE and transaction in your own code. |
| 6:00–7:00 | Show test results, roadmap, conclusion and questions. |

## Defence questions

- Why does a receipt copy the price? It records what was accepted when the appointment was made, even if catalogue prices later change.
- Why is slots a Flow? Room emits new results when reservations change, so the UI reacts.
- What does suspend mean? The function can suspend without blocking its caller's thread; Room schedules database work appropriately.
- Why do you need @Transaction? A slot claim and its receipt must succeed together; otherwise the claim rolls back.
- Can two phones reserve the same real garage time? This local prototype cannot coordinate phones. A shared backend with server-enforced constraints is required.
- Why does a slot have multiple receipts in the diagram? Cancellation keeps the old receipt and allows a new reservation later; at most one is confirmed through the DAO flow.
- What happens on rotation? The ViewModel survives configuration change and saved form fields restore; the password is intentionally cleared.
- Is the payment completed? No. The app records an unpaid booking and a preference for paying at the garage.
- What would you change for 1,000 users? Move authoritative auth, catalogue and booking validation to a backend; retain a local cache for offline reads.

## submission.txt contents

Replace these labels with actual working links, then save as submission.txt:

GitHub: YOUR_LINK
Signed APK: YOUR_LINK
Report PDF: YOUR_LINK
Slides: YOUR_LINK
Backup video: YOUR_LINK
Student/group: YOUR_DETAILS
