#!/usr/bin/env python3
"""
Basic Undo Manager Structure Test

Tests that the undo manager module can be imported and has correct structure.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Basic Undo Manager Structure Test")
print("=" * 60)

try:
    # Test 1: Import module
    print("\nTest 1: Importing undo_manager module...")
    from backend.undo_manager import (
        UndoManager,
        UndoCommand,
        ProvidedNameCommand,
        AnnotationAddCommand,
        AnnotationDeleteCommand,
        AnnotationEditCommand
    )
    print("✓ Successfully imported all undo classes")
    
    # Test 2: Create UndoManager instance
    print("\nTest 2: Creating UndoManager instance...")
    undo_manager = UndoManager()
    print("✓ UndoManager created")
    
    # Test 3: Check required methods exist
    print("\nTest 3: Checking UndoManager has required methods...")
    required_methods = [
        'undo', 'redo', 'can_undo', 'can_redo',
        'push_command', 'setCapacity', 'clear',
        'setFileManager', 'setAnnotationManager',
        'canUndo', 'canRedo', 'getUndoText', 'getRedoText',
        'record_provided_name_change', 'record_annotation_add',
        'record_annotation_delete', 'record_annotation_edit'
    ]
    
    for method in required_methods:
        if not hasattr(undo_manager, method):
            print(f"✗ Missing method: {method}")
            sys.exit(1)
    print(f"✓ All {len(required_methods)} required methods exist")
    
    # Test 4: Check command classes have required methods
    print("\nTest 4: Checking command classes have required methods...")
    command_classes = [
        ProvidedNameCommand,
        AnnotationAddCommand,
        AnnotationDeleteCommand,
        AnnotationEditCommand
    ]
    
    for cmd_class in command_classes:
        # Check base methods
        if not hasattr(cmd_class, 'execute'):
            print(f"✗ {cmd_class.__name__} missing execute method")
            sys.exit(1)
        if not hasattr(cmd_class, 'undo'):
            print(f"✗ {cmd_class.__name__} missing undo method")
            sys.exit(1)
    print(f"✓ All {len(command_classes)} command classes have required methods")
    
    # Test 5: Check signals exist
    print("\nTest 5: Checking UndoManager signals...")
    required_signals = [
        'canUndoChanged',
        'canRedoChanged',
        'undoTextChanged',
        'redoTextChanged',
        'commandExecuted'
    ]
    
    for signal in required_signals:
        if not hasattr(undo_manager, signal):
            print(f"✗ Missing signal: {signal}")
            sys.exit(1)
    print(f"✓ All {len(required_signals)} required signals exist")
    
    # Test 6: Check initial state
    print("\nTest 6: Checking initial state...")
    assert undo_manager.can_undo() == False, "Expected can_undo() to be False initially"
    assert undo_manager.can_redo() == False, "Expected can_redo() to be False initially"
    assert undo_manager.get_undo_text() == "", "Expected empty undo text initially"
    assert undo_manager.get_redo_text() == "", "Expected empty redo text initially"
    print("✓ Initial state is correct")
    
    # Test 7: Check capacity setting
    print("\nTest 7: Testing capacity setting...")
    undo_manager.setCapacity(50)
    undo_manager.setCapacity(100)
    undo_manager.setCapacity(500)
    print("✓ Capacity setting works")
    
    print("\n" + "=" * 60)
    print("✓ All structure tests passed! (7/7)")
    print("=" * 60)
    print("\nUndo manager structure is correct and ready for integration.")
    sys.exit(0)

except Exception as e:
    print(f"\n✗ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
