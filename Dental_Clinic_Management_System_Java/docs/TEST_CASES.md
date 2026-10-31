# Test cases (use synthetic records only)

| ID | Test | Expected result |
|---|---|---|
| TC01 | Start backend | Database tables and demo admin are initialized |
| TC02 | Login with admin / ChangeMe123! | Login succeeds |
| TC03 | Login with incorrect password | HTTP 401 / error displayed |
| TC04 | Register patient with name | Patient created with unique DENT code |
| TC05 | Register patient without name | Validation error |
| TC06 | Search by name/code/phone | Matching patient rows shown |
| TC07 | Save medical history | Conditions, allergies and medications persist |
| TC08 | Add each supported treatment category | Treatment saved |
| TC09 | Submit unknown treatment category | HTTP 400 |
| TC10 | Create appointment | Appointment is listed |
| TC11 | Cancel appointment | Status becomes Cancelled |
| TC12 | Add follow-up | Follow-up appears in list |
| TC13 | Save child chart for age 6–12 | Chart snapshot saved |
| TC14 | Save child chart outside 6–12 | Validation error |
| TC15 | Upload supported image | File and metadata saved |
| TC16 | Upload unsupported file extension | Validation error |
| TC17 | Call patient API while logged out | HTTP 401 |
| TC18 | Open browser and Android simultaneously | Both clients see server-side shared records |
