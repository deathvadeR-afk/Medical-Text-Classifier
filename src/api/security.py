"""
Security configuration and utilities for the Medical Text Classification API.
"""
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Security configuration
class SecurityConfig:
    """Security configuration class."""
    
    def __init__(self):
        # JWT Configuration
        self.SECRET_KEY = os.getenv("SECRET_KEY", self._generate_secret_key())
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # API Key Configuration
        self.API_KEYS = self._load_api_keys()
        self.REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
        
        # Rate Limiting Configuration - relaxed for testing
        is_testing = os.getenv('TESTING', 'false').lower() == 'true'
        default_requests = "10000" if is_testing else "100"
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", default_requests))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        
        # CORS Configuration
        self.ALLOWED_ORIGINS = self._load_allowed_origins()
        self.ALLOWED_HOSTS = self._load_allowed_hosts()
        
        # Security Headers
        self.ENABLE_SECURITY_HEADERS = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
        
        # Input Validation
        self.MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
        self.MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", "1"))
        
        # Logging
        self.LOG_REQUESTS = os.getenv("LOG_REQUESTS", "true").lower() == "true"
        self.LOG_SENSITIVE_DATA = os.getenv("LOG_SENSITIVE_DATA", "false").lower() == "true"
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)
    
    def _load_api_keys(self) -> List[str]:
        """Load API keys from environment."""
        api_keys_str = os.getenv("API_KEYS", "")
        if api_keys_str:
            return [key.strip() for key in api_keys_str.split(",") if key.strip()]
        return []
    
    def _load_allowed_origins(self) -> List[str]:
        """Load allowed CORS origins from environment."""
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
        if origins_str == "*":
            return ["*"]
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    def _load_allowed_hosts(self) -> List[str]:
        """Load allowed hosts from environment."""
        is_testing = os.getenv('TESTING', 'false').lower() == 'true'
        default_hosts = "localhost,127.0.0.1,testserver,host.docker.internal" if is_testing else "localhost,127.0.0.1,host.docker.internal"
        hosts_str = os.getenv("ALLOWED_HOSTS", default_hosts)
        return [host.strip() for host in hosts_str.split(",") if host.strip()]


# Global security config instance
security_config = SecurityConfig()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer(auto_error=False)


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=security_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security_config.SECRET_KEY, algorithm=security_config.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, security_config.SECRET_KEY, algorithms=[security_config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


def verify_api_key(api_key: str) -> bool:
    """Verify an API key."""
    if not security_config.API_KEYS:
        return True  # No API keys configured, allow access
    return api_key in security_config.API_KEYS


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get current user from JWT token."""
    if not credentials:
        if security_config.REQUIRE_API_KEY:
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def verify_api_key_header(request: Request):
    """Verify API key from header."""
    if not security_config.REQUIRE_API_KEY:
        return True
    
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Please provide X-API-Key header."
        )
    
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True


def sanitize_text_input(text: str) -> str:
    """Sanitize text input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    if len(text) > security_config.MAX_TEXT_LENGTH:
        text = text[:security_config.MAX_TEXT_LENGTH]
    
    # Strip whitespace
    text = text.strip()
    
    return text


def validate_text_input(text: str) -> str:
    """Validate and sanitize text input."""
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text input is required"
        )
    
    sanitized_text = sanitize_text_input(text)
    
    if len(sanitized_text) < security_config.MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text must be at least {security_config.MIN_TEXT_LENGTH} characters long"
        )
    
    if len(sanitized_text) > security_config.MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text must be no more than {security_config.MAX_TEXT_LENGTH} characters long"
        )
    
    return sanitized_text


def log_security_event(event_type: str, details: Dict[str, Any], request: Request = None):
    """Log security-related events."""
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details
    }
    
    if request:
        log_data.update({
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "endpoint": str(request.url.path),
            "method": request.method
        })
    
    logger.warning(f"Security Event: {log_data}")
