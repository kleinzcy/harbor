# AutoRCCar - Autonomous Remote-Controlled Car System

## Project Goal

Build a Python-based autonomous driving system for remote-controlled cars that allows developers to implement real-time video stream processing, neural network model training, object detection, sensor data fusion, and hardware control without manually integrating disparate components and writing extensive boilerplate code.

---

## Background & Problem

Without this library/tool, developers are forced to manually integrate OpenCV, serial communication, neural network training, and sensor data processing from scratch. This leads to repetitive code, error-prone boilerplate, maintenance issues, and difficulty achieving a cohesive end-to-end autonomous driving pipeline. Developers must separately handle video stream decoding, object detection classifiers, neural network architecture, distance calculation algorithms, and hardware control protocols, resulting in fragmented systems that are hard to debug and extend.

With this library/tool, developers can focus on high-level autonomous driving logic using a unified API that provides ready-to-use modules for video processing, neural network training, object detection, sensor fusion, and hardware control. The system enables rapid prototyping, consistent error handling, and seamless integration of all components required for autonomous RC car operation.

---

## Core Features

### Feature 1: Real-time Video Stream Processing

**As a developer**, I want to capture and process real-time video streams from a Raspberry Pi camera, so I can extract frames for neural network inference and object detection.

**Expected Behavior / Usage:**

The video stream module should connect to a camera server, receive JPEG-encoded frames, decode them into OpenCV image objects, and perform pre-processing such as grayscale conversion and region-of-interest (ROI) extraction. The API should provide a simple interface to start/stop streaming and retrieve processed frames.

**Test Cases:** `tests/test_cases/feature1_video_stream.json`

```json
{
    "description": "Test JPEG frame decoding and ROI extraction",
    "cases": [
        {
            "input": "base64_encoded_jpeg_frame",
            "expected_output": {
                "width": 320,
                "height": 240,
                "roi_shape": [120, 320],
                "format": "gray"
            }
        }
    ]
}
```

---

### Feature 2: Neural Network Model Training

**As a developer**, I want to train a neural network model using collected driving images, so I can predict steering commands from real-time video frames.

**Expected Behavior / Usage:**

The neural network module should provide a `NeuralNetwork` class with methods `create()`, `train()`, `evaluate()`, `predict()`, `save_model()`, and `load_model()`. The network architecture should be configurable (default 76800→32→4) and use Sigmoid activation with back-propagation training. The `load_data()` function should load and preprocess training data from NPZ files.

**Test Cases:** `tests/test_cases/feature2_nn_training.json`

```json
{
    "description": "Test neural network creation, training, and prediction",
    "cases": [
        {
            "input": {"layer_sizes": [76800, 32, 4]},
            "expected_output": "model_created"
        },
        {
            "input": {"X_train_shape": [100, 76800], "y_train_shape": [100, 4]},
            "expected_output": "training_completed"
        },
        {
            "input": {"X_test_sample": [0.1, 0.2, ...]},
            "expected_output": {"prediction": 2}
        }
    ]
}
```

---

### Feature 3: Object Detection System

**As a developer**, I want to detect stop signs and traffic lights in video frames using Haar cascade classifiers, so I can trigger appropriate driving behaviors.

**Expected Behavior / Usage:**

*3.1 Stop Sign Detection — Detect stop signs using a pre-trained cascade classifier*

The `ObjectDetection` class should provide a `detect()` method that takes a cascade classifier and grayscale image, returns the Y-coordinate of the detected object's bottom, and draws bounding boxes on the color image.

**Test Cases:** `tests/test_cases/feature3_1_stop_sign.json`

```json
{
    "description": "Test stop sign detection in grayscale image",
    "cases": [
        {
            "input": {"cascade_file": "stop_sign.xml", "image": "grayscale_array"},
            "expected_output": {"detected": true, "v_param": 150}
        },
        {
            "input": {"cascade_file": "stop_sign.xml", "image": "empty_gray_array"},
            "expected_output": {"detected": false, "v_param": 0}
        }
    ]
}
```

*3.2 Traffic Light Detection & Recognition — Detect traffic lights and recognize their color state*

The detection should also analyze the region of interest to determine if the light is red, green, or yellow based on brightness distribution.

**Test Cases:** `tests/test_cases/feature3_2_traffic_light.json`

```json
{
    "description": "Test traffic light detection and color recognition",
    "cases": [
        {
            "input": {"cascade_file": "traffic_light.xml", "image": "color_array"},
            "expected_output": {"detected": true, "color": "red"}
        },
        {
            "input": {"cascade_file": "traffic_light.xml", "image": "color_array_green"},
            "expected_output": {"detected": true, "color": "green"}
        }
    ]
}
```

---

### Feature 4: Distance Measurement

**As a developer**, I want to calculate the distance from detected objects to the camera using camera intrinsic parameters, so I can maintain safe following distances.

**Expected Behavior / Usage:**

The `DistanceToCamera` class should provide a `calculate()` method that takes vertical pixel coordinate, object real-world height, X-offset for text display, and image array; it returns distance in centimeters and optionally annotates the image.

**Test Cases:** `tests/test_cases/feature4_distance_calculation.json`

```json
{
    "description": "Test distance calculation from object pixel position",
    "cases": [
        {
            "input": {"v": 150, "h": 5.5, "x_shift": 300, "image": "dummy_array"},
            "expected_output": {"distance": 45.2}
        },
        {
            "input": {"v": 200, "h": 5.5, "x_shift": 300, "image": "dummy_array"},
            "expected_output": {"distance": 32.1}
        }
    ]
}
```

---

### Feature 5: Sensor Data Fusion

**As a developer**, I want to integrate ultrasonic sensor data with visual detection, so I can implement collision avoidance and emergency stopping.

**Expected Behavior / Usage:**

The sensor fusion module should receive distance readings from an ultrasonic sensor via a network socket, compare them with safety thresholds, and trigger stop commands when obstacles are too close.

**Test Cases:** `tests/test_cases/feature5_sensor_fusion.json`

```json
{
    "description": "Test ultrasonic sensor data integration and threshold checking",
    "cases": [
        {
            "input": {"sensor_distance": 15, "threshold": 30},
            "expected_output": {"action": "stop"}
        },
        {
            "input": {"sensor_distance": 50, "threshold": 30},
            "expected_output": {"action": "proceed"}
        }
    ]
}
```

---

### Feature 6: Hardware Control Interface

**As a developer**, I want to send control commands to an Arduino via serial port, so I can steer the RC car forward, backward, left, right, or stop.

**Expected Behavior / Usage:**

The `RCControl` class should provide `steer(prediction)` and `stop()` methods that translate prediction labels (0: left, 1: right, 2: forward, other: stop) into serial commands.

**Test Cases:** `tests/test_cases/feature6_hardware_control.json`

```json
{
    "description": "Test serial command mapping for steering predictions",
    "cases": [
        {
            "input": {"prediction": 2},
            "expected_output": {"command": "forward"}
        },
        {
            "input": {"prediction": 0},
            "expected_output": {"command": "left"}
        },
        {
            "input": {"prediction": 1},
            "expected_output": {"command": "right"}
        },
        {
            "input": {"prediction": 3},
            "expected_output": {"command": "stop"}
        }
    ]
}
```

---

### Feature 7: Data Collection Module

**As a developer**, I want to collect training data by manually driving the car while saving images and corresponding control labels, so I can build a dataset for neural network training.

**Expected Behavior / Usage:**

The `CollectTrainingData` class should connect to video stream and serial port, capture frames when arrow keys are pressed, and save image‑label pairs as NPZ files.

**Test Cases:** `tests/test_cases/feature7_data_collection.json`

```json
{
    "description": "Test training data collection and labeling",
    "cases": [
        {
            "input": {"key": "K_UP", "frame": "image_array"},
            "expected_output": {"label": [0, 0, 1, 0], "saved": true}
        },
        {
            "input": {"key": "K_LEFT", "frame": "image_array"},
            "expected_output": {"label": [1, 0, 0, 0], "saved": true}
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.