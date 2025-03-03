"""
License management system for the testing framework.
Handles license validation, feature access control, and usage tracking.
"""
import os
import json
import hmac
import hashlib
import time
from datetime import datetime
from typing import Dict, Optional, List

class LicenseType:
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class LicenseFeatures:
    """Features available in different license tiers"""
    BASIC = {
        "max_tests": 100,
        "parallel_execution": False,
        "advanced_reporting": False,
        "cloud_execution": False,
        "team_collaboration": False,
        "custom_integrations": False,
        "support_sla": "48h"
    }
    
    PROFESSIONAL = {
        "max_tests": 1000,
        "parallel_execution": True,
        "advanced_reporting": True,
        "cloud_execution": True,
        "team_collaboration": False,
        "custom_integrations": False,
        "support_sla": "24h"
    }
    
    ENTERPRISE = {
        "max_tests": float('inf'),
        "parallel_execution": True,
        "advanced_reporting": True,
        "cloud_execution": True,
        "team_collaboration": True,
        "custom_integrations": True,
        "support_sla": "4h"
    }

class LicenseManager:
    def __init__(self):
        self.license_key: Optional[str] = None
        self.license_data: Optional[Dict] = None
        self._usage_data: Dict = {
            "test_count": 0,
            "last_validation": None,
            "features_used": set()
        }
        self._load_license()
    
    def _load_license(self) -> None:
        """Load license from environment variable or config file"""
        self.license_key = os.getenv("TEST_FRAMEWORK_LICENSE")
        if not self.license_key:
            license_file = os.path.join(os.path.dirname(__file__), "..", "..", "license.json")
            try:
                if os.path.exists(license_file):
                    with open(license_file, 'r') as f:
                        data = json.load(f)
                        self.license_key = data.get("license_key")
            except Exception as e:
                print(f"Error loading license file: {e}")
    
    def validate_license(self, license_key: Optional[str] = None) -> bool:
        """
        Validate the license key and update license data
        Returns True if license is valid, False otherwise
        """
        if license_key:
            self.license_key = license_key
            
        if not self.license_key:
            return False
            
        try:
            # In a real implementation, this would validate against a license server
            # For now, we'll use a simple validation scheme
            parts = self.license_key.split('-')
            if len(parts) != 4:
                return False
                
            timestamp = int(parts[0], 16)
            if timestamp < time.time():  # Check if license has expired
                return False
                
            self.license_data = {
                "type": self._determine_license_type(self.license_key),
                "expiration": datetime.fromtimestamp(timestamp).isoformat(),
                "features": self._get_features_for_type(self._determine_license_type(self.license_key))
            }
            
            self._usage_data["last_validation"] = datetime.now().isoformat()
            return True
            
        except Exception as e:
            print(f"License validation error: {e}")
            return False
    
    def _determine_license_type(self, license_key: str) -> str:
        """Determine license type from key"""
        # Simple determination based on key format
        if license_key.startswith('E'):
            return LicenseType.ENTERPRISE
        elif license_key.startswith('P'):
            return LicenseType.PROFESSIONAL
        return LicenseType.BASIC
    
    def _get_features_for_type(self, license_type: str) -> Dict:
        """Get feature set for license type"""
        if license_type == LicenseType.ENTERPRISE:
            return LicenseFeatures.ENTERPRISE
        elif license_type == LicenseType.PROFESSIONAL:
            return LicenseFeatures.PROFESSIONAL
        return LicenseFeatures.BASIC
    
    def check_feature_access(self, feature: str) -> bool:
        """Check if current license has access to a feature"""
        if not self.license_data:
            return False
        
        has_access = self.license_data["features"].get(feature, False)
        if has_access:
            self._usage_data["features_used"].add(feature)
        return has_access
    
    def track_test_execution(self) -> bool:
        """Track test execution and check if within limits"""
        if not self.license_data:
            return False
            
        self._usage_data["test_count"] += 1
        return self._usage_data["test_count"] <= self.license_data["features"]["max_tests"]
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            "test_count": self._usage_data["test_count"],
            "last_validation": self._usage_data["last_validation"],
            "features_used": list(self._usage_data["features_used"])
        }

def generate_license_key(license_type: str, duration_days: int = 365) -> str:
    """
    Generate a new license key
    This would typically be done by a separate license server/service
    """
    expiration = int(time.time()) + (duration_days * 24 * 60 * 60)
    prefix = license_type[0].upper()
    # In a real implementation, this would use proper cryptographic methods
    key_parts = [
        hex(expiration)[2:],
        prefix + hashlib.md5(str(expiration).encode()).hexdigest()[:6],
        hashlib.sha256(str(time.time()).encode()).hexdigest()[:8],
        hashlib.md5(str(license_type).encode()).hexdigest()[:6]
    ]
    return "-".join(key_parts)