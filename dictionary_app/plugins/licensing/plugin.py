"""
Licensing Plugin - Manages free tier limits and premium licenses
"""

import os
import json
import sqlite3
import hashlib
import platform
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from core.plugin import Plugin

logger = logging.getLogger(__name__)

class LicensingPlugin(Plugin):
    """Manages free tier limits, premium licenses, and payment processing."""
    
    def __init__(self, app):
        super().__init__(app)
        self.db_path = None
        self.conn = None
        self.is_premium = False
        self.search_count = 0
        self.license_data = {}
        self.device_id = None
        self.stripe_session = None
        
    def on_load(self):
        """Initialize licensing system."""
        super().on_load()
        logger.info("Loading licensing plugin...")
        
        # Set up storage path
        storage_dir = Path(self.app.config.get('paths.plugin_storage', 'data/plugin-storage'))
        self.storage_path = storage_dir / 'licensing'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.storage_path / 'licensing.db'
        self._init_database()
        
        # Generate device ID
        self.device_id = self._generate_device_id()
        
        # Load license status
        self._load_license_status()
        
        # Register event listeners
        from core.events import EventPriority
        self.app.events.on('search.before', self._on_before_search, priority=EventPriority.HIGH)
        self.app.events.on('auth.login', self._on_user_login)
        self.app.events.on('auth.logout', self._on_user_logout)
        
        # Check if we need to validate online
        self._check_online_validation()
        
        logger.info(f"Licensing plugin loaded. Premium: {self.is_premium}, Search count: {self.search_count}")
        
    def on_enable(self):
        """Called when plugin is enabled."""
        super().on_enable()
        logger.info("Licensing plugin enabled")
        
    def on_disable(self):
        """Called when plugin is disabled."""
        super().on_disable()
        logger.info("Licensing plugin disabled")
        
        # Close database
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def _init_database(self):
        """Initialize licensing database."""
        if not self.db_path:
            return
            
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()
        
        # License status table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS license_status (
                id INTEGER PRIMARY KEY,
                is_premium BOOLEAN DEFAULT 0,
                license_key TEXT,
                user_id TEXT,
                activated_at TIMESTAMP,
                last_validated TIMESTAMP,
                expires_at TIMESTAMP,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT
            )
        """)
        
        # Device activations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_activations (
                device_id TEXT PRIMARY KEY,
                hardware_fingerprint TEXT,
                device_name TEXT,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Purchase history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stripe_session_id TEXT UNIQUE,
                amount REAL,
                currency TEXT,
                product_type TEXT,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        self.conn.commit()
        
    def _generate_device_id(self) -> str:
        """Generate unique device ID from hardware info."""
        try:
            # Combine various hardware identifiers
            identifiers = []
            
            # Platform info
            identifiers.append(platform.node())
            identifiers.append(platform.machine())
            identifiers.append(platform.processor())
            
            # Try to get MAC address
            import uuid
            mac = uuid.getnode()
            identifiers.append(str(mac))
            
            # Create hash
            combined = '|'.join(identifiers)
            device_id = hashlib.sha256(combined.encode()).hexdigest()[:16]
            
            return device_id
            
        except Exception as e:
            logger.error(f"Error generating device ID: {e}")
            # Fallback to random ID
            import uuid
            return str(uuid.uuid4())[:16]
            
    def _load_license_status(self):
        """Load license status from database."""
        try:
            cursor = self.conn.cursor()
            
            # Get license status
            cursor.execute("SELECT * FROM license_status ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                self.is_premium = bool(row[1])  # is_premium
                self.license_data = {
                    'license_key': row[2],
                    'user_id': row[3],
                    'activated_at': row[4],
                    'last_validated': row[5],
                    'expires_at': row[6],
                    'stripe_customer_id': row[7],
                    'stripe_subscription_id': row[8]
                }
            else:
                # Initialize default status
                cursor.execute("""
                    INSERT INTO license_status (is_premium, last_validated)
                    VALUES (0, datetime('now'))
                """)
                self.conn.commit()
                
            # Get search count from history plugin if available
            if hasattr(self.app, 'plugins') and 'history' in self.app.plugins:
                history_plugin = self.app.plugins['history']
                if hasattr(history_plugin, 'get_search_count'):
                    self.search_count = history_plugin.get_search_count()
                    
        except Exception as e:
            logger.error(f"Error loading license status: {e}")
            
    def _check_online_validation(self):
        """Check if we need to validate license online."""
        if not self.is_premium:
            return
            
        last_validated = self.license_data.get('last_validated')
        if not last_validated:
            return
            
        try:
            # Parse timestamp
            if isinstance(last_validated, str):
                last_check = datetime.fromisoformat(last_validated)
            else:
                last_check = last_validated
                
            # Check every 7 days
            check_interval = self.app.config.get('licensing.license_check_interval', 604800)
            if (datetime.now() - last_check).total_seconds() > check_interval:
                self._validate_license_online()
                
        except Exception as e:
            logger.error(f"Error checking validation schedule: {e}")
            
    def _on_before_search(self, event_data):
        """Intercept searches to enforce limits."""
        # Check if enforcement is enabled
        if not self.app.config.get('licensing.enforce_limit', True):
            return
            
        # Premium users have no limits
        if self.is_premium:
            return
            
        # Check search count
        free_limit = self.app.config.get('licensing.free_tier_limit', 50)
        
        # Get current count from history plugin
        if hasattr(self.app.plugin_loader, 'plugins') and 'history' in self.app.plugin_loader.plugins:
            history_plugin = self.app.plugin_loader.plugins['history']
            if hasattr(history_plugin, 'get_search_count'):
                self.search_count = history_plugin.get_search_count()
                
        if self.search_count >= free_limit:
            # Block the search
            logger.info(f"Search blocked: Free tier limit reached ({self.search_count}/{free_limit})")
            
            # Mark search as cancelled in the event data
            if isinstance(event_data, dict):
                event_data['cancelled'] = True
                event_data['reason'] = 'free_tier_limit'
            
            # Show upgrade prompt
            self._show_upgrade_prompt()
            
    def _on_user_login(self, event_data):
        """Handle user login - check premium status."""
        user_data = event_data.get('user', {})
        user_id = user_data.get('id')
        
        if not user_id:
            return
            
        # Check if user has premium from auth plugin
        if hasattr(self.app, 'auth'):
            auth_plugin = self.app.auth
            if hasattr(auth_plugin, 'is_premium'):
                self.is_premium = auth_plugin.is_premium()
                
        # Update database
        self._update_premium_status(user_id)
        
    def _on_user_logout(self, event_data):
        """Handle user logout - revert to free tier."""
        self.is_premium = False
        self.license_data = {}
        
        # Update database
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE license_status 
            SET is_premium = 0, user_id = NULL
            WHERE id = (SELECT MAX(id) FROM license_status)
        """)
        self.conn.commit()
        
    def _update_premium_status(self, user_id: str):
        """Update premium status in database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE license_status 
                SET is_premium = ?, user_id = ?, last_validated = datetime('now')
                WHERE id = (SELECT MAX(id) FROM license_status)
            """, (int(self.is_premium), user_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating premium status: {e}")
            
    def _validate_license_online(self):
        """Validate license with Supabase."""
        try:
            # Check with auth plugin for premium status
            if hasattr(self.app, 'auth'):
                auth_plugin = self.app.auth
                if hasattr(auth_plugin, 'check_premium_status'):
                    is_valid = auth_plugin.check_premium_status()
                    
                    if is_valid != self.is_premium:
                        self.is_premium = is_valid
                        self._update_premium_status(auth_plugin.get_user_id())
                        
                    # Update last validated time
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        UPDATE license_status 
                        SET last_validated = datetime('now')
                        WHERE id = (SELECT MAX(id) FROM license_status)
                    """)
                    self.conn.commit()
                    
        except Exception as e:
            logger.error(f"Error validating license online: {e}")
            
    def _show_upgrade_prompt(self):
        """Show upgrade prompt when limit is reached."""
        try:
            # Import tkinter for UI
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            # Create upgrade window
            window = tk.Toplevel()
            window.title("Upgrade to Premium")
            window.geometry("450x350")
            window.resizable(False, False)
            
            # Center window
            window.update_idletasks()
            x = (window.winfo_screenwidth() // 2) - (450 // 2)
            y = (window.winfo_screenheight() // 2) - (350 // 2)
            window.geometry(f"450x350+{x}+{y}")
            
            # Header
            header = ttk.Label(
                window,
                text="Free Search Limit Reached",
                font=('Arial', 16, 'bold')
            )
            header.pack(pady=20)
            
            # Message
            message = ttk.Label(
                window,
                text=f"You've used all {self.app.config.get('licensing.free_tier_limit', 50)} free searches.\n\n"
                     "Upgrade to Premium for unlimited searches,\n"
                     "advanced features, and priority support.",
                font=('Arial', 11),
                justify='center'
            )
            message.pack(pady=10)
            
            # Price
            price_frame = ttk.Frame(window)
            price_frame.pack(pady=20)
            
            price_label = ttk.Label(
                price_frame,
                text="$20",
                font=('Arial', 24, 'bold')
            )
            price_label.pack(side='left')
            
            price_desc = ttk.Label(
                price_frame,
                text=" one-time payment\n lifetime license",
                font=('Arial', 10)
            )
            price_desc.pack(side='left', padx=5)
            
            # Benefits
            benefits_frame = ttk.LabelFrame(window, text="Premium Benefits", padding=10)
            benefits_frame.pack(fill='x', padx=20, pady=10)
            
            benefits = [
                "✓ Unlimited dictionary searches",
                "✓ Access to premium extensions",
                "✓ Use on up to 3 devices",
                "✓ Priority customer support"
            ]
            
            for benefit in benefits:
                ttk.Label(benefits_frame, text=benefit, font=('Arial', 10)).pack(anchor='w')
                
            # Buttons
            button_frame = ttk.Frame(window)
            button_frame.pack(pady=20)
            
            def upgrade():
                window.destroy()
                self.start_purchase_flow()
                
            upgrade_btn = ttk.Button(
                button_frame,
                text="Upgrade Now",
                command=upgrade,
                style='Accent.TButton'
            )
            upgrade_btn.pack(side='left', padx=5)
            
            ttk.Button(
                button_frame,
                text="Maybe Later",
                command=window.destroy
            ).pack(side='left', padx=5)
            
            # Make window modal
            window.transient()
            window.grab_set()
            
        except ImportError:
            logger.error("Tkinter not available for upgrade prompt")
        except Exception as e:
            logger.error(f"Error showing upgrade prompt: {e}")
            
    def start_purchase_flow(self):
        """Start Stripe checkout flow."""
        try:
            stripe_key = self.app.config.get('licensing.stripe_publishable_key')
            price_id = self.app.config.get('licensing.stripe_price_id')
            
            if not stripe_key or not price_id:
                logger.warning("Stripe not configured. Opening demo purchase page.")
                webbrowser.open("https://stripe.com/docs/testing")
                return
                
            # Import stripe
            try:
                import stripe
                stripe.api_key = stripe_key
                
                # Create checkout session
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': price_id,
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=self.app.config.get('licensing.stripe_success_url', 'http://localhost:8000/success'),
                    cancel_url=self.app.config.get('licensing.stripe_cancel_url', 'http://localhost:8000/cancel'),
                    metadata={
                        'device_id': self.device_id,
                        'user_id': self._get_current_user_id()
                    }
                )
                
                # Save session ID
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO purchases (stripe_session_id, amount, currency, product_type, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (session.id, 20.00, 'USD', 'core_app', 'pending'))
                self.conn.commit()
                
                # Open checkout in browser
                webbrowser.open(session.url)
                
                # Start polling for completion
                self._poll_payment_status(session.id)
                
            except ImportError:
                logger.warning("Stripe library not installed. Opening demo page.")
                webbrowser.open("https://stripe.com/docs/testing")
                
        except Exception as e:
            logger.error(f"Error starting purchase flow: {e}")
            
    def _get_current_user_id(self) -> Optional[str]:
        """Get current user ID from auth plugin."""
        if hasattr(self.app, 'auth'):
            auth_plugin = self.app.auth
            if hasattr(auth_plugin, 'get_user_id'):
                return auth_plugin.get_user_id()
        return None
        
    def _poll_payment_status(self, session_id: str):
        """Poll for payment completion."""
        # This would normally poll Stripe API
        # For now, we'll simulate with a timer
        import threading
        
        def check_status():
            import time
            time.sleep(5)  # Wait 5 seconds
            
            # In production, check Stripe session status
            # For demo, just activate premium
            logger.info("Demo: Activating premium license")
            self.activate_premium_license({
                'user_id': self._get_current_user_id(),
                'stripe_session_id': session_id
            })
            
        thread = threading.Thread(target=check_status, daemon=True)
        thread.start()
        
    def activate_premium_license(self, purchase_data: Dict[str, Any]):
        """Activate premium license after successful payment."""
        try:
            self.is_premium = True
            
            # Update database
            cursor = self.conn.cursor()
            
            # Update license status
            cursor.execute("""
                UPDATE license_status 
                SET is_premium = 1,
                    user_id = ?,
                    activated_at = datetime('now'),
                    last_validated = datetime('now'),
                    stripe_customer_id = ?
                WHERE id = (SELECT MAX(id) FROM license_status)
            """, (purchase_data.get('user_id'), purchase_data.get('stripe_customer_id')))
            
            # Update purchase status
            if purchase_data.get('stripe_session_id'):
                cursor.execute("""
                    UPDATE purchases 
                    SET status = 'completed'
                    WHERE stripe_session_id = ?
                """, (purchase_data['stripe_session_id'],))
                
            # Register device
            cursor.execute("""
                INSERT OR REPLACE INTO device_activations (device_id, hardware_fingerprint, device_name)
                VALUES (?, ?, ?)
            """, (self.device_id, self.device_id, platform.node()))
            
            self.conn.commit()
            
            # Emit event
            self.app.events.emit('license.activated', {
                'user_id': purchase_data.get('user_id'),
                'device_id': self.device_id
            })
            
            # Show success message
            self._show_activation_success()
            
            logger.info("Premium license activated successfully")
            
        except Exception as e:
            logger.error(f"Error activating license: {e}")
            
    def _show_activation_success(self):
        """Show success message after activation."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showinfo(
                "License Activated",
                "Thank you for purchasing Dictionary App Premium!\n\n"
                "You now have unlimited searches and access to all premium features.\n\n"
                "Enjoy using Dictionary App!"
            )
            
            root.destroy()
            
        except Exception as e:
            logger.error(f"Error showing success message: {e}")
            
    # Public API methods
    
    def is_premium_user(self) -> bool:
        """Check if current user has premium license."""
        return self.is_premium
        
    def get_search_count(self) -> int:
        """Get current search count."""
        return self.search_count
        
    def get_search_limit(self) -> int:
        """Get free tier search limit."""
        return self.app.config.get('licensing.free_tier_limit', 50)
        
    def get_remaining_searches(self) -> int:
        """Get remaining free searches."""
        if self.is_premium:
            return -1  # Unlimited
        return max(0, self.get_search_limit() - self.search_count)
        
    def check_device_limit(self) -> bool:
        """Check if device limit is reached."""
        if not self.is_premium:
            return True
            
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM device_activations")
            count = cursor.fetchone()[0]
            
            max_devices = self.app.config.get('licensing.max_devices', 3)
            return count < max_devices
            
        except Exception as e:
            logger.error(f"Error checking device limit: {e}")
            return True