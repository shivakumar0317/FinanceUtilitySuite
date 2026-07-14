Authentication System v1.5.1

Copy files into your backend project.

Update:
- backend/models/__init__.py
    from backend.models.user import User
- backend/main.py
    from backend.api.auth_routes import router as auth_router
    app.include_router(auth_router)
- requirements-web.txt
    passlib[bcrypt]>=1.7
    python-jose[cryptography]>=3.3
    email-validator>=2.2

APIs:
POST /auth/register
POST /auth/login
GET /auth/me
