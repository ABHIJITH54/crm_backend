
---

### 🚀 `backend/README.md`

# Django Admin Dashboard Backend (DRF)

This is the **backend API** built with **Django** and **Django REST Framework**.  

It powers the React frontend by handling authentication, permissions, CRUD operations, and file uploads.

---

## 🚀 Live API
👉 [Backend Live](https://crm-backend-2-qahf.onrender.com)

---

---

## 📋 API Documentation
When running, API docs are available at:
- Swagger UI: [https://your-backend-url.com/docs/](https://your-backend-url.com/docs/)
- 
- OpenAPI JSON: [https://your-backend-url.com/openapi/](https://your-backend-url.com/openapi/)

Key Endpoints:

| Resource    | Endpoint             |
|-------------|----------------------|
| Auth        | `/api/auth/`         |
| Staff       | `/api/staff/`        |
| Managers    | `/api/managers/`     |
| Customers   | `/api/customers/`    |
| Departments | `/api/departments/`  |

---

### Admin credentials

username==>   abhijithms216@gmail.com

password==>   Abhijithabhi@808933


### 1. Clone & Setup

git clone https://github.com/ABHIJITH54/crm_backend.git


cd crm_backend


python -m venv crm_backend


.\crm_backend\Scripts\activate


cd crm_project


python manage.py makemigrations


python manage.py migrate


python manage.py runserver


pip install -r requirements.txt
