"""
Documentation Manager Module

Manages documentation files for in-app help browser.
Discovers and loads markdown documentation from the docs folder.
"""

from pathlib import Path
from typing import List, Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class DocumentationManager(QObject):
    """
    Manages documentation files for the documentation browser.
    
    Features:
    - Discover documentation files in docs/ folder
    - Organize by category (User Guides, Technical, Test Plans, etc.)
    - Load markdown content
    - Search/filter documents
    """
    
    # Signals
    documentsLoaded = pyqtSignal()
    documentContentLoaded = pyqtSignal(str, str)  # title, content
    error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._docs_dir = None
        self._documents = []  # List of (category, title, filepath) tuples
        self._discover_documents()
    
    def _discover_documents(self):
        """Discover all markdown documentation files."""
        self._documents = []
        
        # Determine docs directory (relative to main.py location)
        # Assume we're in backend/, so docs/ is ../docs/
        current_file = Path(__file__).resolve()
        app_dir = current_file.parent.parent  # Go up to AudioBrowser-QML/
        self._docs_dir = app_dir / "docs"
        
        if not self._docs_dir.exists():
            self.error.emit(f"Documentation folder not found: {self._docs_dir}")
            return
        
        # Add README and CHANGELOG from root if they exist
        readme_path = app_dir / "README.md"
        if readme_path.exists():
            self._documents.append(("Getting Started", "README", str(readme_path)))
        
        # Add main INDEX
        index_path = self._docs_dir / "INDEX.md"
        if index_path.exists():
            self._documents.append(("Getting Started", "Documentation Index", str(index_path)))
        
        # User Guides
        user_guides_dir = self._docs_dir / "user_guides"
        if user_guides_dir.exists():
            for doc_file in sorted(user_guides_dir.glob("*.md")):
                title = self._format_title(doc_file.stem)
                self._documents.append(("User Guides", title, str(doc_file)))
        
        # Technical Documentation
        technical_dir = self._docs_dir / "technical"
        if technical_dir.exists():
            for doc_file in sorted(technical_dir.glob("*.md")):
                title = self._format_title(doc_file.stem)
                self._documents.append(("Technical", title, str(doc_file)))
        
        # Test Plans
        test_plans_dir = self._docs_dir / "test_plans"
        if test_plans_dir.exists():
            for doc_file in sorted(test_plans_dir.glob("*.md")):
                title = self._format_title(doc_file.stem)
                self._documents.append(("Test Plans", title, str(doc_file)))
        
        # Phase Reports (first 5 for quick access)
        phase_reports_dir = self._docs_dir / "phase_reports"
        if phase_reports_dir.exists():
            phase_files = sorted(phase_reports_dir.glob("PHASE_*_SUMMARY.md"))[:5]
            for doc_file in phase_files:
                title = self._format_title(doc_file.stem)
                self._documents.append(("Phase Reports", title, str(doc_file)))
        
        self.documentsLoaded.emit()
    
    def _format_title(self, filename: str) -> str:
        """Format filename into readable title."""
        # Replace underscores with spaces and title case
        title = filename.replace("_", " ").title()
        # Special case for common acronyms
        title = title.replace("Qml", "QML")
        title = title.replace("Ui", "UI")
        title = title.replace("Api", "API")
        title = title.replace("Bpm", "BPM")
        return title
    
    @pyqtSlot(result=list)
    def getDocuments(self) -> List[Dict[str, str]]:
        """
        Get list of all documents.
        
        Returns:
            List of dicts with keys: category, title, filepath
        """
        return [
            {
                "category": cat,
                "title": title,
                "filepath": filepath
            }
            for cat, title, filepath in self._documents
        ]
    
    @pyqtSlot(str, result=str)
    def loadDocument(self, filepath: str) -> str:
        """
        Load document content from file.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            Document content as string
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            self.error.emit(f"Error loading document: {e}")
            return f"Error loading document: {e}"
    
    @pyqtSlot(str, result=list)
    def searchDocuments(self, query: str) -> List[Dict[str, str]]:
        """
        Search documents by query string.
        
        Args:
            query: Search query (matches against category and title)
            
        Returns:
            Filtered list of documents matching query
        """
        if not query:
            return self.getDocuments()
        
        query_lower = query.lower()
        results = []
        
        for cat, title, filepath in self._documents:
            if query_lower in cat.lower() or query_lower in title.lower():
                results.append({
                    "category": cat,
                    "title": title,
                    "filepath": filepath
                })
        
        return results
    
    @pyqtSlot(result=int)
    def getDocumentCount(self) -> int:
        """Get total number of documents."""
        return len(self._documents)
