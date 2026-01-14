import random
import math
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt


# ============================================================
# 1. Global configuration
# ============================================================

TELEOP_DURATION = 135.0  # seconds
DT = 0.25                # time step (seconds)
POPULATION_SIZE = 40
GENERATIONS = 60
MUTATION_RATE = 0.12
TOURNAMENT_SIZE = 4

# Roles
ROLE_HOPPER = 0
ROLE_FEEDER = 1
ROLE_SHOOTER = 2
ROLE_HYBRID = 3
ROLE_DEFENDER = 4
ALL_ROLES = [ROLE_HOPPER, ROLE_FEEDER, ROLE_SHOOTER, ROLE_HYBRID, ROLE_DEFENDER]

# Path choices (encode congestion patterns)
PATH_CENTER_BUMP = 0       # center collection, cross bump, score
PATH_CENTER_SIDE = 1       # center collection, side route, score
PATH_WING_SIDE = 2         # wing collection, side route, score
ALL_PATHS = [PATH_CENTER_BUMP, PATH_CENTER_SIDE, PATH_WING_SIDE]

# Zones for congestion modeling
ZONE_CENTER = "center"
ZONE_BUMP = "bump"
ZONE_SIDE = "side"
ZONE_SCORE = "score"

ZONE_LIST = [ZONE_CENTER, ZONE_BUMP, ZONE_SIDE, ZONE_SCORE]


# ============================================================
# 2. Genome structure
# ============================================================

def random_robot() -> Dict:
    """Create a random robot genome."""
    role = random.choice(ALL_ROLES)
    path = random.choice(ALL_PATHS)

    robot = {
        "role": role,
        "path_choice": path,

        # Rates: balls per second
        "collection_rate_center": random.uniform(0.5, 4.5),
        "collection_rate_wing": random.uniform(0.5, 4.5),
        "shooting_rate": random.uniform(0.5, 4.5),

        # Base travel times for segments (seconds)
        "travel_center_to_bump": random.uniform(1.0, 6.0),
        "travel_center_to_side": random.uniform(0.7, 5.0),
        "travel_side_to_score": random.uniform(0.7, 5.0),
        "travel_bump_to_score": random.uniform(0.7, 5.0),

        # Accuracy
        "accuracy_open": random.uniform(0.6, 0.98),
        "accuracy_defended": random.uniform(0.3, 0.9),

        # Capacity
        "max_capacity": random.uniform(8, 60),

        # Behavior weights
        "cycle_size_preference": random.uniform(0.3, 1.0),   # fraction of capacity per cycle
        "defend_aggressiveness": random.uniform(0.0, 1.0),   # how willing to defend vs score
    }

    return robot


def random_genome() -> List[Dict]:
    """An alliance of 3 robots."""
    return [random_robot(), random_robot(), random_robot()]


# ============================================================
# 3. Helper: path → zone sequence
# ============================================================

def path_to_zones(path_choice: int) -> List[str]:
    """
    Map a path choice to a sequence of zones visited during a cycle.
    Simplified: collect, travel, score, travel back.
    """
    if path_choice == PATH_CENTER_BUMP:
        # center -> bump -> score -> bump -> center
        return [ZONE_CENTER, ZONE_BUMP, ZONE_SCORE, ZONE_BUMP, ZONE_CENTER]
    elif path_choice == PATH_CENTER_SIDE:
        # center -> side -> score -> side -> center
        return [ZONE_CENTER, ZONE_SIDE, ZONE_SCORE, ZONE_SIDE, ZONE_CENTER]
    elif path_choice == PATH_WING_SIDE:
        # wing collection uses side instead of center
        return [ZONE_SIDE, ZONE_SIDE, ZONE_SCORE, ZONE_SIDE, ZONE_SIDE]
    else:
        return [ZONE_CENTER, ZONE_SIDE, ZONE_SCORE, ZONE_SIDE, ZONE_CENTER]


# ============================================================
# 4. Opponent model
# ============================================================

def opponent_defender_zone(t: float) -> str:
    """
    Simple opponent defender model:
    - Spends most of the time near SCORE and BUMP.
    - Occasionally drifts to CENTER.
    Time-based rotation for variability.
    """
    phase = (t // 10) % 3
    if phase == 0:
        return ZONE_SCORE
    elif phase == 1:
        return ZONE_BUMP
    else:
        return ZONE_CENTER



# ============================================================
# 5. Time-step simulation of one alliance
# ============================================================

def simulate_alliance(genome: List[Dict],
                      record_congestion: bool = False
                      ) -> Tuple[float, Dict[str, List[int]]]:
    """
    Time-step simulation of Teleop for one alliance.
    Returns:
        fitness (points)
        congestion_history: dict zone -> list[#robots] per time step
    """
    steps = int(TELEOP_DURATION / DT)
    balls_scored_total = 0.0

    # Initialize robot state
    robots_state = []
    for robot in genome:
        # Derived parameters per robot
        role = robot["role"]
        capacity = robot["max_capacity"]
        cycle_frac = robot["cycle_size_preference"]
        cycle_load = max(1.0, capacity * cycle_frac)

        # Choose main collection rate based on path
        if robot["path_choice"] == PATH_WING_SIDE:
            collection_rate = robot["collection_rate_wing"]
        else:
            collection_rate = robot["collection_rate_center"]

        state = {
            "robot": robot,
            "role": role,
            "path": robot["path_choice"],
            "cycle_load": cycle_load,
            "collection_rate": collection_rate,
            "shooting_rate": robot["shooting_rate"],
            "accuracy_open": robot["accuracy_open"],
            "accuracy_defended": robot["accuracy_defended"],
            "defend_aggressiveness": robot["defend_aggressiveness"],

            "zone_sequence": path_to_zones(robot["path_choice"]),
            "phase_index": 0,          # which leg of the path
            "phase_time_remaining": 0, # time left in current leg
            "balls_in_robot": 0.0,
            "mode": "collect",         # "collect", "travel", "shoot"
        }

        # Initialize starting in first zone of sequence
        state["current_zone"] = state["zone_sequence"][0]
        robots_state.append(state)

    # Congestion tracking
    congestion_history = {z: [0] * steps for z in ZONE_LIST}

    # Simulation loop
    for step in range(steps):
        t = step * DT

        # 1) Count robots per zone at start of step
        zone_counts = {z: 0 for z in ZONE_LIST}
        for rs in robots_state:
            zone_counts[rs["current_zone"]] += 1

        # Record congestion if requested
        if record_congestion:
            for z in ZONE_LIST:
                congestion_history[z][step] = zone_counts[z]

        # Opponent defender zone this step
        defender_zone = opponent_defender_zone(t)

        # 2) Update each robot
        for rs in robots_state:
            robot = rs["robot"]
            role = rs["role"]

            # Decide if this robot actually plays defense instead of cycling
            # (very simple heuristic: high defend_aggressiveness + not HQ scorer)
            if role == ROLE_DEFENDER and rs["defend_aggressiveness"] > 0.5:
                # If acting as defender, it won't score; skip
                continue

            # Congestion factor for this robot's current zone
            robots_here = zone_counts[rs["current_zone"]]
            congestion_factor = 1.0 + 0.2 * max(0, robots_here - 1)

            # Opponent defense: if in same zone as defender, apply defended mode
            is_defended = (rs["current_zone"] == defender_zone)
            if is_defended:
                accuracy = rs["accuracy_defended"]
                defense_travel_penalty = 1.2
            else:
                accuracy = rs["accuracy_open"]
                defense_travel_penalty = 1.0

            # Effective dt considering congestion + defense (for travel phases)
            eff_DT_travel = DT * congestion_factor * defense_travel_penalty

            # State machine
            if rs["mode"] == "collect":
                # Collect until cycle_load reached
                collect_rate = rs["collection_rate"]
                # Effective collection rate slowed by congestion
                eff_collect_rate = collect_rate / congestion_factor
                rs["balls_in_robot"] += eff_collect_rate * DT

                if rs["balls_in_robot"] >= rs["cycle_load"]:
                    rs["balls_in_robot"] = rs["cycle_load"]
                    # Move to travel toward scoring
                    rs["mode"] = "travel"
                    rs["phase_index"] = 1  # go to second zone in sequence
                    rs["phase_time_remaining"] = travel_time_for_leg(
                        rs, leg_index=1
                    )

            elif rs["mode"] == "travel":
                # Travel along zone sequence segments
                rs["phase_time_remaining"] -= eff_DT_travel
                if rs["phase_time_remaining"] <= 0:
                    # Arrive at next zone
                    rs["current_zone"] = rs["zone_sequence"][rs["phase_index"]]
                    rs["phase_index"] += 1

                    # If we reached scoring zone, switch to shoot
                    if rs["current_zone"] == ZONE_SCORE:
                        rs["mode"] = "shoot"
                    else:
                        # Still traveling to next zone
                        if rs["phase_index"] < len(rs["zone_sequence"]):
                            rs["phase_time_remaining"] = travel_time_for_leg(
                                rs, leg_index=rs["phase_index"]
                            )
                        else:
                            # Safety: restart cycle from beginning
                            rs["mode"] = "collect"
                            rs["phase_index"] = 0
                            rs["current_zone"] = rs["zone_sequence"][0]

            elif rs["mode"] == "shoot":
                # Shoot balls at shooting_rate, apply accuracy
                eff_shoot_rate = rs["shooting_rate"] / congestion_factor
                balls_shot = eff_shoot_rate * DT

                if balls_shot > rs["balls_in_robot"]:
                    balls_shot = rs["balls_in_robot"]

                scored = balls_shot * accuracy
                balls_scored_total += scored
                rs["balls_in_robot"] -= balls_shot

                if rs["balls_in_robot"] <= 0.0:
                    # Done scoring, travel back to start zone and repeat cycle
                    rs["balls_in_robot"] = 0.0
                    rs["mode"] = "travel"
                    # After score zone, we assume last legs of path lead back to start
                    rs["phase_index"] = rs["zone_sequence"].index(ZONE_SCORE) + 1
                    if rs["phase_index"] >= len(rs["zone_sequence"]):
                        # If no legs defined after score, go back to collect
                        rs["mode"] = "collect"
                        rs["phase_index"] = 0
                        rs["current_zone"] = rs["zone_sequence"][0]
                    else:
                        rs["phase_time_remaining"] = travel_time_for_leg(
                            rs, leg_index=rs["phase_index"]
                        )

    # Points per ball; adjust as needed
    points_per_ball = 1.0
    fitness = balls_scored_total * points_per_ball
    return fitness, congestion_history


def travel_time_for_leg(rs: Dict, leg_index: int) -> float:
    """
    Estimate travel time for a leg of the path (between two consecutive zones).
    Very simplified: we use robot's travel_x parameters depending on zones.
    """
    robot = rs["robot"]
    zseq = rs["zone_sequence"]
    if leg_index <= 0 or leg_index >= len(zseq):
        return 0.0

    z_from = zseq[leg_index - 1]
    z_to = zseq[leg_index]

    if z_from == ZONE_CENTER and z_to == ZONE_BUMP:
        return robot["travel_center_to_bump"]
    if z_from == ZONE_CENTER and z_to == ZONE_SIDE:
        return robot["travel_center_to_side"]
    if z_from == ZONE_SIDE and z_to == ZONE_SCORE:
        return robot["travel_side_to_score"]
    if z_from == ZONE_BUMP and z_to == ZONE_SCORE:
        return robot["travel_bump_to_score"]

    # Return something modest for undefined pairs
    return 2.0


# ============================================================
# 6. GA operators + revised fitness
# ============================================================

def tournament_selection(population, fitnesses, k=TOURNAMENT_SIZE):
    idxs = random.sample(range(len(population)), k)
    return population[max(idxs, key=lambda i: fitnesses[i])]


def crossover(parent1: List[Dict], parent2: List[Dict]) -> List[Dict]:
    child = []
    for r in range(3):
        if random.random() < 0.5:
            child.append(parent1[r].copy())
        else:
            child.append(parent2[r].copy())
    return child


def mutate_robot(robot: Dict, mutation_rate: float) -> None:
    if random.random() < mutation_rate:
        robot["role"] = random.choice(ALL_ROLES)
    if random.random() < mutation_rate:
        robot["path_choice"] = random.choice(ALL_PATHS)

    def mutate(key, lo, hi, scale=0.25):
        if random.random() < mutation_rate:
            val = robot[key]
            span = (hi - lo) * scale
            val += random.uniform(-span, span)
            robot[key] = max(lo, min(hi, val))

    mutate("collection_rate_center", 0.3, 5.0)
    mutate("collection_rate_wing", 0.3, 5.0)
    mutate("shooting_rate", 0.3, 5.0)
    mutate("travel_center_to_bump", 0.7, 8.0)
    mutate("travel_center_to_side", 0.5, 7.0)
    mutate("travel_side_to_score", 0.5, 7.0)
    mutate("travel_bump_to_score", 0.5, 7.0)
    mutate("accuracy_open", 0.4, 0.99)
    mutate("accuracy_defended", 0.2, 0.95)
    mutate("max_capacity", 5.0, 70.0)
    mutate("cycle_size_preference", 0.2, 1.0)
    mutate("defend_aggressiveness", 0.0, 1.0)


def mutate(genome: List[Dict], mutation_rate: float) -> None:
    for robot in genome:
        mutate_robot(robot, mutation_rate)


def run_ga():
    population = [random_genome() for _ in range(POPULATION_SIZE)]
    fitness_history = []
    role_history = []   # list of dicts: {"hopper": x, "feeder": y, ...}


    for gen in range(GENERATIONS):
        fitnesses = []
        generation_roles = {"hopper": 0, "feeder": 0, "shooter": 0, "hybrid": 0, "defender": 0}

        for g in population:
            fit, _ = simulate_alliance(g, record_congestion=False)
            fitnesses.append(fit)

            # Count roles
            for robot in g:
                if robot["role"] == 0:
                    generation_roles["hopper"] += 1
                elif robot["role"] == 1:
                    generation_roles["feeder"] += 1
                elif robot["role"] == 2:
                    generation_roles["shooter"] += 1
                elif robot["role"] == 3:
                    generation_roles["hybrid"] += 1
                elif robot["role"] == 4:
                    generation_roles["defender"] += 1

        # Save history
        best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        best_fit = fitnesses[best_idx]
        fitness_history.append(best_fit)
        role_history.append(generation_roles)

        print(f"Generation {gen}: best fitness = {best_fit:.1f}")

        # GA reproduction
        new_pop = []
        new_pop.append(population[best_idx])  # elitism

        while len(new_pop) < POPULATION_SIZE:
            p1 = tournament_selection(population, fitnesses)
            p2 = tournament_selection(population, fitnesses)
            child = crossover(p1, p2)
            mutate(child, MUTATION_RATE)
            new_pop.append(child)

        population = new_pop


    final_fitnesses = []
    for g in population:
        fit, _ = simulate_alliance(g, record_congestion=False)
        final_fitnesses.append(fit)

    best_idx = max(range(len(population)), key=lambda i: final_fitnesses[i])
    best_genome = population[best_idx]
    best_fit = final_fitnesses[best_idx]

    print("\nBest genome after evolution:")
    for r in best_genome:
        print(r)
    print(f"Best fitness: {best_fit:.1f}")

    return best_genome


# ============================================================
# 7. Visualization of congestion over time
# ============================================================

def visualize_congestion(genome: List[Dict]):
    fitness, congestion_history = simulate_alliance(genome, record_congestion=True)
    steps = len(congestion_history[ZONE_CENTER])
    times = [i * DT for i in range(steps)]

    plt.figure(figsize=(10, 6))
    for z in ZONE_LIST:
        plt.plot(times, congestion_history[z], label=f"Zone: {z}")

    plt.xlabel("Time (s)")
    plt.ylabel("# robots in zone")
    plt.title(f"Congestion over time (fitness = {fitness:.1f})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ============================================================
# 8. Main
# ============================================================

if __name__ == "__main__":
    best = run_ga()
    visualize_congestion(best)
