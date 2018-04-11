"""
name: Nick Vaccarello
language: Python
Description: Walking through a neural net tutorial on how to implement a backpropogation algorithm for
             training deep learning neural networks
"""

from random import seed
from random import random
from math import exp
import time
"""
This function defines a simple neural network.
The hidden_layer: Creates n_hidden neurons and each neuron has n_inputs+1 weights, one for each input column
                  in a dataset and an additional one for the bias.

The output_layer: Has n_hidden+1 weights meaning that each neuron in the output_layer connects to each neuron
                  in the hidden_layer.
"""

def initialize_network(n_inputs, n_hidden, n_outputs):
    network = list()
    hidden_layer = [{'weights':[random() for i in range(n_inputs + 1)]} for i in range(n_hidden)]
    network.append(hidden_layer)
    output_layer = [{'weights':[random() for i in range(n_hidden + 1)]} for i in range(n_outputs)]
    network.append(output_layer)
    return network

"""
This function will calculate the activation of one neuron. Neuron activation is calculated as the weighted sums
of the inputs. activation = sum(weight_i * input_i) + bias. The bias is a special weight that has no input to
multiply with, its purpose is to shift a line up and down to fit the prediction with the data better.
"""
def activate(weights, inputs):
    activation = weights[-1]
    for i in range(len(weights)-1):
        activation += weights[i] * inputs[i]
    return activation

"""
The transfer function utilizes the sigmoid activation function to output numbers between 0 and 1 using
the calculated activation of a neuron.
"""
def transfer(activation):
    return 1.0/(1.0 + exp(-activation))

"""
This function forward propagates by calculating the output for each neuron. All of the outputs from one
layer, become inputs into the next layer.
"""
def forward_propagate(network, row):
    inputs = row
    for layer in network:
        new_inputs = []
        for neuron in layer:
            activation = activate(neuron['weights'], inputs)
            neuron['output'] = transfer(activation)
            new_inputs.append(neuron['output'])
        inputs = new_inputs
    return inputs

def forward_user_input(network, inputs):
    for layer in network:
        new_inputs = []
        for neuron in layer:
            activation = activate(neuron['weights'], inputs)
            neuron['output'] = transfer(activation)
            new_inputs.append(neuron['output'])
        inputs = new_inputs
    output = network[-1][-1]['output']
    return output



"""
This function is used to calculate the derivative of the output value of a neuron
"""
def transfer_derivative(output):
    return output *(1.0-output)

"""
This function calculates the error for each output neuron, yielding the error signal (input) to 
propagate backwards through the network.
"""
def backward_propagate_error(network, expected):
	for i in reversed(range(len(network))):
		layer = network[i]
		errors = list()
		if i != len(network)-1:
			for j in range(len(layer)):
				error = 0.0
				for neuron in network[i + 1]:
					error += (neuron['weights'][j] * neuron['delta'])
				errors.append(error)
		else:
			for j in range(len(layer)):
				neuron = layer[j]
				errors.append(expected[j] - neuron['output'])
		for j in range(len(layer)):
			neuron = layer[j]
			neuron['delta'] = errors[j] * transfer_derivative(neuron['output'])

"""
This function will update the weights based upon the learning rate, input, and back propagated error
"""
def update_weights(network, row, l_rate):
    for i in range(len(network)):
        inputs = row[:-1]
        if i != 0:
            inputs = [neuron['output'] for neuron in network[i-1]]
        for neuron in network[i]:
            for j in range(len(inputs)):
                neuron['weights'][j]+= l_rate*neuron['delta']*inputs[j]
            neuron['weights'][-1] += l_rate * neuron['delta']

"""
This functions main task will be for calling and initializing all the aspects for training the network.
"""
def train_network(network, train, l_rate, n_epoch, n_outputs):
    for epoch in range(n_epoch):
        sum_error=0
        for row in train:
            outputs = forward_propagate(network, row)
            expected = [0 for i in range(n_outputs)]
            expected[row[-1]]=1
            sum_error += sum([(expected[i]-outputs[i])**2 for i in range(len(expected))])
            backward_propagate_error(network, expected)
            update_weights(network,row,l_rate)
        print('>epoch=%d, lrate=%.3f, error=%.3f' % (epoch, l_rate, sum_error))

seed(1)
dataset = [[0,1,1,0,0,1],
           [1,1,1,0,1,1],
           [1,1,0,0,1,0],
           [0,1,0,1,1,0],
           [1,1,1,0,1,1],
           [0,0,0,1,0,0],
           [1,1,1,0,0,1],
           [1,0,1,0,1,0]]


n_inputs = len(dataset[0]) - 1 #The last value in a single data set is the expected value so it is disregarded
n_outputs = len(set([row[-1] for row in dataset])) #The length of a set of unique expected values
network = initialize_network(n_inputs, 2, n_outputs) #Initialize an untrained network
start = time.time()
train_network(network, dataset, 0.5, 20000, n_outputs)
end = time.time()
print("Time to train:", round(end-start,2),"secs")
user_input = "y"
while user_input != "n":
    inputs = []
    for i in range(len(dataset[1])-1):
        num = input("Number "+str(i+1)+": ")
        num = float (num)
        inputs.append(num)
    output = forward_user_input(network, inputs)
    print("Data set maps to: " + str(round(output, 0)))
    user_input = input("Would you like to test another set of data (y/n): ")
for layer in network:
    for i in layer:
        print(i)

