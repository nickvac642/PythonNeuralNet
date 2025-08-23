# Foundational Neural Network

This folder contains the core neural network implementation that serves as the foundation for more complex models.

## Overview

This is a clean, improved version of the original neural network with:

- Forward propagation
- Backpropagation algorithm
- Sigmoid activation function
- Configurable architecture (input, hidden, output layers)
- Early stopping capability
- Progress tracking

## Key Components

### Core Functions:

- `initialize_network()` - Creates network structure with random weights
- `forward_propagate()` - Processes inputs through the network
- `backward_propagate_error()` - Calculates error gradients
- `update_weights()` - Adjusts weights based on gradients
- `train_network()` - Orchestrates the training process

### Improvements from Original:

1. Added `if __name__ == "__main__":` guard to prevent execution on import
2. Early stopping when error < 0.01
3. Verbose training option
4. Better progress reporting
5. Configurable hidden layer size

## Usage

```python
from NeuralNet import initialize_network, train_network, forward_user_input, predict

# Initialize network
n_inputs = 5
n_hidden = 3
n_outputs = 2
network = initialize_network(n_inputs, n_hidden, n_outputs)

# Train network
dataset = [...]  # Your training data
train_network(network, dataset, learning_rate=0.5, epochs=1000, n_outputs=2)

# Make predictions
inputs = [1, 0, 1, 1, 0]
outputs = forward_user_input(network, inputs)
prediction = predict(outputs)
```

## Architecture

- **Input Layer**: Variable size based on features
- **Hidden Layer**: Configurable neurons (default: 3)
- **Output Layer**: Variable size based on classes
- **Activation**: Sigmoid function
- **Learning**: Gradient descent with backpropagation

This serves as the foundation for domain-specific applications like medical diagnosis, image recognition, or any pattern recognition task.
