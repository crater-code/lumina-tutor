"""
Test to verify project setup is complete
"""
import pytest


def test_imports():
    """Test that all core dependencies can be imported"""
    try:
        import fastapi
        import PyPDF2
        import pdfplumber
        import sentence_transformers
        import faiss
        import chromadb
        import sqlalchemy
        import hypothesis
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required dependency: {e}")


def test_project_structure():
    """Test that project directories exist"""
    import os
    
    # Check main directories
    assert os.path.exists("src"), "src directory should exist"
    assert os.path.exists("tests"), "tests directory should exist"
    assert os.path.exists("data"), "data directory should exist"
    assert os.path.exists("frontend"), "frontend directory should exist"
    
    # Check key files
    assert os.path.exists("src/main.py"), "src/main.py should exist"
    assert os.path.exists("requirements.txt"), "requirements.txt should exist"
    assert os.path.exists("frontend/package.json"), "frontend/package.json should exist"
    assert os.path.exists("README.md"), "README.md should exist"


def test_fastapi_app():
    """Test that FastAPI app can be imported"""
    from src.main import app
    assert app is not None
    assert hasattr(app, 'routes')
