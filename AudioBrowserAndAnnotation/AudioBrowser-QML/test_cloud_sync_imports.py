#!/usr/bin/env python3
"""
Test cloud sync module imports.

This test verifies that all cloud sync modules can be imported successfully.
"""

def test_imports():
    """Test that all cloud sync modules can be imported."""
    try:
        from backend.cloud_sync_base import CloudSyncBase, SyncHistory, SyncRules, SyncVersion
        print("✓ cloud_sync_base imported successfully")
        
        from backend.gdrive_sync import GDriveSync
        print("✓ gdrive_sync imported successfully")
        
        from backend.dropbox_sync import DropboxSync
        print("✓ dropbox_sync imported successfully")
        
        from backend.webdav_sync import WebDAVSync
        print("✓ webdav_sync imported successfully")
        
        from backend.sync_manager import SyncManager
        print("✓ sync_manager imported successfully")
        
        print("\n✓ All cloud sync modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = test_imports()
    sys.exit(0 if success else 1)
