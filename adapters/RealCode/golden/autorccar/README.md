# AutoRCCar - Autonomous Remote-Controlled Car System

## Overview

AutoRCCar is an autonomous driving system for remote-controlled cars that uses computer vision, neural networks, and sensor fusion to navigate and avoid obstacles.

## Project Structure

```
autorccar/
├── computer/                    # Core implementation
│   ├── feature1_video_stream.py      # Video frame processing
│   ├── feature2_nn_training.py       # Neural network training
│   ├── feature3_object_detection.py  # Stop sign/traffic light detection
│   ├── feature4_distance_calculation.py # Distance calculation
│   ├── feature5_sensor_fusion.py     # Sensor data integration
│   ├── feature6_hardware_control.py  # RC car control commands
│   ├── feature7_data_collection.py   # Training data collection
│   ├── model.py                 # Neural network implementation
│   ├── rc_driver_helper.py      # Helper classes for RC control
│   ├── rc_driver.py             # Main autonomous driving program
│   └── cascade_xml/             # Haar cascade classifiers
│       ├── stop_sign.xml
│       └── traffic_light.xml
├── tests/                       # Test suite
│   ├── test_cases/              # JSON test cases for all features
│   ├── stdout/                  # Test output directory
│   └── test.sh                  # Test runner script
├── start.md                     # Product Requirements Document (PRD)
├── environment.yml              # Conda environment configuration
└── README.md                    # This file
```

## Features

1. **Real-time Video Stream Processing** - Processes JPEG frames, extracts ROI
2. **Neural Network Model Training** - Creates and trains NN for steering prediction
3. **Object Detection** - Detects stop signs and traffic lights using Haar cascades
4. **Distance Calculation** - Calculates distance to objects using camera geometry
5. **Sensor Fusion** - Integrates ultrasonic sensor data with visual input
6. **Hardware Control** - Maps predictions to serial commands for RC car
7. **Data Collection** - Collects and labels training data from keyboard input

## Quick Start

### Running Tests

1. Make the test script executable:
   ```bash
   chmod +x tests/test.sh
   ```

2. Run all tests:
   ```bash
   bash tests/test.sh
   ```

3. Test outputs will be saved to `tests/stdout/`

### Testing Individual Features

Each feature script reads JSON input from stdin and outputs JSON results:

```bash
# Test feature 1 (video stream processing)
echo "base64_encoded_jpeg_frame" | python3 computer/feature1_video_stream.py

# Test feature 2 (neural network)
echo '{"layer_sizes": [76800, 32, 4]}' | python3 computer/feature2_nn_training.py

# Test feature 3 (object detection)
echo '{"cascade_file": "stop_sign.xml", "image": "grayscale_array"}' | python3 computer/feature3_object_detection.py

# Test feature 4 (distance calculation)
echo '{"v": 150, "h": 5.5, "x_shift": 300, "image": "dummy_array"}' | python3 computer/feature4_distance_calculation.py

# Test feature 5 (sensor fusion)
echo '{"sensor_distance": 15, "threshold": 30}' | python3 computer/feature5_sensor_fusion.py

# Test feature 6 (hardware control)
echo '{"prediction": 2}' | python3 computer/feature6_hardware_control.py

# Test feature 7 (data collection)
echo '{"key": "K_UP", "frame": "image_array"}' | python3 computer/feature7_data_collection.py
```

## Main Autonomous Driving System

The main program `rc_driver.py` provides two modes:

### Training Mode
Trains the neural network on collected data:
```bash
python3 computer/rc_driver.py train
```

### Autonomous Driving Mode
Runs the autonomous driving server:
```bash
python3 computer/rc_driver.py run [host] [video_port] [sensor_port]
```

Default: `python3 computer/rc_driver.py run 192.168.1.100 8000 8002`

## Dependencies

The project requires:
- Python 3.11+
- OpenCV (cv2)
- NumPy
- PySerial

A conda environment configuration is provided in `environment.yml`:

```bash
conda env create -f environment.yml
conda activate autorccar
```

## Implementation Notes

- The current implementation uses simplified versions of feature scripts for testing without external dependencies
- For full functionality, install the dependencies listed in `environment.yml`
- Haar cascade XML files are placeholders; real classifiers would be needed for actual object detection
- Serial communication is simulated when hardware is not available

## Test Cases

Test cases are defined in `tests/test_cases/` as JSON files:
- `feature1_video_stream.json`
- `feature2_nn_training.json`
- `feature3_1_stop_sign.json`
- `feature3_2_traffic_light.json`
- `feature4_distance_calculation.json`
- `feature5_sensor_fusion.json`
- `feature6_hardware_control.json`
- `feature7_data_collection.json`

## License

This project is for educational and demonstration purposes.