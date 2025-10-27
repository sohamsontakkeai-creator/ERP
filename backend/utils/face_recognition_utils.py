"""
Face Recognition Utilities using face_recognition library
Handles face encoding generation and comparison
"""
import base64
import io
import json
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


# Try to import OpenCV
try:
    import cv2
    FACE_RECOGNITION_AVAILABLE = True
    logger.info("OpenCV (cv2) library loaded successfully")
except ImportError as e:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning(f"OpenCV (cv2) library not available. Face recognition features will be disabled. Error: {e}")


def is_face_recognition_available():
    """Check if face recognition is available"""
    return FACE_RECOGNITION_AVAILABLE


def base64_to_image(base64_string):
    """Convert base64 string to PIL Image"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        logger.error(f"Error converting base64 to image: {e}")
        return None


def image_to_numpy(image):
    """Convert PIL Image to numpy array"""
    try:
        return np.array(image)
    except Exception as e:
        logger.error(f"Error converting image to numpy: {e}")
        return None


def generate_face_encoding(photo_base64):
    """
    Generate face encoding from base64 photo using face_recognition library
    
    Args:
        photo_base64: Base64 encoded photo string
        
    Returns:
        dict: {
            'success': bool,
            'encoding': str (JSON serialized numpy array) or None,
            'message': str,
            'face_count': int
        }
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {
            'success': False,
            'encoding': None,
            'message': 'OpenCV (cv2) library not available. Please install: pip install opencv-python',
            'face_count': 0
        }
    if not photo_base64:
        return {
            'success': False,
            'encoding': None,
            'message': 'No photo provided',
            'face_count': 0
        }
    try:
        image = base64_to_image(photo_base64)
        if image is None:
            return {
                'success': False,
                'encoding': None,
                'message': 'Failed to decode image',
                'face_count': 0
            }
        image_array = image_to_numpy(image)
        if image_array is None:
            return {
                'success': False,
                'encoding': None,
                'message': 'Failed to convert image to array',
                'face_count': 0
            }
        # Convert to grayscale for OpenCV
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        # Use Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Use more lenient parameters for better detection
        # scaleFactor: lower = more sensitive but slower (1.05-1.1 is good)
        # minNeighbors: lower = more sensitive but more false positives (3-5 is good)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30))
        face_count = len(faces)
        if face_count == 0:
            return {
                'success': False,
                'encoding': None,
                'message': 'No face detected in the photo. Please ensure your face is clearly visible.',
                'face_count': 0
            }
        if face_count > 1:
            return {
                'success': False,
                'encoding': None,
                'message': f'Multiple faces detected ({face_count}). Please ensure only one face is in the photo.',
                'face_count': face_count
            }
        # Crop the face region
        (x, y, w, h) = faces[0]
        face_img = gray[y:y+h, x:x+w]
        # Resize to a standard size for encoding
        face_img = cv2.resize(face_img, (100, 100))
        # Serialize the face image as encoding
        encoding_json = json.dumps(face_img.tolist())
        logger.info(f"Successfully generated face encoding (OpenCV LBPH)")
        return {
            'success': True,
            'encoding': encoding_json,
            'message': 'Face encoding generated successfully',
            'face_count': 1
        }
    except Exception as e:
        logger.error(f"Error generating face encoding: {e}")
        return {
            'success': False,
            'encoding': None,
            'message': f'Error processing face: {str(e)}',
            'face_count': 0
        }


def compare_faces(known_encoding_json, unknown_photo_base64, tolerance=0.6):
    """
    Compare a known face encoding with an unknown photo
    
    Args:
        known_encoding_json: JSON string of known face encoding
        unknown_photo_base64: Base64 encoded photo to compare
        tolerance: Distance tolerance for matching (lower = more strict, default 0.6)
        
    Returns:
        dict: {
            'success': bool,
            'match': bool,
            'distance': float,
            'message': str
        }
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {
            'success': False,
            'match': False,
            'distance': None,
            'message': 'Face recognition library not available'
        }
    
    try:
        # Load known encoding (face image)
        known_face_img = np.array(json.loads(known_encoding_json), dtype=np.uint8)
        # Generate encoding for unknown photo
        result = generate_face_encoding(unknown_photo_base64)
        if not result['success']:
            return {
                'success': False,
                'match': False,
                'distance': None,
                'message': result['message']
            }
        unknown_face_img = np.array(json.loads(result['encoding']), dtype=np.uint8)
        # Use LBPHFaceRecognizer for comparison
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train([known_face_img], np.array([0]))
        label, confidence = recognizer.predict(unknown_face_img)
        match = confidence < (tolerance * 100)  # Lower confidence means better match
        logger.info(f"Face comparison: match={match}, confidence={confidence:.2f}, tolerance={tolerance}")
        return {
            'success': True,
            'match': match,
            'distance': confidence,
            'message': 'Face matched!' if match else 'Face does not match'
        }
    except Exception as e:
        logger.error(f"Error comparing faces: {e}")
        return {
            'success': False,
            'match': False,
            'distance': None,
            'message': f'Error comparing faces: {str(e)}'
        }


def recognize_face_from_database(unknown_photo_base64, known_faces_dict, tolerance=0.7):
    """
    Recognize a face from a database of known faces
    Properly handles multiple encodings per user (all 7 encodings used for training)
    
    Args:
        unknown_photo_base64: Base64 encoded photo to recognize
        known_faces_dict: Dict of {user_id: face_encoding_json}
        tolerance: Distance tolerance for matching (lower = more strict, default 0.7 = 70% confidence threshold)
        
    Returns:
        dict: {
            'success': bool,
            'recognized': bool,
            'user_id': int or None,
            'distance': float or None,
            'message': str
        }
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return {
            'success': False,
            'recognized': False,
            'user_id': None,
            'distance': None,
            'message': 'Face recognition library not available'
        }
    
    if not known_faces_dict:
        return {
            'success': False,
            'recognized': False,
            'user_id': None,
            'distance': None,
            'message': 'No registered faces in database'
        }
    
    try:
        logger.info("=" * 80)
        logger.info("RECOGNIZE_FACE_FROM_DATABASE: Starting recognition")
        logger.info("=" * 80)
        
        result = generate_face_encoding(unknown_photo_base64)
        if not result['success']:
            return {
                'success': False,
                'recognized': False,
                'user_id': None,
                'distance': None,
                'message': result['message']
            }
        unknown_face_img = np.array(json.loads(result['encoding']), dtype=np.uint8)
        logger.info(f"Unknown face image shape: {unknown_face_img.shape}")
        
        # Prepare training data for LBPH recognizer
        # IMPORTANT: Use ALL encodings from each user (not just the first one!)
        train_imgs = []
        train_labels = []
        user_id_to_label = {}  # Map user_id to label
        
        for user_id, encoding_json in known_faces_dict.items():
            if not encoding_json:
                continue
                
            try:
                # Parse the encoding - it could be single or multiple encodings
                encoding_data = json.loads(encoding_json)
                
                logger.info(f"\n📊 Processing user {user_id}:")
                logger.info(f"   Encoding data type: {type(encoding_data)}")
                
                # Check if this is multiple encodings (7 photos) or single encoding
                if isinstance(encoding_data, list) and len(encoding_data) > 0:
                    # Check if first item is also a list (indicating multiple encodings)
                    if isinstance(encoding_data[0], list) and len(encoding_data[0]) > 0:
                        if isinstance(encoding_data[0][0], list):
                            # Multiple encodings: [[[...], [...]], [[...], [...]]]
                            logger.info(f"   ✅ Multiple encodings detected: {len(encoding_data)} encodings")
                            
                            # Assign a unique label for this user
                            label = len(user_id_to_label)
                            user_id_to_label[label] = user_id
                            
                            # ADD ALL ENCODINGS for training (not just first one!)
                            for encoding_idx, single_encoding in enumerate(encoding_data):
                                try:
                                    known_face_img = np.array(single_encoding, dtype=np.uint8)
                                    if known_face_img.shape == (100, 100):
                                        train_imgs.append(known_face_img)
                                        train_labels.append(label)
                                        logger.info(f"     Encoding {encoding_idx + 1}: ✅ Added (shape: {known_face_img.shape})")
                                    else:
                                        logger.warning(f"     Encoding {encoding_idx + 1}: ❌ Invalid shape {known_face_img.shape}")
                                except Exception as e:
                                    logger.warning(f"     Encoding {encoding_idx + 1}: ❌ Error: {e}")
                        else:
                            # Single encoding: [[...], [...]]
                            logger.info(f"   ✅ Single encoding detected")
                            label = len(user_id_to_label)
                            user_id_to_label[label] = user_id
                            known_face_img = np.array(encoding_data, dtype=np.uint8)
                            if known_face_img.shape == (100, 100):
                                train_imgs.append(known_face_img)
                                train_labels.append(label)
                                logger.info(f"     ✅ Added (shape: {known_face_img.shape})")
                            else:
                                logger.warning(f"     ❌ Invalid shape {known_face_img.shape}")
                    else:
                        logger.warning(f"   ❌ Invalid encoding structure for user {user_id}")
                else:
                    logger.warning(f"   ❌ Invalid encoding format for user {user_id}")
                    
            except Exception as e:
                logger.warning(f"   ❌ Failed to load encoding for user {user_id}: {e}")
        
        logger.info(f"\n📈 Training data prepared:")
        logger.info(f"   Total training images: {len(train_imgs)}")
        logger.info(f"   Total users: {len(user_id_to_label)}")
        
        if not train_imgs:
            return {
                'success': False,
                'recognized': False,
                'user_id': None,
                'distance': None,
                'message': 'No valid face encodings in database'
            }
        
        # Train LBPH recognizer with all encodings
        logger.info(f"\n🔧 Training LBPH recognizer with {len(train_imgs)} images...")
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(train_imgs, np.array(train_labels))
        logger.info("✅ Recognizer trained successfully")
        
        # Predict
        logger.info(f"\n🔍 Predicting face match...")
        label, confidence = recognizer.predict(unknown_face_img)
        logger.info(f"   Predicted label: {label}, confidence: {confidence:.2f}")
        logger.info(f"   Tolerance threshold: {tolerance * 100:.2f}")
        
        # Check if prediction is valid
        # LBPH confidence: lower is better, so lower threshold = stricter matching
        confidence_threshold = tolerance * 100
        match = confidence < confidence_threshold
        logger.info(f"   Match result: {match} (confidence {confidence:.2f} < threshold {confidence_threshold:.2f})")
        best_match_user_id = user_id_to_label.get(label) if match else None
        
        logger.info(f"\n✨ Recognition result:")
        logger.info(f"   Match: {match}")
        logger.info(f"   User ID: {best_match_user_id}")
        logger.info(f"   Confidence: {confidence:.2f}")
        logger.info("=" * 80)
        
        return {
            'success': True,
            'recognized': match,
            'user_id': best_match_user_id,
            'distance': confidence,
            'message': f'Face recognized (confidence: {100-confidence:.1f}%)' if match else 'Face not recognized. Please try again or use manual entry.'
        }
    except Exception as e:
        logger.error(f"Error recognizing face: {e}", exc_info=True)
        return {
            'success': False,
            'recognized': False,
            'user_id': None,
            'distance': None,
            'message': f'Error recognizing face: {str(e)}'
        }


# Backward compatibility functions
def load_known_faces():
    """
    Load known faces from database
    This is a placeholder - actual implementation should query the database
    """
    logger.warning("load_known_faces() called but not implemented. Use recognize_face_from_database() instead.")
    return {}


def find_matching_face(face_encoding, known_faces, tolerance=0.6):
    """
    Find matching face from known faces
    This is a placeholder for backward compatibility
    """
    logger.warning("find_matching_face() called but deprecated. Use recognize_face_from_database() instead.")
    return None