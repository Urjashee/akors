# Hoofsnap API (Code Block Style)

---

# 🔐 AUTH APIs

## Register

```http
POST /auth/register
```

```text
Requests:
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string"
}

Response:
{
  "user_id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```

---

## Verify Email

```http
POST /auth/verify-email
```

```text
Request:
{
  "token": "string"
}
```

---

## Login

```http
POST /auth/login
```

```text
Request:
{
  "email": "string",
  "password": "string",
  "device_type": "int"
}

Response:
{
  "access_token": "string",
  "refresh_token": "string"
}
```

---

## Forgot Password

```http
POST /auth/forgot-password
```

```text
Request:
{
  "email": "string"
}
```

---

## Reset Password

```http
POST /auth/reset-password
```

```text
Request:
{
  "token": "string",
  "password": "string"
}
```

---

## Logout

```http
POST /auth/logout
```

---

## Delete Account

```http
DELETE /auth/account
```

```text
Request:
{
  "password": "string"
}
```

---

## Refresh Token

```http
POST /auth/refresh-token
```

```text
Response:
{
  "access_token": "string"
}
```

---

## Update Profile

```http
PUT /auth/profile
```

```text
Request:
{
  "first_name": "string",
  "last_name": "string"
}
```

---

# 🏠 STABLE APIs

## List Stables

```http
GET /stables?page=&per_page=
```

```text
Response:
[
  {
    "stable_id": "string",
    "stable_name": "string",
    "equine_count": "integer",
    "client_name": "string"
  }
]
```

---

## Create Stable

```http
POST /stables
```

```text
Request:
{
  "stable_name": "string",
  "stable_address": "string",
  "client_name": "string",
  "client_address": "string",
  "client_phone": "string",
  "client_email": "string",
  "special_instructions": "string"
}
```

---

## Get Stable

```http
GET /stables/:stable_id
```

```text
Response:
{
  "stable_id": "string",
  "stable_name": "string",
  "stable_address": "string | null",
  "client_name": "string",
  "client_address": "string | null",
  "client_phone": "string | null",
  "client_email": "string | null",
  "special_instructions": "string | null"
}
```

---

## Update Stable

```http
PUT /stables/:stable_id
```

```text
Request:
{
  "stable_name": "string",
  "stable_address": "string",
  "client_name": "string",
  "client_address": "string",
  "client_phone": "string",
  "client_email": "string",
  "special_instructions": "string"
}
```

---

## Get Equines in Stable

```http
GET /stables/:stable_id/equines?page=&per_page=
```

```text
Response:
[
  {
    "equine_id": "int",
    "name": "string",
    "image_url": "string | null"
  }
]
```

---

## Add Equines to Stable

```http
POST /stables/:stable_id/equine/add
```

```text
Request:
{
  "equine_id": ["array"]
}
```

---

# 🐎 EQUINE APIs

## Get All Equines

```http
GET /equines/all?page=&per_page=
```

```text
Response:
[
  {
    "stable_id": "int",
    "equine_id": "int",
    "name": "string",
    "image_url": "string | null"
  }
]
```

---

## Create Equine

```http
POST /equines
```

```text
Request:
{
  "name": "string",
  "age": "string",
  "gender": "string",
  "breed": "string",
  "weight": "string",
  "height": "string",
  "notes": "string",
  "image": "file"
}
```

---

## Get Equine

```http
GET /equines/:equine_id
```

```text
Response:
{
  "equine_id": "string",
  "stable_id": "string | null",
  "name": "string",
  "age": "string | null",
  "gender": "string | null",
  "breed": "string | null",
  "weight": "string | null",
  "height": "string | null",
  "notes": "string | null",
  "image_url": "string | null"
}
```

---

## Update Equine

```http
PUT /equines/:equine_id
```

```text
Request:
{
  "name": "string",
  "age": "string",
  "gender": "string",
  "breed": "string",
  "weight": "string",
  "height": "string",
  "notes": "string",
  "image": "file",
  "remove_image": "boolean"
}
```

---

# 📸 POSTURE PHOTOS

## Get Posture Photos

```http
GET /equines/:equine_id/posture-photos
```

```text
Response:
{
  "session_id": "string",
  "date": "MM/DD/YYYY",
  "front_photo_url": [],
  "hind_photo_url": [],
  "left_photo_url": [],
  "right_photo_url": [],
  "gait_observations": "string | null"
}
```

---

## Upload Posture Photos

```http
POST /equines/:equine_id/posture-photos
```

```bash
front_photo_url[]
hind_photo_url[]
left_photo_url[]
right_photo_url[]
gait_observations
```

---

# 🐾 HOOF PHOTOS

## Get Hoof Photos

```http
GET /equines/:equine_id/hoof-photos
```

```text
Response:
{
  "session_id": "string",
  "date": "MM/DD/YYYY",
  "hoof_application": "string | null",
  "general_notes": "string | null",
  "front_left": [],
  "front_right": [],
  "hind_left": [],
  "hind_right": []
}
```

---

## Upload Hoof Photos

```http
POST /equines/:equine_id/hoof-photos
```

```bash
hoof_application
general_notes
front_left[]
front_right[]
hind_left[]
hind_right[]
session_id
```

---

# 📏 HOOF MEASUREMENTS

## Get Measurements

```http
GET /equines/:equine_id/hoof-measurements
```

```text
Response:
{
  "measurement_id": "string",
  "heel_width": "number",
  "frog_width": "number",
  "frog_length": "number",
  "widest_part": "number",
  "heel_to_heel": "number",
  "total_hoof_length": "number",
  "dorsal_wall_length": "number",
  "other_measurements": "string"
}
```

---

## Create Measurements

```http
POST /equines/:equine_id/hoof-measurements
```

```text
Request:
{
  "heel_width": "number",
  "frog_width": "number",
  "frog_length": "number",
  "widest_part": "number",
  "heel_to_heel": "number",
  "total_hoof_length": "number",
  "dorsal_wall_length": "number",
  "other_measurements": "string"
}
```

---

# 🖼️ IMAGES

## Get All Images

```http
GET /equines/:equine_id/images-all
```

```text
Response:
{
  "images": []
}
```
