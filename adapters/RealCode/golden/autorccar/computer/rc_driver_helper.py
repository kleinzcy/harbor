import cv2
import math
import serial


class RCControl:
    """Control the movement of the RC car through the serial port."""

    def __init__(self, serial_port):
        """
        Initialize the RC control.

        Parameters:
        - serial_port (str): The path to the serial port device, e.g., "/dev/tty.usbmodem1421"
        """
        self.serial_port = serial_port
        self.ser = None

        # For testing without actual hardware, we'll simulate serial communication
        try:
            self.ser = serial.Serial(serial_port, 115200, timeout=1)
            print(f"Connected to serial port: {serial_port}")
        except (serial.SerialException, FileNotFoundError):
            print(f"Warning: Could not open serial port {serial_port}. Running in simulation mode.")
            self.ser = None

    def steer(self, prediction):
        """
        Send steering command based on prediction.

        Parameters:
        - prediction (int): The predicted action label
          - 0: Left turn
          - 1: Right turn
          - 2: Forward
          - Other: Stop
        """
        if prediction == 2:  # Forward
            command = b'1'
            print("Forward")
        elif prediction == 0:  # Left turn
            command = b'7'
            print("Left")
        elif prediction == 1:  # Right turn
            command = b'6'
            print("Right")
        else:  # Stop
            self.stop()
            return

        if self.ser is not None:
            self.ser.write(command)

    def stop(self):
        """Send stop command."""
        command = b'0'
        print("Stop")
        if self.ser is not None:
            self.ser.write(command)


class DistanceToCamera:
    """Calculate the distance from the target object to the camera based on camera parameters."""

    def __init__(self):
        # Camera parameters (obtained through manual measurement and calibration)
        self.alpha = 8.0 * math.pi / 180    # Camera viewing angle (in radians)
        self.v0 = 119.865631204             # Camera matrix parameter v0
        self.ay = 332.262498472             # Camera matrix parameter ay

    def calculate(self, v, h, x_shift, image):
        """
        Calculate distance from camera to object.

        Parameters:
        - v (float): The vertical coordinate of the target point in the image
        - h (float): The actual height of the target object (in centimeters)
        - x_shift (int): The X-axis offset for text display
        - image (np.ndarray): The image array for displaying distance information

        Returns:
        - float: The calculated distance (in centimeters)
        """
        if v <= 0:
            return 0

        # Compute distance using camera geometry
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))

        # Draw distance on image if provided
        if d > 0 and image is not None:
            cv2.putText(image, "%.1fcm" % d,
                        (image.shape[1] - x_shift, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return d


class ObjectDetection:
    """Detect stop signs and traffic lights using a cascade classifier."""

    def __init__(self):
        # Traffic light status flags
        self.red_light = False      # Red light detection flag
        self.green_light = False    # Green light detection flag
        self.yellow_light = False   # Yellow light detection flag

    def detect(self, cascade_classifier, gray_image, image, threshold=100):
        """
        Detect objects using a cascade classifier.

        Parameters:
        - cascade_classifier: An OpenCV cascade classifier object
        - gray_image (np.ndarray): A grayscale image
        - image (np.ndarray): A color image for drawing the detection results
        - threshold (int): Brightness threshold for traffic light detection

        Returns:
        - int: The Y-coordinate of the bottom of the detected object, returning 0 if no object is detected
        """
        if cascade_classifier is None:
            return 0

        # Detect objects
        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        v = 0
        for (x_pos, y_pos, width, height) in cascade_obj:
            # Draw rectangle around detected object
            cv2.rectangle(image, (x_pos + 5, y_pos + 5),
                          (x_pos + width - 5, y_pos + height - 5),
                          (255, 255, 255), 2)

            v = y_pos + height - 5

            # Check if it's a stop sign or traffic light
            if width / height == 1:  # Stop sign (square aspect ratio)
                cv2.putText(image, 'STOP', (x_pos, y_pos - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:  # Traffic light
                # Extract ROI for traffic light analysis
                roi = gray_image[y_pos + 10:y_pos + height - 10,
                                 x_pos + 10:x_pos + width - 10]

                # Apply Gaussian blur
                mask = cv2.GaussianBlur(roi, (25, 25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)

                # Check if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

                    # Determine light color based on vertical position
                    # Red light: upper third
                    if 1.0 / 8 * (height - 30) < maxLoc[1] < 4.0 / 8 * (height - 30):
                        cv2.putText(image, 'Red', (x_pos + 5, y_pos - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        self.red_light = True

                    # Green light: lower third
                    elif 5.5 / 8 * (height - 30) < maxLoc[1] < height - 30:
                        cv2.putText(image, 'Green', (x_pos + 5, y_pos - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        self.green_light = True

                    # Yellow light: middle
                    else:
                        cv2.putText(image, 'Yellow', (x_pos + 5, y_pos - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        self.yellow_light = True

        return v

    def reset_lights(self):
        """Reset all traffic light detection flags."""
        self.red_light = False
        self.green_light = False
        self.yellow_light = False


# Helper function to load cascade classifiers
def load_cascade_classifiers(stop_sign_path="cascade_xml/stop_sign.xml",
                             traffic_light_path="cascade_xml/traffic_light.xml"):
    """
    Load cascade classifiers for stop signs and traffic lights.

    Parameters:
    - stop_sign_path (str): Path to stop sign cascade classifier
    - traffic_light_path (str): Path to traffic light cascade classifier

    Returns:
    - tuple: (stop_cascade, light_cascade)
    """
    stop_cascade = None
    light_cascade = None

    try:
        stop_cascade = cv2.CascadeClassifier(stop_sign_path)
        if stop_cascade.empty():
            print(f"Warning: Could not load stop sign cascade from {stop_sign_path}")
            stop_cascade = None
    except Exception as e:
        print(f"Error loading stop sign cascade: {e}")

    try:
        light_cascade = cv2.CascadeClassifier(traffic_light_path)
        if light_cascade.empty():
            print(f"Warning: Could not load traffic light cascade from {traffic_light_path}")
            light_cascade = None
    except Exception as e:
        print(f"Error loading traffic light cascade: {e}")

    return stop_cascade, light_cascade


if __name__ == "__main__":
    # Test the module
    print("rc_driver_helper module loaded successfully")
    print(f"RCControl class: {RCControl.__doc__}")
    print(f"DistanceToCamera class: {DistanceToCamera.__doc__}")
    print(f"ObjectDetection class: {ObjectDetection.__doc__}")