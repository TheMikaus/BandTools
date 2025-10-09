#!/usr/bin/env python3
"""
Test metaclass fix for CloudSyncBase.

Verifies that the QABCMeta metaclass properly resolves the conflict between
QObject (PyQt6.sip.wrappertype) and ABC (ABCMeta).
"""

def test_metaclass_resolution():
    """Test that CloudSyncBase can be imported and inherited from."""
    from backend.cloud_sync_base import CloudSyncBase
    
    print("✓ CloudSyncBase imported successfully")
    
    # Verify it has the correct metaclass
    metaclass = type(CloudSyncBase)
    print(f"✓ CloudSyncBase metaclass: {metaclass.__name__}")
    
    # Test that we can create a concrete implementation
    class TestSync(CloudSyncBase):
        """Test implementation of CloudSyncBase."""
        
        def isAvailable(self) -> bool:
            return True
        
        def isAuthenticated(self) -> bool:
            return False
        
        def authenticate(self) -> bool:
            return True
        
        def select_remote_folder(self, folder_name=None):
            return "test_folder"
        
        def upload_file(self, local_path, remote_name=None) -> bool:
            return True
        
        def download_file(self, remote_name, local_path) -> bool:
            return True
        
        def list_remote_files(self):
            return []
        
        def performSync(self, directory, upload) -> bool:
            return True
    
    # Try to instantiate the concrete class
    try:
        test_obj = TestSync()
        print("✓ Concrete implementation instantiated successfully")
        
        # Test that Qt signals work
        assert hasattr(test_obj, 'authenticationStatusChanged')
        assert hasattr(test_obj, 'syncProgress')
        assert hasattr(test_obj, 'syncCompleted')
        assert hasattr(test_obj, 'syncError')
        assert hasattr(test_obj, 'folderSelected')
        print("✓ Qt signals are present")
        
        # Test that abstract methods are implemented
        assert test_obj.isAvailable() == True
        assert test_obj.isAuthenticated() == False
        assert test_obj.authenticate() == True
        print("✓ Abstract methods work correctly")
        
        print("\n✓✓✓ All tests passed! ✓✓✓")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_inheritance():
    """Test that the metaclass properly handles multiple inheritance."""
    from backend.cloud_sync_base import CloudSyncBase
    from abc import ABC, abstractmethod
    
    # Test that we can't instantiate abstract class
    try:
        obj = CloudSyncBase()
        print("✗ Should not be able to instantiate abstract class")
        return False
    except TypeError as e:
        print(f"✓ Cannot instantiate abstract class (as expected): {e}")
        return True


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Testing Metaclass Fix for CloudSyncBase")
    print("=" * 60)
    
    success1 = test_metaclass_resolution()
    print()
    success2 = test_multiple_inheritance()
    
    if success1 and success2:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
