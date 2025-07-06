import random
import numpy as np
from settings import *
import os

class NeuralNetwork:
    """Jaringan Saraf Tiruan sederhana sebagai 'otak' sel."""
    def __init__(self, num_inputs, num_hidden, num_outputs):
        self.weights_ih = np.random.uniform(-1, 1, (num_hidden, num_inputs))
        self.weights_ho = np.random.uniform(-1, 1, (num_outputs, num_hidden))

    def predict(self, inputs):
        """Melakukan forward propagation untuk mendapatkan output."""
        hidden = np.dot(self.weights_ih, inputs)
        hidden = np.tanh(hidden)
        outputs = np.dot(self.weights_ho, hidden)
        outputs = np.tanh(outputs)
        return outputs

    @staticmethod
    def crossover(parent1_brain, parent2_brain):
        """Menggabungkan dua 'otak' untuk menciptakan keturunan."""
        child_brain = NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
        midpoint = random.randint(0, child_brain.weights_ih.size)
        child_brain.weights_ih.flat[:midpoint] = parent1_brain.weights_ih.flat[:midpoint]
        child_brain.weights_ih.flat[midpoint:] = parent2_brain.weights_ih.flat[midpoint:]
        
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

    @staticmethod
    def save_brains(filepath, brains):
        """Menyimpan daftar beberapa otak (bobotnya) ke satu file."""
        if not brains:
            print("Tidak ada otak untuk disimpan.")
            return
        # Membuat dictionary untuk menyimpan semua bobot dari semua otak
        all_weights = {}
        for i, brain in enumerate(brains):
            all_weights[f'w_ih_{i}'] = brain.weights_ih
            all_weights[f'w_ho_{i}'] = brain.weights_ho
        np.savez(filepath, **all_weights)
        print(f"{len(brains)} otak berhasil disimpan ke {filepath}")

    @staticmethod
    def load_brains(filepath):
        """Memuat beberapa otak dari file dan mengembalikannya sebagai list."""
        if not os.path.exists(filepath):
            print(f"File otak tidak ditemukan di {filepath}")
            return []
            
        data = np.load(filepath)
        loaded_brains = []
        i = 0
        # Terus memuat selama ada bobot dengan indeks i
        while f'w_ih_{i}' in data:
            brain = NeuralNetwork(NUM_INPUTS, NUM_HIDDEN, NUM_OUTPUTS)
            brain.weights_ih = data[f'w_ih_{i}']
            brain.weights_ho = data[f'w_ho_{i}']
            loaded_brains.append(brain)
            i += 1
        print(f"{len(loaded_brains)} otak berhasil dimuat dari {filepath}")
        return loaded_brains