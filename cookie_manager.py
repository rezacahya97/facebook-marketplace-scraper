# Phase 1: Cookie Management System
# Implements cookie persistence and rotation for Facebook session management

import pickle
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

class CookieManager:
    """Manages Facebook cookies for session persistence"""
    
    def __init__(self, cookies_dir="cookies"):
        self.cookies_dir = Path(cookies_dir)
        self.cookies_dir.mkdir(exist_ok=True)
        
        # Cookie rotation settings
        self.max_cookie_age_hours = 24  # Rotate cookies after 24 hours
        self.max_sessions_per_cookie = 10  # Limit usage per cookie set
        
    def save_cookies(self, page, session_name: str = "default") -> bool:
        """Save browser cookies for future use"""
        try:
            cookies = page.context.cookies()
            
            if not cookies:
                print("⚠️ No cookies found to save")
                return False
            
            # Filter for Facebook-specific cookies
            fb_cookies = [
                cookie for cookie in cookies 
                if 'facebook.com' in cookie.get('domain', '') or 
                   'fb.com' in cookie.get('domain', '')
            ]
            
            if not fb_cookies:
                print("⚠️ No Facebook cookies found to save")
                return False
            
            cookie_data = {
                "cookies": fb_cookies,
                "saved_at": datetime.now().isoformat(),
                "usage_count": 0,
                "last_used": None,
                "session_name": session_name,
                "user_agent": page.evaluate("navigator.userAgent"),
                "viewport": page.viewport_size
            }
            
            cookie_file = self.cookies_dir / f"{session_name}.json"
            
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            print(f"✅ Saved {len(fb_cookies)} Facebook cookies for session '{session_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save cookies: {e}")
            return False
    
    def load_cookies(self, context, session_name: str = "default") -> bool:
        """Load saved cookies into browser context"""
        try:
            cookie_file = self.cookies_dir / f"{session_name}.json"
            
            if not cookie_file.exists():
                print(f"⚠️ No saved cookies found for session '{session_name}'")
                return False
            
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            # Check cookie age
            saved_at = datetime.fromisoformat(cookie_data["saved_at"])
            age_hours = (datetime.now() - saved_at).total_seconds() / 3600
            
            if age_hours > self.max_cookie_age_hours:
                print(f"⚠️ Cookies too old ({age_hours:.1f}h), rotating...")
                self._rotate_cookie_file(cookie_file)
                return False
            
            # Check usage count
            if cookie_data["usage_count"] >= self.max_sessions_per_cookie:
                print(f"⚠️ Cookie usage limit reached ({cookie_data['usage_count']}), rotating...")
                self._rotate_cookie_file(cookie_file)
                return False
            
            # Load cookies into context
            cookies = cookie_data["cookies"]
            context.add_cookies(cookies)
            
            # Update usage tracking
            cookie_data["usage_count"] += 1
            cookie_data["last_used"] = datetime.now().isoformat()
            
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            print(f"✅ Loaded {len(cookies)} cookies for session '{session_name}' (usage: {cookie_data['usage_count']})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            return False
    
    def get_available_sessions(self) -> List[str]:
        """Get list of available cookie sessions"""
        sessions = []
        
        for cookie_file in self.cookies_dir.glob("*.json"):
            try:
                with open(cookie_file, 'r') as f:
                    cookie_data = json.load(f)
                
                # Check if session is still valid
                saved_at = datetime.fromisoformat(cookie_data["saved_at"])
                age_hours = (datetime.now() - saved_at).total_seconds() / 3600
                
                if (age_hours <= self.max_cookie_age_hours and 
                    cookie_data["usage_count"] < self.max_sessions_per_cookie):
                    sessions.append(cookie_data["session_name"])
                    
            except Exception as e:
                print(f"⚠️ Invalid cookie file {cookie_file}: {e}")
        
        return sessions
    
    def create_session_from_manual_login(self, page, session_name: str) -> bool:
        """Helper to create cookie session from manual Facebook login"""
        print(f"🔑 Creating cookie session '{session_name}' from manual login...")
        print("📋 Instructions:")
        print("1. A browser will open to Facebook")
        print("2. Manually log in to your Facebook account")
        print("3. Navigate to Facebook Marketplace")
        print("4. Close the browser when done")
        print("5. Cookies will be automatically saved")
        
        try:
            # This would be used with a non-headless browser for manual setup
            return self.save_cookies(page, session_name)
        except Exception as e:
            print(f"❌ Failed to create session: {e}")
            return False
    
    def _rotate_cookie_file(self, cookie_file: Path):
        """Move old cookie file to archive"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"archived_{cookie_file.stem}_{timestamp}.json"
        archive_path = self.cookies_dir / "archived" / archive_name
        
        archive_path.parent.mkdir(exist_ok=True)
        cookie_file.rename(archive_path)
        print(f"📁 Archived old cookies to: {archive_path}")
    
    def cleanup_old_cookies(self, max_age_days: int = 7):
        """Clean up old cookie files"""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        for cookie_file in self.cookies_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(cookie_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cookie_file.unlink()
                    print(f"🗑️ Deleted old cookie file: {cookie_file}")
            except Exception as e:
                print(f"⚠️ Error cleaning up {cookie_file}: {e}")
    
    def get_session_stats(self) -> Dict:
        """Get statistics about cookie sessions"""
        sessions = []
        total_cookies = 0
        
        for cookie_file in self.cookies_dir.glob("*.json"):
            try:
                with open(cookie_file, 'r') as f:
                    cookie_data = json.load(f)
                
                saved_at = datetime.fromisoformat(cookie_data["saved_at"])
                age_hours = (datetime.now() - saved_at).total_seconds() / 3600
                
                session_info = {
                    "name": cookie_data["session_name"],
                    "age_hours": round(age_hours, 1),
                    "usage_count": cookie_data["usage_count"],
                    "cookie_count": len(cookie_data["cookies"]),
                    "valid": age_hours <= self.max_cookie_age_hours and 
                            cookie_data["usage_count"] < self.max_sessions_per_cookie
                }
                
                sessions.append(session_info)
                total_cookies += session_info["cookie_count"]
                
            except Exception as e:
                print(f"⚠️ Error reading {cookie_file}: {e}")
        
        return {
            "total_sessions": len(sessions),
            "valid_sessions": len([s for s in sessions if s["valid"]]),
            "total_cookies": total_cookies,
            "sessions": sessions
        }

# Helper functions for integration with existing code
def create_cookie_manager():
    """Factory function to create cookie manager"""
    return CookieManager()

def save_cookies_for_session(page, session_name: str = "default"):
    """Quick function to save cookies"""
    manager = create_cookie_manager()
    return manager.save_cookies(page, session_name)

def load_cookies_for_session(context, session_name: str = "default"):
    """Quick function to load cookies"""
    manager = create_cookie_manager()
    return manager.load_cookies(context, session_name)

if __name__ == "__main__":
    # Test cookie manager
    manager = CookieManager()
    stats = manager.get_session_stats()
    
    print("🍪 === COOKIE MANAGER STATUS ===")
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"Valid Sessions: {stats['valid_sessions']}")
    print(f"Total Cookies: {stats['total_cookies']}")
    
    if stats['sessions']:
        print("\n📋 Session Details:")
        for session in stats['sessions']:
            status = "✅ Valid" if session['valid'] else "❌ Invalid"
            print(f"  {session['name']}: {session['cookie_count']} cookies, "
                  f"{session['age_hours']}h old, used {session['usage_count']}x - {status}")
    else:
        print("\n⚠️ No cookie sessions found")
        print("💡 Use create_session_from_manual_login() to create your first session")