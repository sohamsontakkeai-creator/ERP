#!/usr/bin/env python3
"""
Test face encoding with a real sample photo from a source
This will help identify if the issue is with:
1. Photo format/encoding
2. Face detection
3. Database storage
"""
import json
import logging
import sys
import requests
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("FACE ENCODING TEST WITH REAL PHOTO")
print("=" * 80)
print()

# Get a real face image from a public source
print("Step 1: Getting a real face image...")
print("-" * 40)
try:
    # Try to get a sample face from a public URL
    # Using a small portrait image URL
    sample_url = "https://www.w3schools.com/css/img_avatar.png"
    
    print(f"Downloading sample photo from: {sample_url}")
    response = requests.get(sample_url, timeout=5)
    
    if response.status_code == 200:
        print(f"✓ Downloaded {len(response.content)} bytes")
        
        # Convert to base64
        import base64
        photo_base64 = base64.b64encode(response.content).decode('utf-8')
        print(f"✓ Converted to base64: {len(photo_base64)} bytes")
        
        # Add data URL prefix
        photo_with_prefix = f"data:image/png;base64,{photo_base64}"
        print(f"✓ Added data URL prefix: {len(photo_with_prefix)} bytes")
        
    else:
        print(f"✗ Failed to download: HTTP {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error downloading: {e}")
    print("\n  Trying alternative method with local image creation...")
    
    # If download fails, create a more realistic test image
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    import base64
    import io
    
    # Create a 200x200 image that looks more like a face
    img = Image.new('RGB', (200, 200), color=(220, 180, 150))  # Skin tone
    draw = ImageDraw.Draw(img)
    
    # Draw face outline (oval)
    draw.ellipse([40, 20, 160, 180], outline=(100, 70, 50), width=2, fill=(220, 180, 150))
    
    # Draw eyes (larger, more realistic)
    draw.ellipse([70, 70, 95, 90], fill=(50, 50, 50))  # Left eye
    draw.ellipse([105, 70, 130, 90], fill=(50, 50, 50))  # Right eye
    draw.ellipse([75, 75, 90, 85], fill=(150, 150, 200))  # Left iris
    draw.ellipse([110, 75, 125, 85], fill=(150, 150, 200))  # Right iris
    
    # Draw eyebrows
    draw.line([70, 65, 95, 60], fill=(80, 60, 40), width=2)
    draw.line([105, 60, 130, 65], fill=(80, 60, 40), width=2)
    
    # Draw nose (triangle)
    draw.line([100, 90, 95, 120], fill=(100, 70, 50), width=2)
    draw.line([100, 90, 105, 120], fill=(100, 70, 50), width=2)
    
    # Draw mouth
    draw.arc([80, 110, 120, 140], 0, 180, fill=(150, 50, 50), width=2)
    
    # Convert to base64
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    photo_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    photo_with_prefix = f"data:image/png;base64,{photo_base64}"
    
    print(f"✓ Created test face image: {len(photo_base64)} bytes")

print()

# Test face encoding generation
print("Step 2: Testing face encoding generation...")
print("-" * 40)
try:
    from utils.face_recognition_utils import generate_face_encoding
    
    result = generate_face_encoding(photo_with_prefix)
    print(f"Result: {result['message']}")
    print(f"  - success: {result['success']}")
    print(f"  - face_count: {result['face_count']}")
    
    if result['success']:
        encoding = json.loads(result['encoding'])
        import numpy as np
        print(f"  - encoding shape: {np.array(encoding).shape}")
        print(f"  - encoding size: {len(result['encoding'])} bytes")
        print("✓ Face encoding generation successful!")
        
        # Store for next step
        test_encoding = result['encoding']
    else:
        print(f"✗ Face encoding failed")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test POST request to registration endpoint
print("Step 3: Testing registration endpoint...")
print("-" * 40)
try:
    api_url = "http://localhost:5000/gate-entry/register"
    
    payload = {
        "name": "Test User",
        "phone": "9999999999",
        "photos": [photo_with_prefix]  # Send as list with base64 data URL
    }
    
    print(f"POST {api_url}")
    print(f"  - Name: {payload['name']}")
    print(f"  - Phone: {payload['phone']}")
    print(f"  - Photos: {len(payload['photos'])} photos")
    print(f"  - Photo size: {len(payload['photos'][0])} bytes")
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers, timeout=10)
    
    print(f"\nResponse: HTTP {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        print("✓ Registration successful!")
        user_id = result.get('user_id')
        has_face_encoding = result.get('has_face_encoding')
        face_count = result.get('face_encodings_count', 0)
        print(f"  - User ID: {user_id}")
        print(f"  - Has face encoding: {has_face_encoding}")
        print(f"  - Face encodings count: {face_count}")
    else:
        print(f"✗ Registration failed: {result.get('message')}")
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API at localhost:5000")
    print("  Is the Flask app running?")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)