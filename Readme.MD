# Meeting Service API Documentation

## Endpoints

### Health Check
- **GET** `/health`
- **Response:**
  - `200 OK`: `Server is working`

---

### Get All Meetings by Club
- **GET** `/<club_id>`
- **Description:** Returns all meetings for the specified club.
- **Response:**
  - `200 OK`: `{ status: "ok", data: [...] }`
  - `500 ERROR`: `{ status: "error", message: <error> }`

---

### Create Meeting
- **POST** `/<club_id>`
- **Description:** Creates a new meeting for the specified club.
- **Request Body:**
```json
{
  "timeful_link": "string (optional)",
  "zoom_link": "string (optional)",
  "event_id": "bigint (optional)",
  "meeting_dt": "timestamp (required)",
  "personnel_list": "jsonb (optional)"
}
```
- **Response:**
  - `201 CREATED`: `{ status: "ok", data: [...] }`
  - `400 ERROR`: `{ status: "error", message: "meeting_dt and club_id are required" }`
  - `500 ERROR`: `{ status: "error", message: <error> }`

---

### Update Meeting
- **PUT** `/<club_id>/<meeting_id>`
- **Description:** Updates fields of a meeting for the specified club.
- **Request Body:**
```json
{
  "timeful_link": "string (optional)",
  "zoom_link": "string (optional)",
  "event_id": "bigint (optional)",
  "meeting_dt": "timestamp (optional)",
  "personnel_list": "jsonb (optional)"
}
```
- **Response:**
  - `200 OK`: `{ status: "ok", data: [...] }`
  - `400 ERROR`: `{ status: "error", message: "No valid fields to update" }`
  - `500 ERROR`: `{ status: "error", message: <error> }`

---

### Delete Meeting
- **DELETE** `/<club_id>/<meeting_id>`
- **Description:** Deletes a meeting for the specified club.
- **Response:**
  - `200 OK`: `{ status: "ok", message: "Meeting deleted", data: [...] }`
  - `404 ERROR`: `{ status: "error", message: "Meeting not found" }`
  - `500 ERROR`: `{ status: "error", message: <error> }`

---
