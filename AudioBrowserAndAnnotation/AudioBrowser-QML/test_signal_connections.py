#!/usr/bin/env python3
"""
Test script to validate QML signal connections.

This test verifies that all signals defined in QML components are properly
connected to handlers, ensuring that UI features are fully functional.
"""

import re
import sys
from pathlib import Path


def find_signals_in_file(filepath):
    """Find all signal declarations in a QML file."""
    signals = []
    with open(filepath, 'r') as f:
        content = f.read()
        # Match signal declarations: signal signalName(params)
        matches = re.finditer(r'signal\s+(\w+)\s*\(([^)]*)\)', content)
        for match in matches:
            signals.append({
                'name': match.group(1),
                'params': match.group(2),
                'file': filepath
            })
    return signals


def find_signal_handlers(filepath, signal_name):
    """Find handlers for a specific signal in QML files."""
    handlers = []
    
    # Create the handler name (onSignalName)
    handler_name = f"on{signal_name[0].upper()}{signal_name[1:]}"
    
    # Search all QML files for this handler
    qml_root = Path(filepath).parent.parent if 'components' in str(filepath) or 'tabs' in str(filepath) else Path(filepath).parent
    for qml_file in qml_root.rglob('*.qml'):
        with open(qml_file, 'r') as f:
            content = f.read()
            # Simple check: if handler name appears with colon (signal connection)
            if re.search(rf'\b{handler_name}\s*:', content):
                # Extract some context (just the line with the handler)
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if handler_name in line and ':' in line:
                        # Get a few lines of context
                        context_start = max(0, i - 1)
                        context_end = min(len(lines), i + 5)
                        context = ' '.join(lines[context_start:context_end]).strip()
                        handlers.append({
                            'file': str(qml_file),
                            'handler': handler_name,
                            'code_preview': context[:150]
                        })
                        break
    
    return handlers


def main():
    """Main test function."""
    print("=" * 80)
    print("QML Signal Connection Validation")
    print("=" * 80)
    
    # Components with signals to check
    components_to_check = [
        'qml/components/WaveformDisplay.qml',
        'qml/components/FileContextMenu.qml',
        'qml/components/BestTakeIndicator.qml',
        'qml/components/PartialTakeIndicator.qml',
        'qml/components/NowPlayingPanel.qml',
        'qml/tabs/LibraryTab.qml',
        'qml/tabs/AnnotationsTab.qml',
    ]
    
    base_path = Path(__file__).parent
    all_connected = True
    
    for component_path in components_to_check:
        full_path = base_path / component_path
        if not full_path.exists():
            print(f"\n⚠️  File not found: {component_path}")
            continue
        
        signals = find_signals_in_file(full_path)
        if not signals:
            continue
        
        print(f"\n📄 {component_path}")
        print("-" * 80)
        
        for signal in signals:
            signal_name = signal['name']
            params = signal['params']
            
            # Find handlers
            handlers = find_signal_handlers(full_path, signal_name)
            
            if handlers:
                print(f"  ✅ {signal_name}({params})")
                for handler in handlers:
                    rel_path = Path(handler['file']).relative_to(base_path)
                    print(f"     └─ Connected in {rel_path}")
                    # Show a preview of what the handler does
                    preview = handler['code_preview'].replace('\n', ' ')[:100]
                    if len(handler['code_preview']) > 100:
                        preview += "..."
                    print(f"        {preview}")
            else:
                print(f"  ❌ {signal_name}({params}) - NOT CONNECTED")
                all_connected = False
    
    print("\n" + "=" * 80)
    if all_connected:
        print("✅ All signals are properly connected!")
        print("=" * 80)
        return 0
    else:
        print("❌ Some signals are not connected!")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
