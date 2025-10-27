#!/usr/bin/env python3
"""
Diagnostic script to test face encoding functionality
"""
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("FACE ENCODING DIAGNOSTIC TEST")
print("=" * 80)
print()

# Test 1: Check if OpenCV is installed
print("TEST 1: OpenCV Installation")
print("-" * 40)
try:
    import cv2
    print("✓ OpenCV (cv2) is installed")
    print(f"  Version: {cv2.__version__}")
    print(f"  Location: {cv2.__file__}")
except ImportError as e:
    print(f"✗ OpenCV (cv2) is NOT installed")
    print(f"  Error: {e}")
    print("\n  FIX: Run 'pip install opencv-python'")
    sys.exit(1)

print()

# Test 2: Check if face_recognition utility works
print("TEST 2: Face Recognition Utility")
print("-" * 40)
try:
    from utils.face_recognition_utils import is_face_recognition_available, generate_face_encoding
    available = is_face_recognition_available()
    print(f"✓ Face recognition module loaded")
    print(f"  Available: {available}")
    if not available:
        print("  ✗ Face recognition is not available!")
except ImportError as e:
    print(f"✗ Cannot import face recognition utilities")
    print(f"  Error: {e}")
    sys.exit(1)

print()

# Test 3: Test face encoding with a sample image
print("TEST 3: Face Encoding Generation")
print("-" * 40)

# Create a simple test image (100x100 white square with a black dot)
try:
    import numpy as np
    from PIL import Image, ImageDraw
    import base64
    import io
    
    print("Creating test image...")
    # Create a simple face-like image
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw simple face features
    draw.ellipse([50, 50, 150, 150], fill='black', outline='black')  # Head
    draw.ellipse([80, 90, 100, 110], fill='white', outline='white')  # Left eye
    draw.ellipse([120, 90, 140, 110], fill='white', outline='white')  # Right eye
    draw.line([110, 130, 110, 150], fill='black', width=3)  # Nose
    
    # Convert to base64
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode()
    
    print(f"  Test image created: {len(img_base64)} bytes")
    
    # Try to generate face encoding
    print("  Generating face encoding...")
    result = generate_face_encoding(img_base64)
    
    print(f"  Result: {result['message']}")
    print(f"    - success: {result['success']}")
    print(f"    - face_count: {result['face_count']}")
    
    if result['success']:
        encoding = json.loads(result['encoding'])
        print(f"    - encoding shape: {np.array(encoding).shape}")
        print(f"    - encoding bytes: {len(result['encoding'])}")
        print("  ✓ Face encoding generation works!")
    else:
        print("  ✗ Face encoding generation failed")
        print(f"    Reason: {result['message']}")
        
except Exception as e:
    print(f"✗ Error during face encoding test")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Check database connection
print("TEST 4: Database Connection")
print("-" * 40)
try:
    from models import db
    from models.gate_entry import GateUser
    from app import app
    
    with app.app_context():
        # Try to query users
        users = GateUser.query.all()
        print(f"✓ Database connected")
        print(f"  Total users: {len(users)}")
        
        # Check for users with face encodings
        users_with_encoding = [u for u in users if u.face_encoding]
        print(f"  Users with face encoding: {len(users_with_encoding)}")
        
        for user in users_with_encoding[:3]:  # Show first 3
            try:
                encoding_data = json.loads(user.face_encoding)
                if isinstance(encoding_data, list):
                    print(f"    - {user.name} ({user.phone}): {len(encoding_data)} encodings")
                else:
                    print(f"    - {user.name} ({user.phone}): Invalid format")
            except:
                print(f"    - {user.name} ({user.phone}): Cannot parse encoding")
                
except Exception as e:
    print(f"✗ Database error")
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)