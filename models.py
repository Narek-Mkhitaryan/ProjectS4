import numpy as np
import logging

# Logging setup
logging.basicConfig(filename='sales_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NeuralNetwork:
    def __init__(self, layer_sizes):
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []
        self.initialize_parameters()
    
    def initialize_parameters(self):
        for i in range(len(self.layer_sizes) - 1):
            w = np.random.randn(self.layer_sizes[i], self.layer_sizes[i+1]) * 0.01
            b = np.zeros((1, self.layer_sizes[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        return np.where(x > 0, 1, 0)
    
    def forward(self, X):
        self.activations = [X]
        self.z_values = []
        
        for i in range(len(self.weights)):
            z = np.dot(self.activations[-1], self.weights[i]) + self.biases[i]
            self.z_values.append(z)
            if i < len(self.weights) - 1:
                a = self.relu(z)
            else:
                a = z
            self.activations.append(a)
        
        return self.activations[-1]
    
    def backward(self, X, y, learning_rate):
        m = X.shape[0]
        delta = self.activations[-1] - y
        
        for i in range(len(self.weights) - 1, -1, -1):
            dw = np.dot(self.activations[i].T, delta) / m
            db = np.sum(delta, axis=0, keepdims=True) / m
            
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * self.relu_derivative(self.z_values[i-1])
            
            self.weights[i] -= learning_rate * dw
            self.biases[i] -= learning_rate * db
    
    def train(self, X, y, epochs, learning_rate):
        for epoch in range(epochs):
            y_pred = self.forward(X)
            self.backward(X, y, learning_rate)
            if epoch % 100 == 0:
                loss = np.mean((y_pred - y) ** 2)
                logging.debug(f"Epoch {epoch}, Loss: {loss}")