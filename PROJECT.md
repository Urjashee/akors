# AKORS API Documentation

---

# ⚙️ CONFIG APIs

## Get Config

```http
GET /api/config/get
```

```text
Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "roles": [
      { "id": "int", "name": "string" }
    ],
    "titles": [
      { "id": "int", "name": "string" }
    ],
    "subscriptions": [
      {
        "id": "int",
        "name": "string",
        "amount": "int",
        "external_id": "string | null",
        "units": "int"
      }
    ],
    "states": [
      { "id": "int", "name": "string", "is_active": "boolean" }
    ],
    "unit_classes": [
      { "id": "int", "name": "string" }
    ],
    "unit_types": [
      { "id": "int", "name": "string" }
    ]
  }
}
```

---

# 🔐 AUTH / ACCOUNTS APIs

## Register Operator

```http
POST /api/accounts/operator/register
```

```text
Request:
{
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "title": "int | null",
  "qei_number": "string | null",
  "company_name": "string | null",
  "company_address": "string | null",
  "phone_number": "string | null",
  "subscription": "int | null"
}

Response:
{
  "status": "SUCCESS",
  "message": "Successfully created operator account.",
  "data": {
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "qei_number": "string | null"
  }
}
```

---

## Register Property Manager

```http
POST /api/accounts/property_manager/register
```

```text
Request:
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "company_name": "string | null",
  "company_address": "string | null",
  "phone_number": "string | null"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "email": "string",
    "first_name": "string",
    "last_name": "string"
  }
}
```

---

## Verify Email

```http
POST /api/accounts/verify
```

```text
Request:
{
  "token": "string",
  "user_id": "int",
  "type": "int",
  "password": "string | null"
}

Response:
{
  "status": "SUCCESS",
  "message": "Email verified successfully",
  "data": null
}
```

---

## Forgot Password

```http
POST /api/accounts/forgot-password
```

```text
Request:
{
  "email": "string"
}

Response:
{
  "status": "SUCCESS",
  "message": "Password reset request sent successfully.",
  "data": null
}
```

Note: Rate limited to 1 request per 5 minutes per email.

---

## Reset Password

```http
POST /api/accounts/reset-password
```

```text
Request:
{
  "token": "string",
  "user_id": "int",
  "type": "int",
  "password": "string"
}

Response:
{
  "status": "SUCCESS",
  "message": "Password reset successfully.",
  "data": null
}
```

---

## Login

```http
POST /api/accounts/login
```

```text
Request:
{
  "email": "string",
  "password": "string"
}

Response:
{
  "status": "SUCCESS",
  "message": "Login successful.",
  "data": {
    "access_token": "string",
    "refresh_token": "string"
  }
}
```

---

## Refresh Token

```http
POST /api/accounts/refresh-token
```

```text
Headers:
Authorization: Bearer <refresh_token>

Response:
{
  "status": "SUCCESS",
  "message": "Token refreshed successfully.",
  "data": {
    "access_token": "string"
  }
}
```

---

## Create Password (Invited User)

```http
POST /api/accounts/create-password
```

```text
Request:
{
  "token": "string",
  "password": "string",
  "type": "int"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Setup Operator Account

```http
POST /api/accounts/setup
```

```text
Request:
{
  "token": "string",
  "qei_number": "string",
  "password": "string"
}

Response:
{
  "status": "SUCCESS",
  "message": "Operator account setup successfully.",
  "data": null
}
```

---

## Change Password

```http
POST /api/accounts/change-password
```

```text
Auth: Bearer Token (any authenticated user)

Request:
{
  "old_password": "string",
  "password": "string"
}

Response:
{
  "status": "SUCCESS",
  "message": "Password updated successfully.",
  "data": null
}
```

---

# 👤 OPERATOR APIs

## Get Operator Profile

```http
GET /api/accounts/operator/profile
```

```text
Auth: Bearer Token (Operator role)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "id": "int",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "qei_number": "string | null",
    "company_name": "string | null",
    "company_address": "string | null",
    "phone_number": "string | null",
    "title": { "id": "int", "name": "string" } | null,
    "role": { "id": "int", "name": "string" }
  }
}
```

---

# 🏢 PROPERTY MANAGER APIs

## Get Property Manager Profile

```http
GET /api/accounts/property-manager/profile
```

```text
Auth: Bearer Token (Property Manager role)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "id": "int",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "company_name": "string | null",
    "company_address": "string | null",
    "phone_number": "string | null",
    "role": { "id": "int", "name": "string" }
  }
}
```

---

## Edit Property Manager Profile

```http
POST /api/accounts/property-manager/profile/edit
```

```text
Auth: Bearer Token (Property Manager role)

Request:
{
  "first_name": "string",
  "last_name": "string",
  "company_name": "string | null",
  "company_address": "string | null",
  "phone_number": "string | null"
}

Response:
{
  "status": "SUCCESS",
  "message": "Successfully updated property manager.",
  "data": null
}
```

---

## Invite Operator User

```http
POST /api/accounts/property-manager/invite-users
```

```text
Auth: Bearer Token (Property Manager role)

Request:
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "title": "int"
}

Response:
{
  "status": "SUCCESS",
  "message": "Successfully invited operator account.",
  "data": null
}
```

---

## Get Property Manager's Users

```http
GET /api/accounts/property-manager/users?current_page=&page_size=
```

```text
Auth: Bearer Token (Property Manager role)

Response:
{
  "status": "SUCCESS",
  "message": "Users fetched successfully.",
  "data": {
    "users": [
      {
        "id": "int",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "status": "Invited | Active | Pending",
        "title": { "id": "int", "name": "string" } | null
      }
    ],
    "current_page": "int",
    "page_size": "int",
    "total": "int",
    "total_pages": "int"
  }
}
```

---

## Toggle Operator Active Status

```http
PATCH /api/accounts/property-manager/user-toggle/{user_id}
```

```text
Auth: Bearer Token (Property Manager role)

Response:
{
  "status": "SUCCESS",
  "message": "Successfully updated user status.",
  "data": null
}
```

---

## Delete Operator User

```http
PATCH /api/accounts/property-manager/delete-user/{user_id}
```

```text
Auth: Bearer Token (Property Manager role)

Response:
{
  "status": "SUCCESS",
  "message": "Successfully deleted user.",
  "data": null
}
```

---

# 🛡️ ADMIN APIs

## Get All Users

```http
GET /api/accounts/admin/users?current_page=&page_size=&status=
```

```text
Auth: Bearer Token (Super Admin role)

Query Parameters:
- current_page: int (required)
- page_size: int (required)
- status: "verified_operator" | "verified_property_manager" | "pending_property_manager" (optional)

Response:
{
  "status": "SUCCESS",
  "message": "Users fetched successfully.",
  "data": {
    "pending_users_count": "int",
    "users": [
      {
        "id": "int",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "email_verified_at": "datetime | null",
        "status": "Active | Inactive",
        "company_name": "string | null",
        "company_address": "string | null",
        "phone_number": "string | null",
        "role": { "id": "int", "name": "string" },
        "subscription": {
          "id": "int",
          "name": "string",
          "amount": "number"
        } | null
      }
    ],
    "current_page": "int",
    "page_size": "int",
    "total": "int",
    "total_pages": "int"
  }
}
```

---

## Approve or Deny User

```http
POST /api/accounts/admin/user-approve
```

```text
Auth: Bearer Token (Super Admin role)

Request:
{
  "user_id": "int",
  "status": "approve | deny"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

Note: On approval, a create-password email is sent. On denial, the user is deactivated and a denial email is sent.

---

## Toggle User Active Status (Admin)

```http
PATCH /api/accounts/admin/user-toggle/{user_id}
```

```text
Auth: Bearer Token (Super Admin role)

Response:
{
  "status": "SUCCESS",
  "message": "Successfully updated user status.",
  "data": null
}
```

---

## Get User Details (Admin)

```http
GET /api/property/get-user-details/{user_id}
```

```text
Auth: Bearer Token (Super Admin role)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "user": {
      "id": "int",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "role": { "id": "int", "name": "string" }
    },
    "property": [
      {
        "id": "int",
        "name": "string",
        "unit_count": "int"
      }
    ],
    "payment_history": [
      {
        "invoice_id": "string",
        "amount": "number",
        "date": "string",
        "status": "string"
      }
    ]
  }
}
```

---

## Assign Property Manager to Property

```http
POST /api/property/admin/assign-manager
```

```text
Auth: Bearer Token (Super Admin role)

Request:
{
  "property_id": "int",
  "manager_id": "int"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

# 🏠 PROPERTY APIs

## Add or Edit Property

```http
POST /api/property/add-edit
```

```text
Auth: Bearer Token (any authenticated user)

Request:
{
  "id": "int | null",
  "name": "string",
  "state_registration": "string",
  "property_management_company": "string",
  "address_line_1": "string",
  "address_line_2": "string",
  "city": "string",
  "zipcode": "string",
  "state_id": "int",
  "forms": ["int"] | null,
  "manager_id": "int | null"
}

Note:
- Operators create new properties (no id)
- Property Managers and Super Admins edit existing properties (with id)
- manager_id is only used by Super Admin

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Get Properties

```http
GET /api/property/get?current_page=&page_size=
```

```text
Auth: Bearer Token (any authenticated user)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "properties": [
      {
        "id": "int",
        "name": "string",
        "address_line_1": "string",
        "address_line_2": "string",
        "city": "string",
        "zipcode": "string",
        "property_management_company": "string",
        "state_registration": "string",
        "state": { "id": "int", "name": "string" },
        "forms": [
          {
            "id": "int",
            "name": "string",
            "image": "string | null",
            "unit_type": "string | null",
            "active": "int | null"
          }
        ],
        "unit_count": "int"
      }
    ],
    "current_page": "int",
    "page_size": "int",
    "total": "int",
    "total_pages": "int"
  }
}
```

Note: Property Managers see only assigned properties; Operators see only properties they created.

---

## Search Properties

```http
GET /api/property/search?query=&current_page=&page_size=
```

```text
Auth: None (public)

Query Parameters:
- query: string (optional)
- current_page: int (required)
- page_size: int (required)

Response: Same structure as GET /api/property/get
```

---

# 🏗️ UNIT APIs

## Add or Edit Unit

```http
POST /api/property/unit/add-edit
```

```text
Auth: Bearer Token (any authenticated user)
Content-Type: multipart/form-data

Request:
- id: int (optional — omit to create, include to edit)
- nickname: string
- state_registration: string
- unit_type: int
- unit_class: int
- property: int
- expiration_date: datetime (optional, Property Manager only)
- certificate: file (optional, Property Manager only during edit)

Note:
- Operators create new units (no id)
- Property Managers edit existing units (with id)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Add Unit Image

```http
POST /api/property/unit/add-image
```

```text
Auth: Bearer Token (any authenticated user)
Content-Type: multipart/form-data

Request:
- unit_id: int
- image: file

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "image_id": "int",
    "image_url": "string"
  }
}
```

---

## Add Unit Form

```http
POST /api/property/unit/add-form
```

```text
Auth: Bearer Token (any authenticated user)
Content-Type: multipart/form-data

Request:
- unit_id: int
- form_name: string
- image: file
- expiration_date: datetime (optional)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "image_id": "int",
    "image_url": "string"
  }
}
```

---

## Delete Unit Form

```http
DELETE /api/property/unit/delete-form/{unit_form_id}
```

```text
Auth: Bearer Token (any authenticated user)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Delete Unit Image

```http
DELETE /api/property/unit/delete-image/{unit_image_id}
```

```text
Auth: Bearer Token (any authenticated user)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Get Units for Property

```http
GET /api/property/units/get/{property_id}?current_page=&page_size=
```

```text
Auth: Bearer Token (any authenticated user)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "units": [
      {
        "id": "int",
        "nickname": "string",
        "state_registration": "string | null",
        "expiration_date": "datetime | null",
        "certificate": "string | null",
        "unit_type": { "id": "int", "name": "string" } | null,
        "unit_class": { "id": "int", "name": "string" } | null,
        "user": { "id": "int", "email": "string" } | null,
        "property": {
          "id": "int",
          "name": "string",
          "state_registration": "string",
          "property_management_company": "string",
          "address_line_1": "string",
          "address_line_2": "string",
          "city": "string",
          "zipcode": "string",
          "state": { "id": "int", "name": "string" }
        } | null,
        "forms": [
          {
            "id": "int",
            "url": "string | null",
            "form_name": "string",
            "expiration_date": "datetime | null"
          }
        ],
        "images": [
          {
            "id": "int",
            "url": "string | null"
          }
        ],
        "forms_count": "int",
        "images_count": "int"
      }
    ],
    "current_page": "int",
    "page_size": "int",
    "total": "int",
    "total_pages": "int"
  }
}
```

Note: Operators see only units they created for the property.

---

# 📋 FORMS APIs

## Update Active States

```http
POST /api/forms/update-states
```

```text
Auth: Bearer Token (Super Admin role)

Request:
{
  "states": ["int"]
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Add or Edit Form Template

```http
POST /api/forms/add-edit
```

```text
Auth: Bearer Token (Super Admin role)
Content-Type: multipart/form-data

Request:
- id: int (optional — omit to create, include to edit)
- name: string (optional)
- state_id: int (optional)
- image: file (optional)

Note: state must be active to add a form to it.

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Delete Form Template

```http
POST /api/forms/delete
```

```text
Auth: Bearer Token (Super Admin role)

Request:
{
  "id": "int"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Get Forms by State

```http
GET /api/forms/get/{state_id}?current_page=&page_size=
```

```text
Auth: Bearer Token (Super Admin role)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "forms": [
      {
        "id": "int",
        "name": "string",
        "state_id": "int",
        "image": "string | null"
      }
    ],
    "current_page": "int",
    "page_size": "int",
    "total": "int",
    "total_pages": "int"
  }
}
```

---

# 💳 STRIPE APIs

## Create Stripe Customer

```http
POST /api/stripe/customers/create
```

```text
Auth: None (public)

Request:
{
  "email": "string",
  "name": "string"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {}
}
```

---

## Create Subscription Checkout Session

```http
POST /api/stripe/subscription/checkout-session
```

```text
Auth: Bearer Token (any authenticated user)

Request:
{
  "price_id": "string",
  "subscription_type_id": "int"
}

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "checkout_url": "string"
  }
}
```

---

## Stripe Webhook

```http
POST /api/stripe/subscription/webhook
```

```text
Auth: None (Stripe signature verification via stripe-signature header)

Headers:
stripe-signature: string

Request: Raw Stripe webhook payload

Handled events:
- checkout.session.completed → activates user subscription
- customer.subscription.deleted → deactivates user subscription

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Cancel Subscription

```http
POST /api/stripe/subscription/cancel
```

```text
Auth: Bearer Token (any authenticated user)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

## Get Subscription Details

```http
GET /api/stripe/subscription/details
```

```text
Auth: Bearer Token (any authenticated user)

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {
    "current_payment_method": {},
    "invoice_history": [],
    "active": "boolean",
    "pricing": {}
  }
}
```

---

## Update Payment Method

```http
GET /api/stripe/payment-method/update?payment_method_id=
```

```text
Auth: Bearer Token (any authenticated user)

Query Parameters:
- payment_method_id: string

Response:
{
  "status": "SUCCESS",
  "message": "string",
  "data": null
}
```

---

# 🔑 AUTHENTICATION

All protected endpoints require a JWT Bearer token in the Authorization header:

```text
Authorization: Bearer <access_token>
```

## Token Payload

```text
Access Token:
{
  "id": "int",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "is_subscribed": "string",
  "subscription": { "id": "int", "name": "string" },
  "role": { "id": "int", "name": "string" },
  "type": "access",
  "exp": "timestamp",
  "invited_by": "int | null"
}

Refresh Token:
Same as access token but:
- "type": "refresh"
- "uuid": "string"
```

## Roles

```text
1. Super Admin    — full system access
2. Property Manager — manages assigned properties and operators
3. Operator       — creates and manages properties and units
```

## Standard Response Format

```text
Success:
{
  "status": "SUCCESS",
  "message": "string",
  "data": {} | [] | null
}

Error:
{
  "status": "ERROR" | "UNAUTHORIZED" | "FORBIDDEN",
  "message": "string"
}
```
