#!/usr/bin/env python3
"""
Debug test for face recognition pipeline
Tests each step to identify where it's failing
"""
import os
import sys
import logging
from PIL import Image
import base64
import io

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from utils.database import db
from models.gate_entry import GateUser
from utils.face_recognition_utils import generate_face_encoding, recognize_face_from_database
from app import create_app

# Create app
app = create_app()

def test_pipeline():
    """Test the complete recognition pipeline"""
    
    with app.app_context():
        logger.info("=" * 80)
        logger.info("FACE RECOGNITION PIPELINE DEBUG TEST")
        logger.info("=" * 80)
        
        # Step 1: Check database
        logger.info("\n✓ STEP 1: Check database for users")
        users = GateUser.query.filter(GateUser.face_encoding.isnot(None)).all()
        logger.info(f"  Found {len(users)} users with encodings")
        
        if not users:
            logger.error("  ❌ NO USERS FOUND - REGISTER A USER FIRST!")
            return
        
        for user in users:
            encoding_len = len(str(user.face_encoding)) if user.face_encoding else 0
            logger.info(f"  - {user.name} (ID: {user.id}, Phone: {user.phone}) - Encoding size: {encoding_len} chars")
        
        # Step 2: Create a test photo from one of the registered users
        logger.info("\n✓ STEP 2: Create test photo")
        logger.info("  ⚠️  IMPORTANT: For this test to work, you need a photo of the registered user")
        logger.info("  We'll create a sample test using face detection parameters")
        
        # Let's create a simple test image with a face-like pattern
        test_image = Image.new('RGB', (200, 200), color='white')
        test_image_bytes = io.BytesIO()
        test_image.save(test_image_bytes, format='PNG')
        test_photo_base64 = base64.b64encode(test_image_bytes.getvalue()).decode()
        
        logger.info(f"  Created test image (200x200, white background)")
        logger.info(f"  Base64 length: {len(test_photo_base64)} chars")
        
        # Step 3: Test face encoding generation
        logger.info("\n✓ STEP 3: Test face encoding generation")
        logger.info("  Attempting to generate encoding from test image...")
        result = generate_face_encoding(test_photo_base64)
        
        logger.info(f"  Success: {result['success']}")
        logger.info(f"  Message: {result['message']}")
        logger.info(f"  Face count: {result['face_count']}")
        
        if not result['success']:
            logger.warning("  ⚠️  Face detection failed (this is expected for the test image)")
            logger.warning("  This means the face detection parameters might need adjustment")
            logger.warning("  Current parameters: scaleFactor=1.1, minNeighbors=5")
            return
        
        # Step 4: Test recognition
        logger.info("\n✓ STEP 4: Test face recognition")
        known_faces = {user.id: user.face_encoding for user in users}
        logger.info(f"  Testing with {len(known_faces)} known faces")
        
        recognition_result = recognize_face_from_database(test_photo_base64, known_faces)
        
        logger.info(f"  Success: {recognition_result['success']}")
        logger.info(f"  Recognized: {recognition_result['recognized']}")
        logger.info(f"  User ID: {recognition_result['user_id']}")
        logger.info(f"  Distance: {recognition_result['distance']}")
        logger.info(f"  Message: {recognition_result['message']}")
        
        # Step 5: Summary
        logger.info("\n" + "=" * 80)
        logger.info("RECOMMENDATIONS:")
        logger.info("=" * 80)
        
        if result['success'] and recognition_result['success']:
            logger.info("✅ Pipeline working correctly!")
            logger.info("   If recognition is not working in the UI, check:")
            logger.info("   1. Are you capturing photos of the registered user?")
            logger.info("   2. Is your face clearly visible and front-facing?")
            logger.info("   3. Is the lighting adequate?")
        else:
            logger.warning("❌ Issues detected:")
            
            if not result['success']:
                logger.warning("   - Face detection is failing")
                logger.warning("   - Try adjusting face detection parameters:")
                logger.warning("     - scaleFactor: 1.05 (more sensitive), 1.2 (less sensitive)")
                logger.warning("     - minNeighbors: 3 (more sensitive), 7 (less sensitive)")
                logger.warning("   - Or try a real photo of a person")
            
            if result['success'] and not recognition_result['success']:
                logger.warning("   - Recognition pipeline has issues")
                logger.warning("   - Check the tolerance threshold (currently 0.5)")
                logger.warning("   - Ensure training data is valid")
        
        logger.info("=" * 80)

if __name__ == '__main__':
    test_pipeline()