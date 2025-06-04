"""
simulation.py
Evrimsel Yapay Yaşam Simülasyonu'nun ana yöneticisi.
Tüm canlılar (Blob) ve yiyecekler (Food) burada yönetilir.
"""

import settings
from blob import Blob, METABOLISM_TYPES, generate_random_dna
from food import Food
import math
import random
import os
import csv

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

def create_balanced_foods(count, birth_frame):
    """
    count kadar yiyeceği, settings.FOOD_TYPES arasında eşit paylaştırarak oluşturur.
    Kalanlar random atanır. Esnek ve modülerdir.
    """
    types = settings.FOOD_TYPES
    per_type = count // len(types)
    remainder = count % len(types)
    foods = []
    for i, food_type in enumerate(types):
        n = per_type + (1 if i < remainder else 0)
        for _ in range(n):
            foods.append(Food(birth_frame=birth_frame, food_type=food_type))
    random.shuffle(foods)
    return foods

class Simulation:
    def __init__(self):
        """
        Simülasyonun başlangıç durumunu oluşturur.
        5 biyom/zone ve tür başına popülasyon ile başlatılır.
        """
        self.blobs = []
        self.foods = []
        self.frame_count = 0
        self.day = 1
        # Zone koordinatları ve tür eşleşmesi
        self.zones = [
            (settings.ZONE_A, 'herbivore'),
            (settings.ZONE_B, 'omnivore'),
            (settings.ZONE_C, 'predator'),
            (settings.ZONE_D, 'hybrid'),
            (settings.ZONE_E, None),  # Center hot zone, karışık
        ]
        self.species_caps = {k: v['max_population'] for k, v in settings.SPECIES.items()}
        self._spawn_initial_species()
        self._spawn_initial_foods()

    def _spawn_initial_species(self):
        # Her zone için tür başına başlangıç popülasyonu oluştur
        for zone, species in self.zones:
            if species is None:
                continue
            cap = settings.SPECIES[species]['max_population']
            for _ in range(cap):
                x = random.uniform(zone[0], zone[0]+zone[2])
                y = random.uniform(zone[1], zone[1]+zone[3])
                dna = self._generate_species_dna(species)
                self.blobs.append(Blob(x=x, y=y, dna=dna, initial=True, species=species))

    def _generate_species_dna(self, species):
        # Türün genetik bias'larına göre DNA üret
        params = settings.SPECIES[species]
        food_types = list(params['food_weights'].keys())
        food_weights = list(params['food_weights'].values())
        preferred_food = random.choices(food_types, weights=food_weights)[0]
        aggression = random.uniform(*params['aggression_range'])
        metabolism = params['metabolism_bias']
        # Diğer genler random, bias'lı üretilebilir
        dna = generate_random_dna(preferred_food=preferred_food, aggression=aggression)
        dna['metabolism'] = metabolism
        return dna

    def _spawn_initial_foods(self):
        # Her zone'a uygun şekilde food spawnla
        for zone, _ in self.zones:
            for _ in range(30):
                x = random.uniform(zone[0], zone[0]+zone[2])
                y = random.uniform(zone[1], zone[1]+zone[3])
                # Center zone'da daha fazla ve random food
                if zone == settings.ZONE_E:
                    for _ in range(int(30 * (settings.ZONE_E_FOOD_MULTIPLIER-1))):
                        x2 = random.uniform(zone[0], zone[0]+zone[2])
                        y2 = random.uniform(zone[1], zone[1]+zone[3])
                        self.foods.append(Food(birth_frame=0, food_type=random.choice(settings.FOOD_TYPES)))
                self.foods.append(Food(birth_frame=0, food_type=random.choice(settings.FOOD_TYPES)))

    def _species_population(self):
        # Tür başına canlı sayısı
        pop = {k: 0 for k in settings.SPECIES.keys()}
        for b in self.blobs:
            if hasattr(b, 'species') and b.species in pop:
                pop[b.species] += 1
        return pop

    def _zone_food_count(self, zone):
        # Belirli bir zone'daki mevcut yiyecek sayısını döndürür
        x0, y0, w, h = zone
        return sum(1 for f in self.foods if not f.is_eaten and not f.is_rotten and x0 <= f.x < x0+w and y0 <= f.y < y0+h)

    def mutate_dna(self, dna, force_aggression_boost=False):
        """
        DNA üzerinde mutasyon uygular. MUTATION_RATE kadar gen, MUTATION_STRENGTH oranında değişir.
        force_aggression_boost: Eğer True ise aggression geninin artma olasılığı yükseltilir.
        """
        new_dna = dna.copy()
        # Sadece efficiency için ±0.05 değişim, [1.0, 1.1] aralığında clamp
        if random.random() < settings.MUTATION_RATE:
            eff = dna["efficiency"]
            eff += random.uniform(-0.05, 0.05)
            new_dna["efficiency"] = clamp(eff, 1.0, 1.1)
        # Diğer genler için settings.py sınırlarıyla clamp
        for gene, (minv, maxv) in zip(
            ["speed", "size", "vision"],
            [(settings.SPEED_MIN, settings.SPEED_MAX), (settings.SIZE_MIN, settings.SIZE_MAX), (settings.VISION_MIN, settings.VISION_MAX)]
        ):
            if random.random() < settings.MUTATION_RATE:
                val = dna[gene]
                val *= 1 + random.uniform(-settings.MUTATION_STRENGTH, settings.MUTATION_STRENGTH)
                new_dna[gene] = clamp(val, minv, maxv)
        # --- Genetik tradeoff'lar ---
        # Eğer size artarsa, speed azalt
        if new_dna["size"] > dna["size"] and random.random() < 0.7:
            new_dna["speed"] = clamp(new_dna["speed"] - settings.SIZE_SPEED_TRADEOFF, settings.SPEED_MIN, settings.SPEED_MAX)
        # Eğer efficiency artarsa, aggression azalt
        if new_dna["efficiency"] > dna["efficiency"] and random.random() < 0.7:
            new_dna["aggression"] = clamp(new_dna["aggression"] - settings.EFF_AGGR_TRADEOFF, 0.0, 1.0)
        # Eğer vision artarsa, speed azalt
        if new_dna["vision"] > dna["vision"] and random.random() < 0.5:
            new_dna["speed"] = clamp(new_dna["speed"] - settings.VISION_SPEED_TRADEOFF, settings.SPEED_MIN, settings.SPEED_MAX)
        # Metabolism mutasyonu
        if random.random() < settings.MUTATION_RATE * 0.5:
            new_dna["metabolism"] = random.choice(METABOLISM_TYPES)
        # preferred_food mutasyonu
        if random.random() < settings.MUTATION_RATE:
            new_dna["preferred_food"] = random.choice(settings.FOOD_TYPES)
        # aggression mutasyonu (0.0-1.0 arası clamp)
        aggr_rate = settings.AGGRESSION_MUTATION_RATE
        if force_aggression_boost:
            aggr_rate = max(0.2, aggr_rate * 10)
        if random.random() < aggr_rate:
            agg = dna["aggression"]
            if force_aggression_boost:
                agg += abs(random.uniform(0, settings.MUTATION_STRENGTH))
            else:
                agg += random.uniform(-settings.MUTATION_STRENGTH, settings.MUTATION_STRENGTH)
            new_dna["aggression"] = clamp(agg, 0.0, 1.0)
        return new_dna

    def log_stats(self, frame_count):
        # Klasör ve dosya kontrolü
        log_dir = 'logs'
        log_file = os.path.join(log_dir, 'simulation_data.csv')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_exists = os.path.isfile(log_file)
        pop = len(self.blobs)
        avg_speed = avg_size = avg_vision = 0.0
        meta_counts = {"day": 0, "night": 0, "neutral": 0}
        food_counts = {"green": 0, "red": 0, "blue": 0}
        if pop > 0:
            avg_speed = sum(b.dna["speed"] for b in self.blobs) / pop
            avg_size = sum(b.dna["size"] for b in self.blobs) / pop
            avg_vision = sum(b.dna["vision"] for b in self.blobs) / pop
            for b in self.blobs:
                meta = b.dna["metabolism"]
                if meta in meta_counts:
                    meta_counts[meta] += 1
                pf = b.dna["preferred_food"]
                if pf in food_counts:
                    food_counts[pf] += 1
        with open(log_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow([
                    'Frame', 'Population', 'Avg Speed', 'Avg Size', 'Avg Vision',
                    'Day Count', 'Night Count', 'Neutral Count',
                    'Pref Green', 'Pref Red', 'Pref Blue'])
            writer.writerow([
                frame_count, pop, f"{avg_speed:.3f}", f"{avg_size:.2f}", f"{avg_vision:.2f}",
                meta_counts['day'], meta_counts['night'], meta_counts['neutral'],
                food_counts['green'], food_counts['red'], food_counts['blue']
            ])

    def update(self):
        """
        Simülasyonun bir adımını günceller.
        Tüm blob ve food nesnelerinin update() fonksiyonu çağrılır.
        Ölen blob'lar listeden temizlenir.
        Blob'lar, yakınlarındaki food nesnelerini yiyerek enerji kazanır.
        Yeterli enerjiye sahip blob'lar üreyebilir ve mutasyon geçirebilir.
        Her 300 frame'de bir popülasyonun genetik istatistikleri console'a yazdırılır.
        Ayrıca, belirli aralıklarla yeni food nesneleri eklenir (respawn).
        """
        self.frame_count += 1  # Frame sayacını artır
        # Gün sayacı: her FRAMES_PER_DAY frame'de bir artar
        if self.frame_count % settings.FRAMES_PER_DAY == 0:
            self.day += 1
            # İlk 5 günün başında extra food desteği
            if self.day <= 5:
                extra_foods = create_balanced_foods(settings.INITIAL_FOOD_COUNT, birth_frame=self.frame_count)
                self.foods.extend(extra_foods)
        new_blobs = []  # Bu adımda doğan yeni blob'lar
        # Gün/gece oranı (0.0 = gündüz, 1.0 = gece)
        if settings.DAY_NIGHT_CYCLE:
            cycle_pos = (self.frame_count % settings.FRAMES_PER_DAY) / settings.FRAMES_PER_DAY
            if cycle_pos < 0.5:
                day_night_ratio = cycle_pos * 2  # 0.0-1.0 gündüzden geceye
            else:
                day_night_ratio = 1.0 - (cycle_pos - 0.5) * 2  # 1.0-0.0 geceden gündüze
        else:
            day_night_ratio = 0.0
        pop = self._species_population()
        avg_aggr = sum(b.dna["aggression"] for b in self.blobs) / len(self.blobs) if self.blobs else 0
        force_aggr_boost = avg_aggr < 0.05
        for blob in self.blobs:
            # FPS koruması: tür limiti aşıldıysa üreme baskılanır
            if hasattr(blob, 'species') and pop[blob.species] >= settings.SPECIES[blob.species]['max_population']:
                blob.can_reproduce = False
            else:
                blob.can_reproduce = True
            # Central zone risk/reward
            if self._in_zone(blob, settings.ZONE_E):
                blob.energy -= settings.ZONE_E_ENTRY_PENALTY
                if random.random() < settings.ZONE_E_RANDOM_EVENT_CHANCE:
                    effect = random.choice(settings.ZONE_E_RANDOM_EFFECTS)
                    if effect == 'stun':
                        blob.stunned = True
                    elif effect == 'random_move':
                        blob.x = random.uniform(settings.ZONE_E[0], settings.ZONE_E[0]+settings.ZONE_E[2])
                        blob.y = random.uniform(settings.ZONE_E[1], settings.ZONE_E[1]+settings.ZONE_E[3])
                    elif effect == 'aggression_spike':
                        blob.dna['aggression'] = min(1.0, blob.dna['aggression'] + 0.2)
        # Aggression ortalamasını hesapla
        pop = len(self.blobs)
        avg_aggr = sum(b.dna["aggression"] for b in self.blobs) / pop if pop > 0 else 0
        force_aggr_boost = avg_aggr < 0.05
        for blob in self.blobs:
            visible_foods = [f for f in self.foods if not f.is_eaten and not f.is_rotten and math.hypot(blob.x - f.x, blob.y - f.y) < blob.dna["vision"]]
            visible_blobs = [b for b in self.blobs if b is not blob and math.hypot(blob.x - b.x, blob.y - b.y) < blob.dna["vision"]]
            blob.update(visible_foods, visible_blobs, day_night_ratio, self.blobs)
            # Yemek yeme (çarpışma kontrolü)
            for food in self.foods:
                if food.is_eaten or food.is_rotten:
                    continue
                dx = blob.x - food.x
                dy = blob.y - food.y
                distance = math.hypot(dx, dy)
                blob_radius = int(blob.dna["size"])
                if distance < blob_radius + settings.FOOD_RADIUS:
                    eat_ratio = blob.can_eat(food)
                    if eat_ratio > 0:
                        food.is_eaten = True
                        blob.energy += food.energy * blob.dna["efficiency"] * eat_ratio
                        blob.energy = min(blob.energy, settings.BLOB_MAX_ENERGY)
            # --- Avcılık davranışı ---
            if not visible_foods and blob.dna["aggression"] > settings.AGGRESSION_THRESHOLD:
                potential_prey = [b for b in self.blobs if b is not blob and b.dna["size"] < blob.dna["size"] * settings.SIZE_MARGIN]
                if potential_prey:
                    closest_prey = min(potential_prey, key=lambda b: math.hypot(blob.x - b.x, blob.y - b.y))
                    prey_dist = math.hypot(blob.x - closest_prey.x, blob.y - closest_prey.y)
                    if prey_dist < 5:
                        energy_gain = closest_prey.energy * settings.HUNT_ENERGY_GAIN_RATIO
                        blob.energy += energy_gain
                        blob.energy = min(blob.energy, settings.BLOB_MAX_ENERGY)
                        closest_prey.energy = 0
            # --- Kaçış davranışı ---
            if blob.dna["aggression"] < settings.ESCAPE_AGGRESSION_THRESHOLD:
                threats = [b for b in visible_blobs if b.dna["size"] > blob.dna["size"] / settings.ESCAPE_SIZE_RATIO and b.dna["aggression"] > settings.AGGRESSION_THRESHOLD]
                if threats:
                    threat = min(threats, key=lambda b: math.hypot(blob.x - b.x, blob.y - b.y))
                    dx = blob.x - threat.x
                    dy = blob.y - threat.y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        escape_step = blob.dna["speed"] * 1.2
                        blob.x += (dx / dist) * escape_step
                        blob.y += (dy / dist) * escape_step
            # Üreme için dinamik eşik
            reproduction_threshold = settings.BASE_THRESHOLD + blob.dna["size"] * settings.SIZE_FACTOR
            if blob.energy >= settings.REPRODUCTION_COST + reproduction_threshold:
                # Ebeveynin DNA'sı kopyalanır ve mutasyona uğratılır
                child_dna = self.mutate_dna(blob.dna, force_aggr_boost)
                # Yeni doğan konumu: ebeveynin etrafında rastgele açı ve 10-20 piksel mesafe
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(10, 20)
                child_x = blob.x + math.cos(angle) * distance
                child_y = blob.y + math.sin(angle) * distance
                # Kenar kontrolü (margin = BLOB_RADIUS)
                margin = settings.BLOB_RADIUS
                child_x = max(margin, min(child_x, settings.SCREEN_WIDTH - margin))
                child_y = max(margin, min(child_y, settings.SCREEN_HEIGHT - margin))
                child = Blob(
                    x=child_x,
                    y=child_y,
                    dna=child_dna,
                    energy=settings.BLOB_INITIAL_ENERGY,
                    is_newborn=True,
                    newborn_max_age=40,
                    species=blob.species
                )
                new_blobs.append(child)
                blob.energy -= settings.REPRODUCTION_COST
                # TODO: Üreme animasyonu veya istatistikleri eklenebilir
        # Food nesnelerini güncelle (şimdilik pasif)
        for food in self.foods:
            food.update(current_frame=self.frame_count)
        # Enerjisi biten blob'ları listeden çıkar
        self.blobs = [blob for blob in self.blobs if not blob.is_dead()]
        # Yenen veya çürüyen yiyecekleri sil
        self.foods = [food for food in self.foods if not food.is_eaten and not food.is_rotten]
        # Yeni doğan blob'ları ekle
        self.blobs.extend(new_blobs)

        # Yeni doğan blob'ları eklemeden önce tür başına limit kontrolü
        pop = self._species_population()
        for child in new_blobs:
            if hasattr(child, 'species') and child.species in pop:
                if pop[child.species] < settings.SPECIES[child.species]['max_population']:
                    self.blobs.append(child)
                    pop[child.species] += 1
                else:
                    # Overflow: En yaşlı veya en zayıf blobu öldür
                    candidates = [b for b in self.blobs if b.species == child.species]
                    if candidates:
                        # Önce en yaşlıyı, yoksa en düşük enerjiliyi öldür
                        oldest = max(candidates, key=lambda b: b.age)
                        oldest.is_alive = False
                        self.blobs = [b for b in self.blobs if b.is_alive]
                        self.blobs.append(child)
                        pop[child.species] = sum(1 for b in self.blobs if b.species == child.species)
        # ...existing code...

        # Belirli aralıklarla yeni food üretimi (respawn)
        if self.frame_count % settings.FOOD_RESPAWN_INTERVAL == 0:
            # Rastgele konumda yeni yiyecekler oluştur ve ekle
            new_foods = create_balanced_foods(settings.FOOD_RESPAWN_AMOUNT, birth_frame=self.frame_count)
            self.foods.extend(new_foods)
            # print(f"[FRAME {self.frame_count}] {FOOD_RESPAWN_AMOUNT} yeni yiyecek eklendi.")

        # Gün bazında istatistik yazdır (sadece gün sonunda)
        if self.frame_count % settings.FRAMES_PER_DAY == 0:
            pop = len(self.blobs)
            if pop > 0:
                avg_speed = sum(b.dna["speed"] for b in self.blobs) / pop
                avg_size = sum(b.dna["size"] for b in self.blobs) / pop
                avg_vision = sum(b.dna["vision"] for b in self.blobs) / pop
                avg_eff = sum(b.dna["efficiency"] for b in self.blobs) / pop
                avg_aggr = sum(b.dna["aggression"] for b in self.blobs) / pop
                meta_counts = {m: 0 for m in METABOLISM_TYPES}
                food_pref_counts = {ft: 0 for ft in settings.FOOD_TYPES}
                for b in self.blobs:
                    meta_counts[b.dna["metabolism"]] += 1
                    food_pref_counts[b.dna["preferred_food"]] += 1
                print(f"[GÜN {self.day}] Pop: {pop} | FoodPref: "
                      + " ".join(f"{ft}={food_pref_counts[ft]}" for ft in settings.FOOD_TYPES)
                      + f" | Speed: {avg_speed:.2f} | Size: {avg_size:.1f} | Vision: {avg_vision:.1f} | Eff: {avg_eff:.2f} | Agg: {avg_aggr:.3f} | Meta: "
                      + " ".join(f"{m}={meta_counts[m]}" for m in METABOLISM_TYPES))
            else:
                print(f"[GÜN {self.day}] Popülasyon yok.")

        # Her 100 frame'de bir istatistikleri logla
        if self.frame_count % 100 == 0:
            self.log_stats(self.frame_count)

        # --- Central zone risk/reward ---
        for blob in self.blobs:
            if self._in_zone(blob, settings.ZONE_E):
                blob.energy -= settings.ZONE_E_ENTRY_PENALTY
                # Rastgele event
                if random.random() < settings.ZONE_E_RANDOM_EVENT_CHANCE:
                    effect = random.choice(settings.ZONE_E_RANDOM_EFFECTS)
                    if effect == 'stun':
                        blob.stunned = True
                    elif effect == 'random_move':
                        blob.x = random.uniform(settings.ZONE_E[0], settings.ZONE_E[0]+settings.ZONE_E[2])
                        blob.y = random.uniform(settings.ZONE_E[1], settings.ZONE_E[1]+settings.ZONE_E[3])
                    elif effect == 'aggression_spike':
                        blob.dna['aggression'] = min(1.0, blob.dna['aggression'] + 0.2)
        # --- Per-species population cap: üreme baskılanır ---
        pop = self._species_population()
        for blob in self.blobs:
            if hasattr(blob, 'species') and pop[blob.species] >= settings.SPECIES[blob.species]['max_population']:
                blob.can_reproduce = False
            else:
                blob.can_reproduce = True

    def _in_zone(self, blob, zone):
        return (zone[0] <= blob.x < zone[0]+zone[2]) and (zone[1] <= blob.y < zone[1]+zone[3])

    def draw(self, screen):
        """
        Simülasyonun mevcut durumunu ekrana çizer.
        Tüm blob ve food nesnelerinin draw(screen) fonksiyonu çağrılır.
        Ölü bloblar fade-out için çizilmeye devam eder.
        """
        for food in self.foods:
            food.draw(screen)
        for blob in self.blobs:
            blob.draw(screen)
        # Fade-out animasyonu için ölü bloblar da çizilebilir (isteğe bağlı olarak ayrı bir listede tutulabilir)