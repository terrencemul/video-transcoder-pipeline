#!/usr/bin/env python3
"""
Test script to validate Video Transcoder Pipeline setup
"""

import os
import sys
import subprocess

def test_python_dependencies():
    """Test if required Python packages are installed."""
    print("Testing Python dependencies...")
    
    required_packages = [
        'opencv-python',
        'ffmpeg-python', 
        'numpy',
        'Pillow',
        'watchdog',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def test_ffmpeg_installation():
    """Test if FFmpeg is installed and accessible."""
    print("\nTesting FFmpeg installation...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("  ✓ FFmpeg is installed and accessible")
            # Extract version info
            lines = result.stdout.split('\n')
            if lines:
                version_line = lines[0]
                print(f"    {version_line}")
            return True
        else:
            print("  ✗ FFmpeg command failed")
            return False
    except subprocess.TimeoutExpired:
        print("  ✗ FFmpeg command timed out")
        return False
    except FileNotFoundError:
        print("  ✗ FFmpeg not found in PATH")
        print("    Please install FFmpeg:")
        print("    - Windows: Download from https://ffmpeg.org/download.html")
        print("    - macOS: brew install ffmpeg")
        print("    - Linux: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"  ✗ Error testing FFmpeg: {e}")
        return False

def test_directory_structure():
    """Test if required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        'input',
        'processing', 
        'output',
        'src',
        'input/short_form_9_16',
        'input/long_form_16_9_or_9_16',
        'input/listings_16_9'
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - MISSING")
            all_exist = False
    
    return all_exist

def test_source_files():
    """Test if source files exist."""
    print("\nTesting source files...")
    
    required_files = [
        'src/__init__.py',
        'src/video_transcoder.py',
        'src/face_detector.py', 
        'src/utils.py',
        'main.py',
        'requirements.txt',
        '.env'
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test if source modules can be imported."""
    print("\nTesting module imports...")
    
    sys.path.insert(0, 'src')
    
    modules = [
        ('utils', 'setup_logging'),
        ('face_detector', 'FaceDetector'),
        ('video_transcoder', 'VideoTranscoder')
    ]
    
    all_imported = True
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"  ✓ {module_name}.{class_name}")
            else:
                print(f"  ✗ {module_name}.{class_name} - CLASS NOT FOUND")
                all_imported = False
        except ImportError as e:
            print(f"  ✗ {module_name} - IMPORT ERROR: {e}")
            all_imported = False
        except Exception as e:
            print(f"  ✗ {module_name} - ERROR: {e}")
            all_imported = False
    
    return all_imported

def main():
    """Run all tests."""
    print("Video Transcoder Pipeline - Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Python Dependencies", test_python_dependencies),
        ("FFmpeg Installation", test_ffmpeg_installation), 
        ("Directory Structure", test_directory_structure),
        ("Source Files", test_source_files),
        ("Module Imports", test_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("✓ All tests passed! The video transcoder pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Add sample videos to the input/ directory")
        print("2. Run: python main.py --help")
        print("3. Try: python example_usage.py")
    else:
        print("✗ Some tests failed. Please fix the issues above before using the pipeline.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
