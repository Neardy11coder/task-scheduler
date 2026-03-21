import os
import bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def create_users_table():
    """Run this once in Supabase SQL editor to create users table."""
    pass


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def sign_up(username: str, email: str, password: str) -> dict:
    """Register a new user."""
    existing = supabase.table("users").select("*").eq(
        "username", username
    ).execute()

    if existing.data:
        return {"success": False, "error": "Username already taken"}

    email_check = supabase.table("users").select("*").eq(
        "email", email
    ).execute()

    if email_check.data:
        return {"success": False, "error": "Email already registered"}

    hashed = hash_password(password)
    result = supabase.table("users").insert({
        "username": username,
        "email":    email,
        "password": hashed
    }).execute()

    if result.data:
        return {"success": True, "user": result.data[0]}
    return {"success": False, "error": "Registration failed"}


def sign_in(username: str, password: str) -> dict:
    """Log in an existing user."""
    result = supabase.table("users").select("*").eq(
        "username", username
    ).execute()

    if not result.data:
        return {"success": False, "error": "Username not found"}

    user = result.data[0]
    if not verify_password(password, user["password"]):
        return {"success": False, "error": "Incorrect password"}

    return {"success": True, "user": user}