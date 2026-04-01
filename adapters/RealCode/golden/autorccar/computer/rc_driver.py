#!/usr/bin/env python3
"""
Main entry point for the AutoRCCar autonomous driving system.
"""

import socketserver
import threading
import time
import sys
import numpy as np
import cv2

from model import NeuralNetwork, load_data
from rc_driver_helper import RCControl, DistanceToCamera, ObjectDetection, load_cascade_classifiers


class SensorDataHandler(socketserver.BaseRequestHandler):
    """Handle ultrasonic sensor data from Raspberry Pi."""

    def handle(self):
        print(f"Sensor connection from {self.client_address[0]}")
        while True:
            try:
                data = self.request.recv(1024).decode('utf-8').strip()
                if not data:
                    break

                print(f"Sensor data: {data}")
                # Process sensor data (distance in cm)
                self.server.sensor_data = data

            except (ConnectionResetError, BrokenPipeError):
                break


class VideoStreamHandler(socketserver.StreamRequestHandler):
    """Handle video stream from Raspberry Pi camera."""

    # Object height parameters (manually measured)
    h1 = 5.5  # Stop sign height (cm)
    h2 = 5.5  # Traffic light height (cm)

    # Distance threshold configuration
    d_sensor_thresh = 30      # Ultrasonic sensor stop threshold (cm)
    d_stop_light_thresh = 25  # Stop sign and traffic light stop threshold (cm)

    # Time control parameters
    stop_start = 0            # Stop start time
    stop_finish = 0           # Stop finish time
    stop_time = 0             # Stop duration
    drive_time_after_stop = 0  # Driving time after stop

    def __init__(self, *args, **kwargs):
        # Initialize neural network
        self.nn = NeuralNetwork()

        # Load cascade classifiers
        self.stop_cascade, self.light_cascade = load_cascade_classifiers()

        # Initialize helper classes
        self.rc_car = RCControl("/dev/tty.usbmodem1421")
        self.d_to_camera = DistanceToCamera()
        self.obj_detection = ObjectDetection()

        # State variables
        self.d_stop_sign = self.d_stop_light_thresh
        self.d_light = self.d_stop_light_thresh

        super().__init__(*args, **kwargs)

    def handle(self):
        print(f"Video stream connection from {self.client_address[0]}")

        stream_bytes = b' '
        stop_flag = False
        stop_sign_active = True

        while True:
            try:
                # Read JPEG stream
                stream_bytes += self.rfile.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]

                    # Decode image
                    gray = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    if gray is None or image is None:
                        continue

                    # Extract ROI (lower half of the image)
                    height, width = gray.shape
                    roi = gray[int(height/2):height, :]

                    # Reshape for neural network
                    image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)

                    # Neural network prediction
                    prediction = self.nn.predict(image_array)[0]

                    # Object detection
                    v_param1 = 0
                    v_param2 = 0

                    if self.stop_cascade is not None:
                        v_param1 = self.obj_detection.detect(self.stop_cascade, gray, image)

                    if self.light_cascade is not None:
                        v_param2 = self.obj_detection.detect(self.light_cascade, gray, image)

                    # Distance measurement
                    if v_param1 > 0 or v_param2 > 0:
                        d1 = self.d_to_camera.calculate(v_param1, self.h1, 300, image)
                        d2 = self.d_to_camera.calculate(v_param2, self.h2, 100, image)
                        self.d_stop_sign = d1
                        self.d_light = d2

                    # Get sensor data from server
                    sensor_data = getattr(self.server, 'sensor_data', None)

                    # Decision logic
                    if sensor_data and int(sensor_data) < self.d_sensor_thresh:
                        print("Stop, obstacle in front")
                        self.rc_car.stop()
                        sensor_data = None

                    elif 0 < self.d_stop_sign < self.d_stop_light_thresh and stop_sign_active:
                        print("Stop sign ahead")
                        self.rc_car.stop()

                        # Stop for 5 seconds
                        if not stop_flag:
                            self.stop_start = cv2.getTickCount()
                            stop_flag = True

                        self.stop_finish = cv2.getTickCount()
                        self.stop_time = (self.stop_finish - self.stop_start) / cv2.getTickFrequency()
                        print(f"Stop time: {self.stop_time:.2f}s")

                        # 5 seconds later, continue driving
                        if self.stop_time > 5:
                            print("Waited for 5 seconds")
                            stop_flag = False
                            stop_sign_active = False

                    elif 0 < self.d_light < self.d_stop_light_thresh:
                        if self.obj_detection.red_light:
                            print("Red light")
                            self.rc_car.stop()
                        elif self.obj_detection.green_light:
                            print("Green light")
                            pass
                        elif self.obj_detection.yellow_light:
                            print("Yellow light flashing")
                            pass

                        self.d_light = self.d_stop_light_thresh
                        self.obj_detection.reset_lights()

                    else:
                        self.rc_car.steer(prediction)
                        self.stop_start = cv2.getTickCount()
                        self.d_stop_sign = self.d_stop_light_thresh

                    # Display image
                    cv2.imshow('AutoRCCar', image)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            except Exception as e:
                print(f"Error in video stream handler: {e}")
                break

        cv2.destroyAllWindows()


class Server:
    """Main server for handling video stream and sensor data."""

    def __init__(self, host, port1, port2):
        self.host = host
        self.port1 = port1  # Video stream port
        self.port2 = port2  # Sensor data port
        self.sensor_data = None

    def start(self):
        """Start the server threads."""
        print(f"Starting AutoRCCar server on {self.host}")
        print(f"Video stream port: {self.port1}")
        print(f"Sensor data port: {self.port2}")

        # Create server for video stream
        video_server = socketserver.TCPServer(
            (self.host, self.port1),
            VideoStreamHandler
        )
        video_server.sensor_data = self.sensor_data

        # Create server for sensor data
        sensor_server = socketserver.TCPServer(
            (self.host, self.port2),
            SensorDataHandler
        )
        sensor_server.sensor_data = self.sensor_data

        # Start threads
        video_thread = threading.Thread(target=video_server.serve_forever)
        sensor_thread = threading.Thread(target=sensor_server.serve_forever)

        video_thread.daemon = True
        sensor_thread.daemon = True

        video_thread.start()
        sensor_thread.start()

        print("Servers started. Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            video_server.shutdown()
            sensor_server.shutdown()


def main():
    """Main function for command-line usage."""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "train":
            # Train neural network
            print("Training neural network...")
            X_train, X_test, y_train, y_test = load_data(76800, "training_data/*.npz")

            nn = NeuralNetwork()
            nn.create(np.int32([76800, 32, 4]))
            nn.train(X_train, y_train)

            accuracy = nn.evaluate(X_test, y_test)
            print(f"Model accuracy: {accuracy:.2%}")

            nn.save_model("saved_model/nn_model.xml")
            print("Model saved to saved_model/nn_model.xml")

        elif command == "run":
            # Run autonomous driving
            host = sys.argv[2] if len(sys.argv) > 2 else "192.168.1.100"
            port1 = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
            port2 = int(sys.argv[4]) if len(sys.argv) > 4 else 8002

            server = Server(host, port1, port2)
            server.start()

        elif command == "help":
            print("Usage: python rc_driver.py [command]")
            print("Commands:")
            print("  train                    Train neural network model")
            print("  run [host] [port1] [port2]  Run autonomous driving server")
            print("  help                     Show this help message")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python rc_driver.py help' for usage information")
    else:
        # Default: run server
        server = Server("192.168.1.100", 8000, 8002)
        server.start()


if __name__ == '__main__':
    main()