"""
OAuth2 authentication implementation for enterprise features
Supports Google Workspace and Microsoft Entra ID
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 configuration
config = Config(environ=os.environ)
oauth = OAuth(config)

# OAuth2 scopes
SCOPES = {
    "pricing:read": "Read pricing information",
    "pricing:write": "Modify pricing strategies",
    "products:read": "Read product information",
    "products:write": "Manage products",
    "analytics:read": "View analytics and reports"
}

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    scope: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    
class User(BaseModel):
    id: str
    email: str
    name: str
    provider: str  # google, microsoft
    scopes: List[str] = []
    is_active: bool = True
    created_at: datetime
    last_login: datetime

class AuthManager:
    """Manages OAuth2 authentication and authorization"""
    
    def __init__(self):
        self.bearer_scheme = HTTPBearer()
        self._setup_oauth_providers()
        
    def _setup_oauth_providers(self):
        """Configure OAuth providers"""
        # Google OAuth
        if os.getenv("GOOGLE_CLIENT_ID"):
            oauth.register(
                name='google',
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                client_kwargs={
                    'scope': 'openid email profile'
                }
            )
            logger.info("Google OAuth provider configured")
        
        # Microsoft OAuth
        if os.getenv("MICROSOFT_CLIENT_ID"):
            oauth.register(
                name='microsoft',
                client_id=os.getenv("MICROSOFT_CLIENT_ID"),
                client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
                authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
                client_kwargs={
                    'scope': 'openid email profile User.Read'
                }
            )
            logger.info("Microsoft OAuth provider configured")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise credentials_exception
                
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
                
            scopes: List[str] = payload.get("scopes", [])
            token_data = TokenData(username=username, scopes=scopes)
            
        except JWTError:
            raise credentials_exception
            
        return token_data
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
        """Get current authenticated user from token"""
        token_data = self.verify_token(credentials.credentials)
        
        # In production, fetch user from database
        # For now, create a mock user
        user = User(
            id=token_data.username,
            email=token_data.username,
            name="User",
            provider="oauth",
            scopes=token_data.scopes,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
            
        return user
    
    def check_scopes(self, required_scopes: List[str]):
        """Dependency to check if user has required scopes"""
        async def scope_checker(current_user: User = Depends(self.get_current_user)):
            for scope in required_scopes:
                if scope not in current_user.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not enough permissions. Required scope: {scope}"
                    )
            return current_user
        return scope_checker
    
    def create_user_tokens(self, user_data: Dict[str, Any]) -> Token:
        """Create access and refresh tokens for user"""
        # Extract user information
        user_id = user_data.get("id", user_data.get("email"))
        scopes = user_data.get("scopes", ["pricing:read", "products:read", "analytics:read"])
        
        # Create tokens
        access_token_data = {
            "sub": user_id,
            "scopes": scopes,
            "email": user_data.get("email"),
            "name": user_data.get("name")
        }
        
        access_token = self.create_access_token(access_token_data)
        refresh_token = self.create_refresh_token({"sub": user_id})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            scope=" ".join(scopes)
        )
    
    async def handle_oauth_callback(self, provider: str, request: Request) -> Dict[str, Any]:
        """Handle OAuth callback from provider"""
        try:
            client = oauth.create_client(provider)
            token = await client.authorize_access_token(request)
            
            # Get user info from provider
            if provider == "google":
                user_info = token.get("userinfo")
            elif provider == "microsoft":
                resp = await client.get("https://graph.microsoft.com/v1.0/me", token=token)
                user_info = resp.json()
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            # Create user data
            user_data = {
                "id": user_info.get("sub", user_info.get("id")),
                "email": user_info.get("email", user_info.get("mail")),
                "name": user_info.get("name", user_info.get("displayName")),
                "provider": provider,
                "scopes": ["pricing:read", "products:read", "analytics:read"]
            }
            
            # In production, save/update user in database
            # For now, just return the data
            return user_data
            
        except Exception as e:
            logger.error(f"OAuth callback error for {provider}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth authentication failed: {str(e)}"
            )

# Global auth manager instance
auth_manager = AuthManager()

# Convenience dependencies
get_current_user = auth_manager.get_current_user
RequireScopes = auth_manager.check_scopes
