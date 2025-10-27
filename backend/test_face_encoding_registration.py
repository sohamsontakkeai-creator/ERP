#!/usr/bin/env python3
"""
Complete diagnostic test for face encoding registration
This script tests each step of the face encoding process
"""

import sys
import os
import json
import base64
import logging
from pathlib import Path
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_cv2_import():
    """Test 1: Check if OpenCV is installed"""
    print("\n" + "="*80)
    print("TEST 1: OpenCV (cv2) Installation")
    print("="*80)
    
    try:
        import cv2
        print(f"✅ OpenCV successfully imported")
        print(f"   Version: {cv2.__version__}")
        print(f"   Location: {cv2.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import cv2: {e}")
        print(f"   Fix: pip install opencv-python")
        return False

def test_face_recognition_utils():
    """Test 2: Check face_recognition_utils module"""
    print("\n" + "="*80)
    print("TEST 2: Face Recognition Utils Module")
    print("="*80)
    
    try:
        from utils.face_recognition_utils import (
            is_face_recognition_available,
            base64_to_image,
            generate_face_encoding
        )
        print(f"✅ Successfully imported face_recognition_utils")
        print(f"   is_face_recognition_available(): {is_face_recognition_available()}")
        return True
    except Exception as e:
        print(f"❌ Failed to import face_recognition_utils: {e}")
        return False

def test_base64_image_conversion():
    """Test 3: Test base64 to image conversion with sample image"""
    print("\n" + "="*80)
    print("TEST 3: Base64 Image Conversion")
    print("="*80)
    
    try:
        from PIL import Image
        import cv2
        import numpy as np
        
        # Create a simple test image (100x100 with a face-like pattern)
        print("Creating sample image...")
        img = Image.new('RGB', (100, 100), color=(200, 150, 150))
        pixels = img.load()
        
        # Add eyes (simple dots)
        for i in range(35, 45):
            for j in range(35, 45):
                pixels[j, i] = (0, 0, 0)  # Left eye
                pixels[j+20, i] = (0, 0, 0)  # Right eye
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=80)
        image_bytes = buffer.getvalue()
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{base64_string}"
        
        print(f"✅ Created sample image")
        print(f"   Image size: {len(image_bytes)} bytes")
        print(f"   Base64 length: {len(base64_string)} characters")
        print(f"   Data URL length: {len(data_url)} characters")
        
        # Test conversion
        from utils.face_recognition_utils import base64_to_image
        
        converted_img = base64_to_image(data_url)
        if converted_img:
            print(f"✅ Successfully converted base64 to image")
            print(f"   Converted image size: {converted_img.size}")
            print(f"   Converted image mode: {converted_img.mode}")
            return True, base64_string
        else:
            print(f"❌ Failed to convert base64 to image")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in base64 conversion: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_face_encoding_generation(base64_string):
    """Test 4: Test face encoding generation"""
    print("\n" + "="*80)
    print("TEST 4: Face Encoding Generation")
    print("="*80)
    
    if not base64_string:
        print("⚠️  Skipping (no base64 image from previous test)")
        return False
    
    try:
        from utils.face_recognition_utils import generate_face_encoding
        
        print("Calling generate_face_encoding()...")
        result = generate_face_encoding(base64_string)
        
        print(f"Result: {json.dumps(result, default=str, indent=2)}")
        
        if result.get('success'):
            print(f"✅ Face encoding generated successfully")
            if result.get('encoding'):
                encoding_data = json.loads(result['encoding'])
                print(f"   Encoding type: {type(encoding_data)}")
                if isinstance(encoding_data, list):
                    print(f"   Encoding shape: {len(encoding_data)}x{len(encoding_data[0]) if encoding_data else 0}")
                print(f"   Encoding JSON size: {len(result['encoding'])} bytes")
            return True
        else:
            print(f"❌ Face encoding generation failed: {result.get('message')}")
            print(f"   Faces detected: {result.get('face_count')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in face encoding generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test 5: Test database connection"""
    print("\n" + "="*80)
    print("TEST 5: Database Connection")
    print("="*80)
    
    try:
        from models import db
        from models.gate_entry import GateUser
        
        # Try to query
        user_count = GateUser.query.count()
        print(f"✅ Database connection successful")
        print(f"   Total users in database: {user_count}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_gate_entry_service():
    """Test 6: Test GateEntryServiceDB"""
    print("\n" + "="*80)
    print("TEST 6: GateEntryServiceDB Module")
    print("="*80)
    
    try:
        from services.gate_entry_service_db import GateEntryServiceDB
        
        service = GateEntryServiceDB()
        print(f"✅ GateEntryServiceDB instantiated successfully")
        
        # Get users
        users = service.get_users()
        print(f"   Total registered users: {len(users)}")
        
        # Show users with face encoding
        users_with_encoding = [u for u in users if u.get('face_encoding')]
        print(f"   Users with face encoding: {len(users_with_encoding)}")
        
        return True
    except Exception as e:
        print(f"❌ GateEntryServiceDB failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_register_with_sample_image():
    """Test 7: Complete registration with sample image"""
    print("\n" + "="*80)
    print("TEST 7: Complete User Registration Test")
    print("="*80)
    
    try:
        from PIL import Image
        import base64
        from io import BytesIO
        from services.gate_entry_service_db import GateEntryServiceDB
        
        # Create multiple sample images
        print("Creating 3 sample images for registration...")
        photos = []
        for i in range(3):
            img = Image.new('RGB', (100, 100), color=(200, 150, 150))
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=80)
            image_bytes = buffer.getvalue()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{base64_string}"
            photos.append(data_url)
        
        print(f"✅ Created {len(photos)} sample images")
        
        # Register user
        service = GateEntryServiceDB()
        test_phone = "TEST_9999999"
        
        # Check if user already exists
        existing = service.get_user_by_phone(test_phone)
        if existing:
            print(f"Deleting existing test user...")
            service.delete_user(test_phone)
        
        print(f"Registering test user...")
        result = service.register_user(
            name="TEST_USER_FACE_ENCODING",
            phone=test_phone,
            photos=photos
        )
        
        print(f"Registration result:")
        print(json.dumps(result, default=str, indent=2))
        
        if result.get('success'):
            print(f"✅ User registered successfully")
            print(f"   Face encodings: {result.get('face_encodings_count')}")
            print(f"   Has face encoding: {result.get('has_face_encoding')}")
            
            # Verify in database
            user = service.get_user_by_phone(test_phone)
            if user and user.get('face_encoding'):
                print(f"✅ Face encoding found in database")
                print(f"   Encoding size: {len(user['face_encoding'])} bytes")
            else:
                print(f"❌ Face encoding NOT found in database!")
            
            # Cleanup
            service.delete_user(test_phone)
            print(f"✅ Test user cleaned up")
            
            return result.get('face_encodings_count', 0) > 0
        else:
            print(f"❌ Registration failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "FACE ENCODING REGISTRATION DIAGNOSTIC" + " "*22 + "║")
    print("╚" + "="*78 + "╝")
    
    results = {}
    
    # Test 1
    results['cv2_import'] = test_cv2_import()
    if not results['cv2_import']:
        print("\n❌ CRITICAL: OpenCV not installed. Stopping tests.")
        print("   Run: pip install opencv-python")
        return
    
    # Test 2
    results['face_utils'] = test_face_recognition_utils()
    
    # Test 3
    success, base64_string = test_base64_image_conversion()
    results['base64_conversion'] = success
    
    # Test 4
    results['face_encoding'] = test_face_encoding_generation(base64_string)
    
    # Test 5
    results['database'] = test_database_connection()
    
    # Test 6
    results['gate_service'] = test_gate_entry_service()
    
    # Test 7
    results['registration'] = test_register_with_sample_image()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nYour face encoding system is working correctly.")
        print("You can now use the application normally.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease fix the issues above before using the application.")
    print("="*80 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()