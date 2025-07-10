from ultralytics import YOLO
import cv2
import os
import time
import serial  # Add this import for Arduino communication
import numpy as np

# Get the directory of the current script to build absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the custom-trained helmet detection model
MODEL_PATH = os.path.join(script_dir, '..', 'models', 'best.pt')

# The model has 2 classes: 'With Helmet', 'Without Helmet'.
# CORRECTED MAPPING based on data.yaml:
CLASS_NAMES = {0: 'With Helmet', 1: 'Without Helmet'}

def classify_helmet_usage(image_path):
    """
    Analyzes an image to determine helmet usage.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    # Load the custom YOLOv8 model
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}. Make sure the file exists.")
        print(f"Details: {e}")
        return

    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image from {image_path}")
        return

    # Convert BGR to RGB before inference
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Perform inference
    results = model(img_rgb)

    # Process the results
    detections = results[0].boxes.data
    
    # Flags to check detection status
    helmet_detected = False
    no_helmet_detected = False
    total_detections = len(detections)

    print("\n" + "="*60)
    print("HELMET DETECTION TEST RESULTS")
    print("="*60)
    print(f"Total detections found: {total_detections}")
    
    # Show ALL detections first (for debugging)
    print("\n--- ALL DETECTIONS (including low confidence) ---")
    for i, det in enumerate(detections):
        x1, y1, x2, y2, confidence, class_id = det
        class_id = int(class_id)
        class_name = CLASS_NAMES.get(class_id, 'unknown')
        print(f"Detection {i+1}: {class_name} (confidence: {confidence:.3f})")
    
    print("\n--- HIGH CONFIDENCE DETECTIONS (>0.5) ---")
    # Process detections
    for det in detections:
        # det is a tensor like [x1, y1, x2, y2, confidence, class_id]
        x1, y1, x2, y2, confidence, class_id = det
        class_id = int(class_id)
        class_name = CLASS_NAMES.get(class_id, 'unknown')
        
        # Only consider detections with confidence > 0.5
        if confidence > 0.5:
            if class_name == 'With Helmet':
                helmet_detected = True
                print(f"🟢 With Helmet detected (confidence: {confidence:.2f})")
            elif class_name == 'Without Helmet':
                no_helmet_detected = True
                print(f"🔴 Without Helmet detected (confidence: {confidence:.2f})")
            else:
                print(f"❓ Unknown object detected (confidence: {confidence:.2f})")
        else:
            print(f"⚠️ Low confidence detection ignored: {class_name} (confidence: {confidence:.2f})")

    if total_detections == 0:
        print("⚠️ No objects detected in the image")
        print("💡 This could mean:")
        print("   • The image is too dark or blurry")
        print("   • The person is too far from the camera")
        print("   • The model needs better training data")
        print("   • Try adjusting lighting or position")

    # --- Classification Logic (REVISED for 2-class model) ---
    # This model detects: 'With Helmet' vs 'Without Helmet'
    output_message = ""
    if helmet_detected and not no_helmet_detected:
        # If only "With Helmet" is detected
        output_message = "✅ Helmet worn correctly"
    elif no_helmet_detected and not helmet_detected:
        # If only "Without Helmet" is detected
        output_message = "❌ No helmet detected — wear a helmet for safety"
    elif helmet_detected and no_helmet_detected:
        # If both are detected (conflicting results)
        output_message = "⚠️ Conflicting detection results"
    else:
        # If neither is detected
        output_message = "Could not determine helmet status."

    print(f"Result for {os.path.basename(image_path)}: {output_message}")
    
    # Initialize serial connection to Arduino
    # Change 'COM3' to your Arduino's port if needed (see Device Manager or Arduino IDE)
    try:
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        arduino_connected = True
        print("✅ Arduino connected successfully!")
    except Exception as e:
        print(f"Warning: Could not connect to Arduino on COM3.\nDetails: {e}\nProceeding without Arduino integration.")
        arduino_connected = False

    # Determine final helmet status and send to Arduino
    print("\n" + "-"*60)
    print("FINAL TEST RESULT")
    print("-"*60)
    
    # FIXED LOGIC: Only PASS if helmet is detected with high confidence
    if helmet_detected and not no_helmet_detected:
        status = "✅ HELMET WORN CORRECTLY"
        print(f"🎯 {status}")
        print("   Safety compliance: PASSED ✅")
        print("   Status: SAFE TO PROCEED")
        result_summary = "PASS"
        arduino_signal = b'1'  # Send '1' to Arduino
    elif no_helmet_detected and not helmet_detected:
        status = "❌ NO HELMET DETECTED"
        print(f"🎯 {status}")
        print("   Safety compliance: FAILED ❌")
        print("   ⚠️  Please wear a helmet for safety!")
        print("   Status: UNSAFE - HELMET REQUIRED")
        result_summary = "FAIL"
        arduino_signal = b'0'  # Send '0' to Arduino
    elif helmet_detected and no_helmet_detected:
        status = "⚠️ CONFLICTING DETECTION RESULTS"
        print(f"🎯 {status}")
        print("   Safety compliance: UNCERTAIN ⚠️")
        print("   💡 Try adjusting your position or lighting")
        print("   Status: NEEDS VERIFICATION")
        result_summary = "CONFLICT"
        arduino_signal = b'0'  # Treat as fail for safety
    else:
        # If neither is detected, treat as FAIL (no helmet)
        status = "❓ NO HELMET-RELATED OBJECTS DETECTED"
        print(f"🎯 {status}")
        print("   Safety compliance: FAILED ❌ (No helmet detected)")
        print("   💡 TROUBLESHOOTING TIPS:")
        print("      • Make sure your face/head is clearly visible")
        print("      • Ensure good lighting (avoid shadows)")
        print("      • Position yourself 2-3 feet from camera")
        print("      • Try wearing or removing a helmet")
        print("      • Check if camera is working properly")
        print("   Status: UNSAFE - NO HELMET DETECTED")
        result_summary = "FAIL"
        arduino_signal = b'0'  # Treat as fail for safety

    # Send result to Arduino if connected
    if arduino_connected:
        try:
            print(f"[ARDUINO] Sending signal: {arduino_signal.decode()} (1=PASS, 0=FAIL)")
            arduino.write(arduino_signal)
            print("[ARDUINO] Signal sent successfully")
            
            # Wait longer and check for Arduino response
            time.sleep(2)  # Give Arduino more time to process
            
            # Try to read Arduino response
            if arduino.in_waiting:
                response = arduino.readline().decode().strip()
                print(f"[ARDUINO] Response: {response}")
            else:
                print("[ARDUINO] No response from Arduino")
                
            # Keep connection open a bit longer for buzzer to complete
            time.sleep(1)
            
        except Exception as e:
            print(f"[ARDUINO] Error sending signal: {e}")
        finally:
            arduino.close()
            print("[ARDUINO] Connection closed")
    else:
        print("[ARDUINO] No Arduino connection - skipping hardware control")

    # === Save result frame with bounding boxes and labels ===
    save_choice = input("Do you want to save the test frame? (y/n): ").lower().strip()
    if save_choice in ['y', 'yes']:
        result_frame = img.copy()
        for det in detections:
            x1, y1, x2, y2, confidence, class_id = det
            class_id = int(class_id)
            class_name = CLASS_NAMES.get(class_id, 'unknown')
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            if class_name == 'With Helmet':
                color = (0, 255, 0)
            elif class_name == 'Without Helmet':
                color = (0, 0, 255)
            else:
                color = (128, 128, 128)
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(result_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(result_frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(result_frame, f"Result: {result_summary}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"helmet_test_{result_summary}_{timestamp}.jpg"
        save_path = os.path.join(script_dir, '..', 'input', filename)
        try:
            cv2.imwrite(save_path, result_frame)
            print(f"✅ Test frame saved as: {filename}")
            print(f"📁 Location: {save_path}")
        except Exception as e:
            print(f"❌ Error saving frame: {e}")
    else:
        print("Test frame not saved.")
    return output_message

def live_helmet_detection():
    """
    Automatic helmet detection using webcam - no GUI, automatic capture.
    Now sends result to Arduino Uno via serial (COM3 by default).
    """
    # Load the custom YOLOv8 model
    try:
        model = YOLO(MODEL_PATH)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model from {MODEL_PATH}. Make sure the file exists.")
        print(f"Details: {e}")
        return
    # Initialize webcam
    cap = cv2.VideoCapture(0)  # 0 for default camera
    
    # Try different camera index if 0 doesn't work
    if not cap.isOpened():
        print("Trying camera index 1...")
        cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("Trying camera index 2...")
        cap = cv2.VideoCapture(2)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        print("Try:")
        print("1. Close other applications using the camera")
        print("2. Restart your computer")
        print("3. Check camera drivers")
        return

    # Set enhanced camera properties for better detection
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Enable auto exposure
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)  # Set brightness to middle
    cap.set(cv2.CAP_PROP_CONTRAST, 0.5)  # Set contrast to middle
    
    # Test camera by reading a frame
    ret, test_frame = cap.read()
    if not ret:
        print("Error: Could not read frame from webcam")
        cap.release()
        return
    
    print(f"Camera initialized successfully. Frame size: {test_frame.shape}")
    
    # Enhanced image quality analysis
    mean_brightness = test_frame.mean()
    gray_test = cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)
    contrast = gray_test.std()
    blur_level = cv2.Laplacian(gray_test, cv2.CV_64F).var()
    
    print(f"Image brightness: {mean_brightness:.1f}")
    print(f"Image contrast: {contrast:.1f}")
    print(f"Blur level: {blur_level:.1f}")
    
    # Determine optimal detection parameters based on image quality
    if mean_brightness < 60:
        confidence_threshold = 0.3  # Lower threshold for dark images
        print("⚠️ WARNING: Image appears too dark - using lower confidence threshold")
    elif mean_brightness < 100:
        confidence_threshold = 0.4  # Lower threshold for low light
        print("⚠️ WARNING: Image appears dim - using lower confidence threshold")
    elif blur_level < 100:
        confidence_threshold = 0.4  # Lower threshold for blurry images
        print("⚠️ WARNING: Image appears blurry - using lower confidence threshold")
    else:
        confidence_threshold = 0.5  # Standard threshold for good conditions
        print("✅ Image quality looks good")

    print("Automatic helmet detection starting...")
    print("Position yourself in front of the camera")
    print("Frame will be captured automatically in 5 seconds...")
    print("\n📋 POSITIONING TIPS FOR BETTER DETECTION:")
    print("   • Sit 2-3 feet from the camera")
    print("   • Ensure your face/head is clearly visible")
    print("   • Make sure you have good lighting")
    print("   • Avoid shadows on your face")
    print("   • Look directly at the camera")
    print("   • If wearing a helmet, make sure it's visible")
    print("   • If not wearing a helmet, make sure your head is visible")
    print()

    # Countdown and capture frame
    for i in range(5, 0, -1):
        print(f"Capturing frame in {i} seconds...")
        time.sleep(1)
        
        # Read frame to keep camera active
        ret, _ = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam")
            cap.release()
            return

    # Capture multiple frames and select the best one
    print("Capturing frame now...")
    best_frame = None
    best_quality = 0
    
    # Capture 3 frames and select the best quality one
    for attempt in range(3):
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame {attempt + 1}")
            continue
            
        # Calculate frame quality
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_brightness = gray_frame.mean()
        frame_contrast = gray_frame.std()
        frame_blur = cv2.Laplacian(gray_frame, cv2.CV_64F).var()
        
        # Quality score (higher is better)
        quality_score = frame_contrast + frame_blur * 0.1  # Prioritize contrast and sharpness
        
        if quality_score > best_quality:
            best_quality = quality_score
            best_frame = frame.copy()
            print(f"Frame {attempt + 1}: Quality score {quality_score:.1f} (selected)")
        else:
            print(f"Frame {attempt + 1}: Quality score {quality_score:.1f}")
    
    cap.release()
    
    if best_frame is None:
        print("Error: Could not capture any valid frame")
        return
    
    print(f"Selected frame with quality score: {best_quality:.1f}")
    print("Processing captured frame...")
    
    # Enhanced preprocessing for better detection
    processed_frame = best_frame.copy()
    
    # Apply adaptive preprocessing based on image quality
    if mean_brightness < 100:  # Low light condition
        # Enhance brightness and contrast
        lab = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        processed_frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        processed_frame = cv2.convertScaleAbs(processed_frame, alpha=1.2, beta=20)
        print("Applied brightness and contrast enhancement")
    
    if blur_level < 150:  # Blurry condition
        # Apply sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        processed_frame = cv2.filter2D(processed_frame, -1, kernel)
        print("Applied image sharpening")
    
    # Convert BGR to RGB before inference
    processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
    results = model(processed_frame_rgb)
    
    # Debug: Print raw results
    print(f"Model returned {len(results)} result(s)")
    if len(results) > 0:
        print(f"First result has {len(results[0].boxes)} detections")
        print(f"Detection data shape: {results[0].boxes.data.shape if hasattr(results[0].boxes, 'data') else 'No data'}")
    
    # Process the results
    detections = results[0].boxes.data
    
    # Flags to check detection status
    helmet_detected = False
    no_helmet_detected = False
    total_detections = len(detections)

    print("\n" + "="*60)
    print("HELMET DETECTION TEST RESULTS")
    print("="*60)
    print(f"Total detections found: {total_detections}")
    
    # Show ALL detections first (for debugging)
    print("\n--- ALL DETECTIONS (including low confidence) ---")
    for i, det in enumerate(detections):
        x1, y1, x2, y2, confidence, class_id = det
        class_id = int(class_id)
        class_name = CLASS_NAMES.get(class_id, 'unknown')
        print(f"Detection {i+1}: {class_name} (confidence: {confidence:.3f})")
    
    print(f"\n--- HIGH CONFIDENCE DETECTIONS (>{confidence_threshold:.1f}) ---")
    # Process detections with adaptive threshold
    for det in detections:
        # det is a tensor like [x1, y1, x2, y2, confidence, class_id]
        x1, y1, x2, y2, confidence, class_id = det
        class_id = int(class_id)
        class_name = CLASS_NAMES.get(class_id, 'unknown')
        
        # Use adaptive confidence threshold based on image quality
        if confidence > confidence_threshold:
            if class_name == 'With Helmet':
                helmet_detected = True
                print(f"🟢 With Helmet detected (confidence: {confidence:.2f})")
            elif class_name == 'Without Helmet':
                no_helmet_detected = True
                print(f"🔴 Without Helmet detected (confidence: {confidence:.2f})")
            else:
                print(f"❓ Unknown object detected (confidence: {confidence:.2f})")
        else:
            print(f"⚠️ Low confidence detection ignored: {class_name} (confidence: {confidence:.2f})")

    if total_detections == 0:
        print("⚠️ No objects detected in the image")
        print("💡 This could mean:")
        print("   • The image is too dark or blurry")
        print("   • The person is too far from the camera")
        print("   • The model needs better training data")
        print("   • Try adjusting lighting or position")

    # Initialize serial connection to Arduino
    # Change 'COM3' to your Arduino's port if needed (see Device Manager or Arduino IDE)
    try:
        arduino = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        arduino_connected = True
    except Exception as e:
        print(f"Warning: Could not connect to Arduino on COM3.\nDetails: {e}\nProceeding without Arduino integration.")
        arduino_connected = False

    # Determine and display final helmet status
    print("\n" + "-"*60)
    print("FINAL TEST RESULT")
    print("-"*60)
    
    # FIXED LOGIC: Only PASS if helmet is detected with high confidence
    if helmet_detected and not no_helmet_detected:
        status = "✅ HELMET WORN CORRECTLY"
        print(f"🎯 {status}")
        print("   Safety compliance: PASSED ✅")
        print("   Status: SAFE TO PROCEED")
        result_summary = "PASS"
        arduino_signal = b'1'  # Send '1' to Arduino
    elif no_helmet_detected and not helmet_detected:
        status = "❌ NO HELMET DETECTED"
        print(f"🎯 {status}")
        print("   Safety compliance: FAILED ❌")
        print("   ⚠️  Please wear a helmet for safety!")
        print("   Status: UNSAFE - HELMET REQUIRED")
        result_summary = "FAIL"
        arduino_signal = b'0'  # Send '0' to Arduino
    elif helmet_detected and no_helmet_detected:
        status = "⚠️ CONFLICTING DETECTION RESULTS"
        print(f"🎯 {status}")
        print("   Safety compliance: UNCERTAIN ⚠️")
        print("   💡 Try adjusting your position or lighting")
        print("   Status: NEEDS VERIFICATION")
        result_summary = "CONFLICT"
        arduino_signal = b'0'  # Treat as fail for safety
    else:
        # If neither is detected, treat as FAIL (no helmet)
        status = "❓ NO HELMET-RELATED OBJECTS DETECTED"
        print(f"🎯 {status}")
        print("   Safety compliance: FAILED ❌ (No helmet detected)")
        print("   💡 TROUBLESHOOTING TIPS:")
        print("      • Make sure your face/head is clearly visible")
        print("      • Ensure good lighting (avoid shadows)")
        print("      • Position yourself 2-3 feet from camera")
        print("      • Try wearing or removing a helmet")
        print("      • Check if camera is working properly")
        print("   Status: UNSAFE - NO HELMET DETECTED")
        result_summary = "FAIL"
        arduino_signal = b'0'  # Treat as fail for safety

    # Send result to Arduino if connected
    if arduino_connected:
        try:
            arduino.write(arduino_signal)
            print(f"[ARDUINO] Sent signal: {arduino_signal.decode()} (1=PASS, 0=FAIL)")
        except Exception as e:
            print(f"[ARDUINO] Error sending signal: {e}")

    # Ask if user wants to save the test frame
    print("\n" + "="*60)
    save_choice = input("Do you want to save the test frame? (y/n): ").lower().strip()
    
    if save_choice in ['y', 'yes']:
        # Create a copy of frame for drawing results
        result_frame = frame.copy()
        
        # Draw detection results on frame
        for det in detections:
            x1, y1, x2, y2, confidence, class_id = det
            class_id = int(class_id)
            class_name = CLASS_NAMES.get(class_id, 'unknown')
            
            # Convert coordinates to integers
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            if class_name == 'With Helmet':
                color = (0, 255, 0)  # Green
            elif class_name == 'Without Helmet':
                color = (0, 0, 255)  # Red
            else:
                color = (128, 128, 128)  # Gray
            
            # Draw bounding box
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)
            
            # Add label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(result_frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Add final result to frame
        cv2.putText(result_frame, status, (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(result_frame, f"Result: {result_summary}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Save the frame
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"helmet_test_{result_summary}_{timestamp}.jpg"
        save_path = os.path.join(script_dir, '..', 'input', filename)
        
        try:
            cv2.imwrite(save_path, result_frame)
            print(f"✅ Test frame saved as: {filename}")
            print(f"📁 Location: {save_path}")
        except Exception as e:
            print(f"❌ Error saving frame: {e}")
    else:
        print("Test frame not saved.")

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  For image detection: python detect.py <path_to_image>")
        print("  For live webcam detection: python detect.py --webcam")
        sys.exit(1)
    
    if sys.argv[1] == "--webcam":
        live_helmet_detection()
    else:
        image_to_test = sys.argv[1]
        classify_helmet_usage(image_to_test) 