# modules/auth/application/use_cases.py

# auth has no use cases of its own at MVP.
# Login and registration logic lives in modules/users/application/use_cases.py.
# Auth module owns: OTP issuance, token refresh, logout (all future).
# Do not import SQLAlchemy, FastAPI, or infrastructure models here.