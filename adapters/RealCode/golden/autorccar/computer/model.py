import cv2
import numpy as np
import glob
import os

def load_data(input_size, path):
    """
    Load training data from a specified path, perform data pre-processing,
    and split the data into training and validation sets.

    Parameters:
    - input_size (int): The size of the input image (number of pixels)
    - path (str): The path to the training data file, supporting glob pattern matching

    Returns:
    - tuple: (X_train, X_test, y_train, y_test)
    """
    # Find all NPZ files
    files = glob.glob(path)
    if not files:
        raise FileNotFoundError(f"No files found matching pattern: {path}")

    # Load and concatenate data from all files
    X_data = []
    y_data = []

    for file in files:
        data = np.load(file)
        X_data.append(data['X'])
        y_data.append(data['y'])

    # Concatenate all data
    X = np.concatenate(X_data, axis=0)
    y = np.concatenate(y_data, axis=0)

    # Ensure correct shape
    if X.shape[1] != input_size:
        # Reshape if needed
        X = X.reshape(-1, input_size)

    # Split into training and testing sets (80/20)
    n_samples = X.shape[0]
    n_train = int(0.8 * n_samples)

    indices = np.random.permutation(n_samples)
    train_idx, test_idx = indices[:n_train], indices[n_train:]

    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    return X_train, X_test, y_train, y_test


class NeuralNetwork:
    """A neural network model based on OpenCV for autonomous driving decision prediction."""

    def __init__(self):
        self.model = None
        self.layer_sizes = None

    def create(self, layer_sizes):
        """
        Create a neural network with the specified architecture.

        Parameters:
        - layer_sizes (np.ndarray): The number of nodes in each layer, e.g., [76800, 32, 4]
        """
        self.layer_sizes = layer_sizes

        # Create MLP model
        self.model = cv2.ml.ANN_MLP_create()

        # Set layer sizes
        self.model.setLayerSizes(layer_sizes)

        # Set activation function to sigmoid
        self.model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM)

        # Set training method
        self.model.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)

        # Set termination criteria
        self.model.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 1000, 0.01))

    def train(self, X, y):
        """
        Train the neural network model.

        Parameters:
        - X (np.ndarray): Training feature data, shape (n_samples, n_features)
        - y (np.ndarray): Training label data, shape (n_samples, n_classes)
        """
        if self.model is None:
            raise ValueError("Model not created. Call create() first.")

        # Ensure data types are correct
        X = X.astype(np.float32)
        y = y.astype(np.float32)

        # Train the model
        self.model.train(X, cv2.ml.ROW_SAMPLE, y)

    def evaluate(self, X, y):
        """
        Evaluate the model on test data.

        Parameters:
        - X (np.ndarray): Test feature data
        - y (np.ndarray): Test label data

        Returns:
        - float: Model accuracy between 0 and 1
        """
        if self.model is None:
            raise ValueError("Model not created. Call create() first.")

        X = X.astype(np.float32)
        y = y.astype(np.float32)

        # Get predictions
        _, predictions = self.model.predict(X)

        # Convert predictions to class labels (argmax)
        pred_labels = np.argmax(predictions, axis=1)
        true_labels = np.argmax(y, axis=1)

        # Calculate accuracy
        accuracy = np.mean(pred_labels == true_labels)
        return accuracy

    def predict(self, X):
        """
        Make predictions using the trained model.

        Parameters:
        - X (np.ndarray): Feature data to be predicted

        Returns:
        - np.ndarray: Array of prediction results (0: left turn, 1: right turn, 2: forward, 3: stop)
        """
        if self.model is None:
            raise ValueError("Model not created. Call create() first.")

        X = X.astype(np.float32)

        # Get predictions
        _, predictions = self.model.predict(X)

        # Convert to class labels (argmax)
        pred_labels = np.argmax(predictions, axis=1)
        return pred_labels

    def save_model(self, path):
        """
        Save the trained model to a file.

        Parameters:
        - path (str): The path to save the model
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Save model
        self.model.save(path)

    def load_model(self, path):
        """
        Load a trained model from a file.

        Parameters:
        - path (str): The path to the model file
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        # Load model
        self.model = cv2.ml.ANN_MLP_load(path)

        # Extract layer sizes from loaded model
        # Note: OpenCV doesn't provide a direct method to get layer sizes
        # We'll set a default or try to infer
        self.layer_sizes = np.int32([76800, 32, 4])


if __name__ == "__main__":
    # Test the module
    print("NeuralNetwork module loaded successfully")
    print(f"load_data function: {load_data.__doc__}")
    nn = NeuralNetwork()
    print(f"NeuralNetwork class: {nn.__doc__}")