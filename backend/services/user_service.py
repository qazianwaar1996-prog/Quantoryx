# backend/services/user_service.py
"""
Quantoryx — User Service & Persistence Module.

This module implements a thread-safe, JSON-persisted repository layer
managing user profiles, hashed credentials, and revoked refresh tokens,
ensuring persistence across API server reloads and restarts.
"""

import json
import os
import uuid
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

from backend.schemas.auth_schemas import (
    PasswordChangeRequest,
    UserProfileUpdateRequest,
    UserRegisterRequest
)
from backend.services.security_service import SecurityService
from utils.logging_config import get_logger
from utils.path_manager import PathManager

# Initialize centralized logger
logger = get_logger("backend.services.user")

# Thread-safe write lock for JSON database synchronization
_DB_LOCK = Lock()


class UserService:
    """
    Lightweight user database repository and profile manager.
    Persists records to data/users.json, serving as a swappable data layer.
    """

    @classmethod
    def _get_db_path(cls) -> str:
        """Resolves the standard database storage location via PathManager."""
        return PathManager.resolve_path("data", "users.json")

    @classmethod
    def _read_db(cls) -> Dict[str, Dict[str, Any]]:
        """Reads and loads the raw user records dictionary from disk."""
        db_path = cls._get_db_path()
        if not os.path.exists(db_path):
            return {}
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to read user persistence database: %s", str(e))
            return {}

    @classmethod
    def _write_db(cls, data: Dict[str, Dict[str, Any]]) -> bool:
        """Saves user records atomically and safely to disk using a write lock."""
        db_path = cls._get_db_path()
        with _DB_LOCK:
            try:
                # Write to temp file first to prevent corruption on unexpected crashes
                temp_path = f"{db_path}.tmp"
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                os.replace(temp_path, db_path)
                return True
            except Exception as e:
                logger.error("Failed to write user persistence database: %s", str(e))
                return False

    @classmethod
    def register_user(cls, request: UserRegisterRequest) -> Optional[Dict[str, Any]]:
        """
        Registers a new user profile with secure hashed password credentials.
        Returns the clean user dictionary, or None if username or email is already taken.
        """
        db = cls._read_db()

        # Enforce unique credential checks
        username_lower = request.username.lower()
        email_lower = request.email.lower()

        for user in db.values():
            if user["username"].lower() == username_lower:
                logger.warning("Registration rejected: username '%s' is already taken.", request.username)
                return None
            if user["email"].lower() == email_lower:
                logger.warning("Registration rejected: email '%s' is already registered.", request.email)
                return None

        # Secure password hashing via SecurityService
        hashed_pw = SecurityService.hash_password(request.password)
        user_id = str(uuid.uuid4())

        new_user = {
            "id": user_id,
            "username": request.username,
            "email": request.email,
            "hashed_password": hashed_pw,
            "full_name": request.full_name,
            "role": request.role.lower(),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "revoked_tokens": []
        }

        db[user_id] = new_user
        if cls._write_db(db):
            logger.info("User registered successfully. ID: %s | Username: %s", user_id, request.username)
            return cls._clean_user_record(new_user)
        return None

    @classmethod
    def authenticate_user(cls, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticates username/email credentials and verifies hashed passwords.
        Returns the user dictionary if verified, or None if authentication fails.
        """
        db = cls._read_db()
        search_term = username_or_email.lower()

        for user in db.values():
            if user["username"].lower() == search_term or user["email"].lower() == search_term:
                # Verify password against active hash
                if SecurityService.verify_password(password, user["hashed_password"]):
                    if not user["is_active"]:
                        logger.warning("Authentication rejected: User profile '%s' is inactive.", user["username"])
                        return None
                    return cls._clean_user_record(user)

        logger.warning("Authentication failed: invalid credentials for identifier '%s'.", username_or_email)
        return None

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single user profile from disk matching a target ID."""
        db = cls._read_db()
        user = db.get(user_id)
        return cls._clean_user_record(user) if user else None

    @classmethod
    def get_user_by_username(cls, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user profile from disk matching a target username."""
        db = cls._read_db()
        target = username.lower()
        for user in db.values():
            if user["username"].lower() == target:
                return cls._clean_user_record(user)
        return None

    @classmethod
    def update_user_profile(cls, user_id: str, update_request: UserProfileUpdateRequest) -> Optional[Dict[str, Any]]:
        """
        Modifies target communication and metadata elements of a user profile.
        Returns the updated user record, or None if update fails or email collides.
        """
        db = cls._read_db()
        user = db.get(user_id)
        if not user:
            return None

        # Check for unique email collisions if modified
        if update_request.email:
            new_email = update_request.email.lower()
            if new_email != user["email"].lower():
                for other_user in db.values():
                    if other_user["id"] != user_id and other_user["email"].lower() == new_email:
                        logger.warning("Profile update rejected: email '%s' is already taken.", update_request.email)
                        return None
                user["email"] = update_request.email

        if update_request.full_name is not None:
            user["full_name"] = update_request.full_name

        db[user_id] = user
        if cls._write_db(db):
            logger.info("User profile updated successfully. ID: %s", user_id)
            return cls._clean_user_record(user)
        return None

    @classmethod
    def change_user_password(cls, user_id: str, change_request: PasswordChangeRequest) -> bool:
        """
        Verifies old password credentials and commits new hashed target passwords.
        """
        db = cls._read_db()
        user = db.get(user_id)
        if not user:
            return False

        # Verify previous active credentials
        if not SecurityService.verify_password(change_request.old_password, user["hashed_password"]):
            logger.warning("Password update rejected: invalid old password provided.")
            return False

        # Apply and save target hashed password
        user["hashed_password"] = SecurityService.hash_password(change_request.new_password)
        db[user_id] = user
        return cls._write_db(db)

    @classmethod
    def revoke_refresh_token(cls, user_id: str, refresh_token: str) -> None:
        """Saves a refresh token to the revoked token listing of a target user."""
        db = cls._read_db()
        user = db.get(user_id)
        if user:
            if "revoked_tokens" not in user:
                user["revoked_tokens"] = []
            if refresh_token not in user["revoked_tokens"]:
                user["revoked_tokens"].append(refresh_token)
                db[user_id] = user
                cls._write_db(db)
                logger.debug("Refresh token revoked successfully for user ID: %s", user_id)

    @classmethod
    def is_refresh_token_revoked(cls, user_id: str, refresh_token: str) -> bool:
        """Validates if a target refresh token has been logged as revoked."""
        db = cls._read_db()
        user = db.get(user_id)
        if not user:
            return True
        return refresh_token in user.get("revoked_tokens", [])

    @staticmethod
    def _clean_user_record(user_record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Helper returning a copy of user records excluding sensitivehashed credentials.
        """
        if not user_record:
            return None
        cleaned = user_record.copy()
        cleaned.pop("hashed_password", None)
        return cleaned
