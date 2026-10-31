# API reference

All endpoints except `/api/health` and `/api/login` require a login session cookie.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Check server |
| POST | `/api/login` | Login JSON `{username,password}` |
| POST | `/api/logout` | Logout |
| GET | `/api/dashboard` | Summary counts |
| GET | `/api/patients?q=...` | Search patients |
| POST | `/api/patients` | Register patient |
| GET | `/api/patients/<id>` | Full patient record bundle |
| PUT | `/api/patients/<id>/medical-history` | Create/update medical history |
| GET | `/api/treatments/categories` | Supported categories |
| POST | `/api/treatments` | Add dental treatment |
| POST | `/api/charts` | Save chart snapshot |
| POST | `/api/images` | Multipart image upload |
| GET | `/api/images/<id>/file` | View uploaded image/file |
| GET | `/api/appointments` | List appointments |
| POST | `/api/appointments` | Schedule appointment |
| PATCH | `/api/appointments/<id>` | Update/cancel/complete appointment |
| GET | `/api/reminders` | Upcoming reminder queue, not delivery |
| GET | `/api/followups` | List follow-ups |
| POST | `/api/followups` | Create follow-up |
| PATCH | `/api/followups/<id>` | Update follow-up status |
