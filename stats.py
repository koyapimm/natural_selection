import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from settings import *

class StatsCollector:
    def __init__(self):
        self.days = []
        self.trait_history = defaultdict(list)  # {trait: [[values_day1], [values_day2], ...]}
        self.generation_history = []
        self.population_history = []
        self.genealogy = defaultdict(list)  # {generation: [count_day1, count_day2, ...]}
        self.offspring_counts = defaultdict(list)  # {trait_bin: [offspring_counts]}
        self.survival_bins = defaultdict(lambda: defaultdict(list))  # {trait: {bin: [survival_rate]}}
        self.output_dir = STATS_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self.last_blobs = None  # For survival rate tracking

    def collect(self, day, blobs):
        self.days.append(day)
        # Traits
        for trait in ['speed', 'size', 'sense']:
            self.trait_history[trait].append([getattr(b, trait) for b in blobs])
        # Generations
        gens = [b.generation for b in blobs]
        self.generation_history.append(gens)
        self.population_history.append(len(blobs))
        # Genealogy
        for g in set(gens):
            self.genealogy[g].append(gens.count(g))
        # Survival rate per trait bin (compare with previous day)
        if self.last_blobs is not None:
            for trait in ['speed', 'size', 'sense']:
                prev_vals = np.array([getattr(b, trait) for b in self.last_blobs])
                prev_ids = [b.id for b in self.last_blobs]
                curr_ids = set(b.id for b in blobs)
                bins = np.linspace(prev_vals.min(), prev_vals.max(), 8)
                bin_indices = np.digitize(prev_vals, bins)
                for i, pid in enumerate(prev_ids):
                    survived = pid in curr_ids
                    self.survival_bins[trait][bin_indices[i]].append(int(survived))
        self.last_blobs = blobs.copy()

    def trait_stats(self, trait, day_idx):
        vals = np.array(self.trait_history[trait][day_idx])
        return {
            'mean': np.mean(vals),
            'median': np.median(vals),
            'var': np.var(vals),
            'std': np.std(vals),
            'cv': np.std(vals) / np.mean(vals) if np.mean(vals) > 0 else 0
        }

    def plot_trait_distributions(self, day_idx):
        for trait in ['speed', 'size', 'sense']:
            vals = np.array(self.trait_history[trait][day_idx])
            plt.figure(figsize=(6,4))
            sns.histplot(vals, kde=True, bins=20)
            plt.title(f"{trait.capitalize()} Distribution (Day {self.days[day_idx]})")
            plt.xlabel(trait)
            plt.ylabel("Count")
            if STATS_SAVE_PNG:
                plt.savefig(os.path.join(self.output_dir, f"{trait}_hist_day{self.days[day_idx]}.png"))
            plt.close()

    def plot_trait_stats_over_time(self):
        for trait in ['speed', 'size', 'sense']:
            means = [self.trait_stats(trait, i)['mean'] for i in range(len(self.days))]
            stds = [self.trait_stats(trait, i)['std'] for i in range(len(self.days))]
            plt.figure(figsize=(8,4))
            plt.plot(self.days, means, label='Mean')
            plt.fill_between(self.days, np.array(means)-np.array(stds), np.array(means)+np.array(stds), alpha=0.3, label='±1 std')
            plt.title(f"{trait.capitalize()} Mean/Std Over Time")
            plt.xlabel("Day")
            plt.ylabel(trait)
            plt.legend()
            if STATS_SAVE_PNG:
                plt.savefig(os.path.join(self.output_dir, f"{trait}_meanstd.png"))
            plt.close()

    def plot_generation_stats(self):
        # Mean/std per generation
        gen_stats = defaultdict(lambda: {'mean': [], 'std': []})
        for day_idx, gens in enumerate(self.generation_history):
            for g in set(gens):
                vals = [self.trait_history['size'][day_idx][i] for i, blob_gen in enumerate(gens) if blob_gen == g]
                if vals:
                    gen_stats[g]['mean'].append(np.mean(vals))
                    gen_stats[g]['std'].append(np.std(vals))
        # Plotting code here (example for size):
        plt.figure(figsize=(8,5))
        for g in sorted(gen_stats.keys()):
            plt.plot(self.days[:len(gen_stats[g]['mean'])], gen_stats[g]['mean'], label=f'Gen {g}')
        plt.title("Mean Size per Generation Over Time")
        plt.xlabel("Day")
        plt.ylabel("Size")
        plt.legend()
        if STATS_SAVE_PNG:
            plt.savefig(os.path.join(self.output_dir, "generation_size_means.png"))
        plt.close()

    def plot_generation_depth(self):
        # How many generations are active at each day
        depths = [len(set(gens)) for gens in self.generation_history]
        plt.figure(figsize=(8,4))
        plt.plot(self.days, depths)
        plt.title("Active Generations Over Time")
        plt.xlabel("Day")
        plt.ylabel("# Generations")
        if STATS_SAVE_PNG:
            plt.savefig(os.path.join(self.output_dir, "generation_depth.png"))
        plt.close()

    def diversity_metrics(self, day_idx):
        # CV per trait
        cv = {trait: self.trait_stats(trait, day_idx)['cv'] for trait in ['speed', 'size', 'sense']}
        # Shannon entropy for generations
        gens = np.array(self.generation_history[day_idx])
        _, counts = np.unique(gens, return_counts=True)
        probs = counts / counts.sum()
        shannon = -np.sum(probs * np.log2(probs + 1e-9))
        return {'cv': cv, 'shannon': shannon}

    def plot_survival_rate_heatmap(self, trait):
        # Prepare heatmap data: rows=days, cols=bins
        bin_count = 7
        heatmap = np.zeros((len(self.days), bin_count))
        for day_idx in range(len(self.days)):
            # For each bin, average survival rate up to this day
            for b in range(1, bin_count+1):
                rates = self.survival_bins[trait][b]
                if rates:
                    heatmap[day_idx, b-1] = np.mean(rates)
                else:
                    heatmap[day_idx, b-1] = np.nan
        plt.figure(figsize=(10,6))
        sns.heatmap(heatmap.T, cmap="viridis", cbar_kws={'label': 'Survival Rate'},
                    xticklabels=10, yticklabels=[f"Bin {i+1}" for i in range(bin_count)])
        plt.title(f"Survival Rate per {trait.capitalize()} Bin Over Time")
        plt.xlabel("Day")
        plt.ylabel(f"{trait.capitalize()} Bin")
        if STATS_SAVE_PNG:
            plt.savefig(os.path.join(self.output_dir, f"{trait}_survival_heatmap.png"))
        plt.close()

    def check_extinction_convergence(self, day_idx):
        diversity = self.diversity_metrics(day_idx)
        if any(cv < 0.08 for cv in diversity['cv'].values()):
            print(f"[WARNING] Diversity critically low at day {self.days[day_idx]}: {diversity['cv']}")
        # Add more convergence/extinction checks as needed

    def save_csv(self):
        # Save trait stats, diversity, etc. as CSV
        df = pd.DataFrame({
            'day': self.days,
            'pop': self.population_history,
            'speed_mean': [self.trait_stats('speed', i)['mean'] for i in range(len(self.days))],
            'size_mean': [self.trait_stats('size', i)['mean'] for i in range(len(self.days))],
            'sense_mean': [self.trait_stats('sense', i)['mean'] for i in range(len(self.days))],
            'speed_cv': [self.trait_stats('speed', i)['cv'] for i in range(len(self.days))],
            'size_cv': [self.trait_stats('size', i)['cv'] for i in range(len(self.days))],
            'sense_cv': [self.trait_stats('sense', i)['cv'] for i in range(len(self.days))],
        })
        df.to_csv(os.path.join(self.output_dir, "summary_stats.csv"), index=False) 