"""
Authentication UI for Dictionary App.
Provides login, register, and account management windows.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from typing import Optional, Callable


class AuthWindow:
    """Main authentication window with login/register tabs."""
    
    def __init__(self, auth_plugin, on_success: Optional[Callable] = None):
        self.auth = auth_plugin
        self.on_success = on_success
        self.window = None
        
    def show(self):
        """Show the authentication window."""
        if self.window and self.window.winfo_exists():
            self.window.focus()
            return
            
        self.window = tk.Toplevel()
        self.window.title("Dictionary App - Sign In")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"400x500+{x}+{y}")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create tabs
        self._create_login_tab()
        self._create_register_tab()
        self._create_guest_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Check current status
        self._update_status()
        
    def _create_login_tab(self):
        """Create login tab."""
        login_frame = ttk.Frame(self.notebook)
        self.notebook.add(login_frame, text="Sign In")
        
        # Logo/Title
        title = ttk.Label(login_frame, text="Welcome Back!", 
                         font=('Helvetica', 18, 'bold'))
        title.pack(pady=30)
        
        # Email field
        ttk.Label(login_frame, text="Email:").pack(anchor='w', padx=50, pady=(20, 5))
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(login_frame, textvariable=self.email_var, width=30)
        email_entry.pack(padx=50)
        
        # Password field
        ttk.Label(login_frame, text="Password:").pack(anchor='w', padx=50, pady=(20, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, 
                                  width=30, show="*")
        password_entry.pack(padx=50)
        
        # Remember me checkbox
        self.remember_var = tk.BooleanVar(value=True)
        remember_cb = ttk.Checkbutton(login_frame, text="Remember me", 
                                      variable=self.remember_var)
        remember_cb.pack(pady=20)
        
        # Login button
        login_btn = ttk.Button(login_frame, text="Sign In", 
                              command=self._handle_login)
        login_btn.pack(pady=10)
        
        # Forgot password link
        forgot_btn = ttk.Button(login_frame, text="Forgot Password?", 
                               command=self._show_reset_password)
        forgot_btn.pack(pady=10)
        
        # OAuth providers
        ttk.Separator(login_frame, orient='horizontal').pack(fill='x', padx=50, pady=20)
        ttk.Label(login_frame, text="Or sign in with:").pack()
        
        oauth_frame = ttk.Frame(login_frame)
        oauth_frame.pack(pady=10)
        
        ttk.Button(oauth_frame, text="Google", width=10,
                  command=lambda: self._handle_oauth('google')).pack(side=tk.LEFT, padx=5)
        ttk.Button(oauth_frame, text="GitHub", width=10,
                  command=lambda: self._handle_oauth('github')).pack(side=tk.LEFT, padx=5)
        
    def _create_register_tab(self):
        """Create register tab."""
        register_frame = ttk.Frame(self.notebook)
        self.notebook.add(register_frame, text="Sign Up")
        
        # Title
        title = ttk.Label(register_frame, text="Create Account", 
                         font=('Helvetica', 18, 'bold'))
        title.pack(pady=30)
        
        # Email field
        ttk.Label(register_frame, text="Email:").pack(anchor='w', padx=50, pady=(20, 5))
        self.reg_email_var = tk.StringVar()
        email_entry = ttk.Entry(register_frame, textvariable=self.reg_email_var, width=30)
        email_entry.pack(padx=50)
        
        # Password field
        ttk.Label(register_frame, text="Password:").pack(anchor='w', padx=50, pady=(20, 5))
        self.reg_password_var = tk.StringVar()
        password_entry = ttk.Entry(register_frame, textvariable=self.reg_password_var, 
                                  width=30, show="*")
        password_entry.pack(padx=50)
        
        # Confirm password field
        ttk.Label(register_frame, text="Confirm Password:").pack(anchor='w', padx=50, pady=(20, 5))
        self.reg_confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(register_frame, textvariable=self.reg_confirm_var, 
                                 width=30, show="*")
        confirm_entry.pack(padx=50)
        
        # Terms checkbox
        self.terms_var = tk.BooleanVar()
        terms_cb = ttk.Checkbutton(register_frame, 
                                   text="I agree to the Terms of Service", 
                                   variable=self.terms_var)
        terms_cb.pack(pady=20)
        
        # Register button
        register_btn = ttk.Button(register_frame, text="Create Account", 
                                 command=self._handle_register)
        register_btn.pack(pady=10)
        
        # Benefits text
        benefits = ttk.Label(register_frame, 
                           text="✓ Unlimited searches\n✓ Sync across devices\n✓ Export favorites\n✓ Priority support",
                           justify=tk.LEFT)
        benefits.pack(pady=20)
        
    def _create_guest_tab(self):
        """Create guest mode tab."""
        guest_frame = ttk.Frame(self.notebook)
        self.notebook.add(guest_frame, text="Guest Mode")
        
        # Title
        title = ttk.Label(guest_frame, text="Try as Guest", 
                         font=('Helvetica', 18, 'bold'))
        title.pack(pady=30)
        
        # Guest info
        if self.auth.is_guest():
            search_count = self.auth.get_search_count()
            limit = self.auth.settings.get('guest_search_limit', 50)
            
            info_text = f"Guest ID: {self.auth.get_guest_id()[:8]}...\n\n"
            info_text += f"Searches used: {search_count} / {limit}\n\n"
            
            if search_count >= limit:
                info_text += "⚠️ You've reached the free tier limit.\n"
                info_text += "Sign up for unlimited searches!"
            else:
                remaining = limit - search_count
                info_text += f"✓ {remaining} searches remaining"
                
        else:
            info_text = "Continue without an account\n\n"
            info_text += "Guest mode limitations:\n"
            info_text += "• 50 searches per device\n"
            info_text += "• No sync across devices\n"
            info_text += "• No favorites export\n"
            
        info_label = ttk.Label(guest_frame, text=info_text, justify=tk.CENTER)
        info_label.pack(pady=20)
        
        # Continue as guest button
        if not self.auth.is_authenticated():
            guest_btn = ttk.Button(guest_frame, text="Continue as Guest", 
                                  command=self._handle_guest)
            guest_btn.pack(pady=20)
            
        # Upgrade button if limit reached
        if self.auth.is_guest():
            search_count = self.auth.get_search_count()
            limit = self.auth.settings.get('guest_search_limit', 50)
            
            if search_count >= limit:
                upgrade_btn = ttk.Button(guest_frame, text="Upgrade Now - $20", 
                                       command=self._show_upgrade)
                upgrade_btn.pack(pady=10)
                
    def _update_status(self):
        """Update status bar."""
        if self.auth.is_authenticated():
            user = self.auth.get_user()
            status = f"Signed in as: {user.get('email')}"
            if self.auth.is_premium:
                status += " (Premium)"
        elif self.auth.is_guest():
            status = f"Guest mode (ID: {self.auth.get_guest_id()[:8]}...)"
        else:
            status = "Not signed in"
            
        self.status_var.set(status)
        
    def _handle_login(self):
        """Handle login button click."""
        email = self.email_var.get().strip()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
            
        # Run async login
        asyncio.create_task(self._async_login(email, password))
        
    async def _async_login(self, email: str, password: str):
        """Async login handler."""
        self.status_var.set("Signing in...")
        
        result = await self.auth.login(email, password)
        
        if result['success']:
            self.status_var.set("Login successful!")
            messagebox.showinfo("Success", f"Welcome back, {email}!")
            
            if self.on_success:
                self.on_success()
                
            self.window.destroy()
        else:
            self.status_var.set("Login failed")
            messagebox.showerror("Login Failed", result.get('error', 'Unknown error'))
            
    def _handle_register(self):
        """Handle register button click."""
        email = self.reg_email_var.get().strip()
        password = self.reg_password_var.get()
        confirm = self.reg_confirm_var.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter email and password")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please agree to the Terms of Service")
            return
            
        # Run async register
        asyncio.create_task(self._async_register(email, password))
        
    async def _async_register(self, email: str, password: str):
        """Async register handler."""
        self.status_var.set("Creating account...")
        
        result = await self.auth.register(email, password)
        
        if result['success']:
            self.status_var.set("Registration successful!")
            
            if result.get('requires_verification'):
                messagebox.showinfo("Verify Email", 
                                  "Please check your email to verify your account.")
            else:
                messagebox.showinfo("Success", "Account created successfully!")
                
            # Switch to login tab
            self.notebook.select(0)
        else:
            self.status_var.set("Registration failed")
            messagebox.showerror("Registration Failed", result.get('error', 'Unknown error'))
            
    def _handle_guest(self):
        """Handle guest mode button."""
        if self.on_success:
            self.on_success()
        self.window.destroy()
        
    def _handle_oauth(self, provider: str):
        """Handle OAuth login."""
        messagebox.showinfo("OAuth", f"{provider} login coming soon!")
        
    def _show_reset_password(self):
        """Show password reset dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title("Reset Password")
        dialog.geometry("350x200")
        
        ttk.Label(dialog, text="Enter your email address:").pack(pady=20)
        
        email_var = tk.StringVar()
        email_entry = ttk.Entry(dialog, textvariable=email_var, width=30)
        email_entry.pack(pady=10)
        
        async def send_reset():
            email = email_var.get().strip()
            if not email:
                messagebox.showerror("Error", "Please enter your email")
                return
                
            result = await self.auth.reset_password(email)
            
            if result['success']:
                messagebox.showinfo("Email Sent", 
                                  "Password reset instructions have been sent to your email.")
                dialog.destroy()
            else:
                messagebox.showerror("Error", result.get('error', 'Failed to send reset email'))
                
        ttk.Button(dialog, text="Send Reset Email", 
                  command=lambda: asyncio.create_task(send_reset())).pack(pady=20)
                  
    def _show_upgrade(self):
        """Show upgrade window."""
        messagebox.showinfo("Upgrade", "Upgrade flow will open Stripe Checkout (coming soon!)")


class AccountWindow:
    """Account management window for logged-in users."""
    
    def __init__(self, auth_plugin):
        self.auth = auth_plugin
        self.window = None
        
    def show(self):
        """Show account management window."""
        if not self.auth.is_authenticated():
            messagebox.showerror("Error", "Please sign in first")
            return
            
        if self.window and self.window.winfo_exists():
            self.window.focus()
            return
            
        self.window = tk.Toplevel()
        self.window.title("Account Settings")
        self.window.geometry("400x400")
        
        user = self.auth.get_user()
        
        # User info
        info_frame = ttk.LabelFrame(self.window, text="Account Information", padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(info_frame, text=f"Email: {user.get('email')}").pack(anchor='w', pady=5)
        
        status = "Premium" if self.auth.is_premium else "Free"
        ttk.Label(info_frame, text=f"Status: {status}").pack(anchor='w', pady=5)
        
        if not self.auth.is_premium:
            search_count = self.auth.get_search_count()
            ttk.Label(info_frame, text=f"Searches used: {search_count} / 50").pack(anchor='w', pady=5)
            
        # Actions
        action_frame = ttk.LabelFrame(self.window, text="Actions", padding=20)
        action_frame.pack(fill='x', padx=20, pady=20)
        
        if not self.auth.is_premium:
            ttk.Button(action_frame, text="Upgrade to Premium - $20",
                      command=self._show_upgrade).pack(pady=10)
                      
        ttk.Button(action_frame, text="Change Password",
                  command=self._change_password).pack(pady=10)
                  
        ttk.Button(action_frame, text="Sign Out",
                  command=self._handle_logout).pack(pady=10)
                  
    def _show_upgrade(self):
        """Show upgrade flow."""
        messagebox.showinfo("Upgrade", "Stripe Checkout integration coming soon!")
        
    def _change_password(self):
        """Show change password dialog."""
        messagebox.showinfo("Change Password", "Password change flow coming soon!")
        
    def _handle_logout(self):
        """Handle logout."""
        asyncio.create_task(self._async_logout())
        
    async def _async_logout(self):
        """Async logout handler."""
        result = await self.auth.logout()
        
        if result['success']:
            messagebox.showinfo("Signed Out", "You have been signed out successfully.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Failed to sign out")