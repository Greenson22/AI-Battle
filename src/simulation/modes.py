# src/simulation/modes.py

import pygame
import random
from settings import *
from cell import Cell, NeuralNetwork
from crystal import Crystal
from src.simulation.base_simulation import BaseSimulation

class TrainingMode(BaseSimulation):
    def __init__(self, start_from_scratch=True):
        super().__init__(title="Mode Latihan")
        self.generation_count = 1
        self.generation_timer = 0
        self.generation_frame_limit = GENERATION_TIME_SECS * FRAME_RATE
        self.save_indicator_timer = 0
        
        if start_from_scratch:
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            trained_brains = NeuralNetwork.load_brains(BRAIN_FILE)
            if not trained_brains:
                self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
            else:
                self.cells = self._create_new_population(trained_brains)
    
    def _handle_key_press(self, event):
        super()._handle_key_press(event)
        if event.key == pygame.K_s:
            self._save_fittest_brains()

    def _update_simulation(self):
        super()._update_simulation()
        self.generation_timer += 1
        if self.save_indicator_timer > 0:
            self.save_indicator_timer -= 1
        if self.generation_timer >= self.generation_frame_limit or not self.cells:
            self._evolve_next_generation()

    def _save_fittest_brains(self):
        if not self.cells: return
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        fittest_brains = [cell.brain for cell in self.cells[:10]]
        NeuralNetwork.save_brains(BRAIN_FILE, fittest_brains)
        self.save_indicator_timer = 120

    def _draw_info_text(self):
        super()._draw_info_text()
        # ... (Kode untuk info generasi, waktu, dll)

    def _evolve_next_generation(self):
        self.generation_count += 1
        self.generation_timer = 0
        self.crystals = [Crystal() for _ in range(JUMLAH_KRISTAL)]
        self.cells.sort(key=lambda c: c.fitness, reverse=True)
        num_to_select = int(len(self.cells) * SELECTION_PERCENT)
        fittest_cells = self.cells[:num_to_select]
        if not fittest_cells:
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            brains = [c.brain for c in fittest_cells]
            self.cells = self._create_new_population(brains)

    def _create_new_population(self, parent_brains):
        new_cells = []
        while len(new_cells) < JUMLAH_SEL_AWAL:
            p1, p2 = random.choices(parent_brains, k=2)
            child_brain = NeuralNetwork.crossover(p1, p2)
            child_brain.mutate(MUTATION_RATE, MUTATION_STRENGTH)
            new_cells.append(Cell(brain=child_brain))
        return new_cells

class SandboxMode(BaseSimulation):
    def __init__(self):
        super().__init__(title="Mode Sandbox")
        trained_brains = NeuralNetwork.load_brains(BRAIN_FILE)
        if not trained_brains:
            self.cells = [Cell() for _ in range(JUMLAH_SEL_AWAL)]
        else:
            self.cells = [Cell(brain=random.choice(trained_brains)) for _ in range(JUMLAH_SEL_AWAL)]