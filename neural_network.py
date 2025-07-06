import random
import numpy as np
from settings import *

class NeuralNetwork:
    """Jaringan Saraf Tiruan sederhana sebagai 'otak' sel."""
    def __init__(self, num_inputs, num_hidden, num_outputs):
        self.weights_ih = np.random.uniform(-1, 1, (num_hidden, num_inputs))
        self.weights_ho = np.random.uniform(-1, 1, (num_outputs, num_hidden))

    def predict(self, inputs):
        """Melakukan forward propagation untuk mendapatkan output."""
        hidden = np.dot(self.weights_ih, inputs)
        hidden = np.tanh(hidden)  # Fungsi aktivasi tanh
        outputs = np.dot(self.weights_ho, hidden)
        outputs = np.tanh(outputs)
        return outputs

    @staticmethod
    def crossover(parent1_brain, parent2_brain):
        """Menggabungkan dua 'otak' untuk menciptakan keturunan."""
        child_brain = NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        # Crossover weights input-hidden
        midpoint = random.randint(0, child_brain.weights_ih.size)
        child_brain.weights_ih.flat[:midpoint] = parent1_brain.weights_ih.flat[:midpoint]
        child_brain.weights_ih.flat[midpoint:] = parent2_brain.weights_ih.flat[midpoint:]
        # Crossover weights hidden-output
        midpoint = random.randint(0, child_brain.weights_ho.size)
        child_brain.weights_ho.flat[:midpoint] = parent1_brain.weights_ho.flat[:midpoint]
        child_brain.weights_ho.flat[midpoint:] = parent2_brain.weights_ho.flat[midpoint:]
        return child_brain

    def mutate(self, rate, strength):
        """Mengubah bobot secara acak."""
        for i in range(self.weights_ih.shape[0]):
            for j in range(self.weights_ih.shape[1]):
                if random.random() < rate:
                    self.weights_ih[i, j] += random.uniform(-strength, strength)
        for i in range(self.weights_ho.shape[0]):
            for j in range(self.weights_ho.shape[1]):
                if random.random() < rate:
                    self.weights_ho[i, j] += random.uniform(-strength, strength)