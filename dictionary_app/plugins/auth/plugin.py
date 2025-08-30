"""
Authentication Plugin for Dictionary App.
Handles user authentication via Supabase with guest mode fallback.
"""

import os
import json
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from core.plugin import Plugin

logger = logging.getLogger(__name__)

# Try to import Supabase, but allow plugin to work without it for guest mode
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Supabase not installed. Only guest mode will be available.")
    SUPABASE_AVAILABLE = False
    Client = None


class AuthPlugin(Plugin):
    """
    Authentication plugin using Supabase for account management.
    Supports guest mode for users without accounts.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.supabase: Optional[Client] = None
        self.current_user = None
        self.session_data = None
        self.guest_id = None
        self.is_premium = False
        
        # Local storage paths will be set in on_load
        self.auth_storage = None
        self.session_file = None
        self.guest_file = None
        
        # Settings
        self.settings = {
            "enable_guest_mode": True,
            "guest_search_limit": 50,
            "remember_login": True,
            "auto_login": True
        }
        
    def on_load(self):
        """Initialize authentication on plugin load."""
        logger.info("Authentication plugin loading...")
        
        # Set up storage paths now that storage_path is available
        if self.storage_path:
            self.auth_storage = Path(self.storage_path)
            self.auth_storage.mkdir(exist_ok=True, parents=True)
            self.session_file = self.auth_storage / "session.json"
            self.guest_file = self.auth_storage / "guest.json"
        else:
            # Fallback to temp directory
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "dictionary_app_auth"
            temp_dir.mkdir(exist_ok=True)
            self.auth_storage = temp_dir
            self.session_file = temp_dir / "session.json"
            self.guest_file = temp_dir / "guest.json"
        
        # Load settings (no load_settings method defined, using defaults)
        
        # Initialize Supabase if available
        if SUPABASE_AVAILABLE:
            self._init_supabase()
        
        # Try to restore session
        self._restore_session()
        
        # Register event handlers
        self.app.events.on('app.ready', self._on_app_ready)
        self.app.events.on('search.before', self._check_search_limit)
        
        # Expose auth API to other plugins
        self.app.auth = self
        
        logger.info("Authentication plugin loaded")
        
    def _init_supabase(self):
        """Initialize Supabase client."""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_ANON_KEY')
            
            if not url or not key:
                logger.warning("Supabase credentials not configured. Cloud features disabled.")
                return
                
            self.supabase = create_client(url, key)
            logger.info("Supabase client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            self.supabase = None
            
    def _restore_session(self):
        """Restore previous session from local storage."""
        # First check for saved Supabase session
        if self.settings.get('remember_login') and self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                    
                # Check if session is still valid
                if self._is_session_valid(session_data):
                    self.session_data = session_data
                    self.current_user = session_data.get('user')
                    self.is_premium = session_data.get('is_premium', False)
                    
                    # Try to refresh with Supabase if available
                    if self.supabase and self.settings.get('auto_login'):
                        self._refresh_session()
                        
                    logger.info(f"Session restored for user: {self.current_user.get('email')}")
                    return
                    
            except Exception as e:
                logger.error(f"Failed to restore session: {e}")
                
        # Fallback to guest mode
        if self.settings.get('enable_guest_mode'):
            self._init_guest_mode()
            
    def _is_session_valid(self, session_data: Dict) -> bool:
        """Check if a session is still valid."""
        if not session_data:
            return False
            
        expires_at = session_data.get('expires_at')
        if not expires_at:
            return False
            
        try:
            from datetime import datetime
            expiry = datetime.fromisoformat(expires_at)
            return datetime.now() < expiry
        except:
            return False
            
    def _init_guest_mode(self):
        """Initialize or restore guest mode."""
        try:
            if self.guest_file.exists():
                with open(self.guest_file, 'r') as f:
                    guest_data = json.load(f)
                    self.guest_id = guest_data.get('guest_id')
                    logger.info(f"Guest mode restored: {self.guest_id}")
            else:
                # Create new guest ID
                self.guest_id = str(uuid.uuid4())
                guest_data = {
                    'guest_id': self.guest_id,
                    'created_at': datetime.now().isoformat(),
                    'search_count': 0
                }
                with open(self.guest_file, 'w') as f:
                    json.dump(guest_data, f, indent=2)
                logger.info(f"New guest created: {self.guest_id}")
                
        except Exception as e:
            logger.error(f"Failed to initialize guest mode: {e}")
            
    def _on_app_ready(self):
        """Handle app ready event."""
        # Emit authentication status
        if self.is_authenticated():
            self.app.events.emit('auth.authenticated', {
                'user': self.current_user,
                'is_premium': self.is_premium
            })
        else:
            self.app.events.emit('auth.guest', {
                'guest_id': self.guest_id
            })
            
    def _check_search_limit(self, event_data):
        """Check if user has reached search limit."""
        if self.is_premium:
            return  # Premium users have unlimited searches
            
        # Get current search count
        search_count = self.get_search_count()
        limit = self.settings.get('guest_search_limit', 50)
        
        if search_count >= limit:
            # Block the search
            event_data['cancel'] = True
            event_data['reason'] = f"Free tier limit reached ({limit} searches)"
            
            # Emit event for UI to show upgrade prompt
            self.app.events.emit('auth.limit_reached', {
                'limit': limit,
                'count': search_count
            })
            
            logger.info(f"Search blocked - limit reached: {search_count}/{limit}")
            
    def get_search_count(self) -> int:
        """Get current search count for user/guest."""
        try:
            # Get from history plugin directly
            plugins = self.app.get_plugins() if hasattr(self.app, 'get_plugins') else {}
            history_plugin = plugins.get('history')
            
            if history_plugin and hasattr(history_plugin, 'search_count'):
                # History plugin tracks the total count
                return history_plugin.search_count
        except Exception as e:
            logger.debug(f"Could not get count from history: {e}")
            
        # Fallback to local count
        if self.guest_file and self.guest_file.exists():
            with open(self.guest_file, 'r') as f:
                data = json.load(f)
                return data.get('search_count', 0)
        return 0
        
    def _refresh_session(self):
        """Refresh the current session with Supabase."""
        if not self.supabase or not self.session_data:
            return
            
        try:
            # Get refresh token
            refresh_token = self.session_data.get('refresh_token')
            if not refresh_token:
                return
                
            # Refresh session
            response = self.supabase.auth.refresh_session(refresh_token)
            if response and response.session:
                self._save_session(response.session, response.user)
                logger.info("Session refreshed successfully")
                
        except Exception as e:
            logger.error(f"Failed to refresh session: {e}")
            
    def _save_session(self, session, user):
        """Save session to local storage."""
        try:
            # Check if user is premium
            is_premium = self._check_premium_status(user.id if user else None)
            
            session_data = {
                'user': {
                    'id': user.id if user else None,
                    'email': user.email if user else None,
                },
                'access_token': session.access_token if session else None,
                'refresh_token': session.refresh_token if session else None,
                'expires_at': session.expires_at if session else None,
                'is_premium': is_premium,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            self.session_data = session_data
            self.current_user = session_data['user']
            self.is_premium = is_premium
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            
    def _check_premium_status(self, user_id: str) -> bool:
        """Check if user has premium status."""
        if not self.supabase or not user_id:
            return False
            
        try:
            # Query user profile for premium status
            response = self.supabase.table('user_profiles').select('is_premium').eq('id', user_id).single().execute()
            
            if response.data:
                return response.data.get('is_premium', False)
                
        except Exception as e:
            logger.error(f"Failed to check premium status: {e}")
            
        # Check cached status
        if self.session_data:
            return self.session_data.get('is_premium', False)
            
        return False
        
    # Public API methods
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.current_user is not None
        
    def is_guest(self) -> bool:
        """Check if in guest mode."""
        return self.guest_id is not None and not self.is_authenticated()
        
    def get_user(self) -> Optional[Dict]:
        """Get current user info."""
        return self.current_user
        
    def get_guest_id(self) -> Optional[str]:
        """Get guest ID if in guest mode."""
        return self.guest_id if self.is_guest() else None
        
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login with email and password."""
        if not self.supabase:
            return {
                'success': False,
                'error': 'Authentication service not available'
            }
            
        try:
            response = self.supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if response and response.user:
                self._save_session(response.session, response.user)
                
                # Clear guest mode
                self.guest_id = None
                if self.guest_file.exists():
                    self.guest_file.unlink()
                    
                self.app.events.emit('auth.login', {
                    'user': self.current_user,
                    'is_premium': self.is_premium
                })
                
                return {
                    'success': True,
                    'user': self.current_user,
                    'is_premium': self.is_premium
                }
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def register(self, email: str, password: str) -> Dict[str, Any]:
        """Register new account."""
        if not self.supabase:
            return {
                'success': False,
                'error': 'Authentication service not available'
            }
            
        try:
            response = self.supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            
            if response and response.user:
                # Note: User may need to verify email
                return {
                    'success': True,
                    'user': response.user,
                    'requires_verification': True
                }
                
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def logout(self):
        """Logout current user."""
        try:
            # Sign out from Supabase
            if self.supabase:
                self.supabase.auth.sign_out()
                
            # Clear local session
            self.current_user = None
            self.session_data = None
            self.is_premium = False
            
            if self.session_file.exists():
                self.session_file.unlink()
                
            # Re-initialize guest mode if enabled
            if self.settings.get('enable_guest_mode'):
                self._init_guest_mode()
                
            self.app.events.emit('auth.logout')
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email."""
        if not self.supabase:
            return {
                'success': False,
                'error': 'Authentication service not available'
            }
            
        try:
            self.supabase.auth.reset_password_for_email(email)
            return {
                'success': True,
                'message': 'Password reset email sent'
            }
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def on_unload(self):
        """Cleanup on plugin unload."""
        logger.info("Authentication plugin unloading...")
        
        # Remove from app
        if hasattr(self.app, 'auth'):
            delattr(self.app, 'auth')