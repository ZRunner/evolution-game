# Window dimensions
from typing import Optional

HEIGHT: int = 1200
WIDTH: int = 2200

# Number of parallel processes to use, None to get 1 per CPU
PROCESSES_COUNT: Optional[int] = None

# Max frames per second
FPS: int = 60

# Game speed (1 = real time, 2 = 2x faster, etc.)
GAME_SPEED: float = 1.0

# RAM debug mode
MEMORY_DEBUG: bool = False

# Show the map grid (for debug purposes)
SHOW_GRID: bool = False

# Seconds of historical data shown in graphs
GRAPH_WINDOW: int = 150

# Friction coefficient used in acceleration calculs
FRICTION: float = 0.9

# Approximative Initial food quantities per generator
INITIAL_FOOD_QUANTITY: int = 500

# Duration in seconds between each food generation
FOOD_GENERATION_INTERVAL: int = 35

# Maximum food quantity per generation
MAX_FOOD_GENERATED_PER_CYCLE: int = 100

# Maximum food quantity at any time
MAX_FOOD_QUANTITY: int = 1000

# Creatures count at the beginning
INITIAL_CREATURES_COUNT: int = 200

# Max creatures count at any time
MAX_CREATURES_COUNT: int = 1000

# Energy points each creature has at the beginning of the game
CREATURE_STARTING_ENERGY: int = 30

# Coefficient to determine the maximum energy that a creature has based on size
CREATURE_MAX_ENERGY_COEFFICIENT: int = 30

# Minimum food ready to be digested at the beginning
CREATURE_MIN_STARTING_DIGESTING_POINTS: int = 6

# Maximum creature acceleration (on each axis)
MAX_CREATURE_ACC: float = 0.001

# Maximum creature veolocity (on each axis)
MAX_CREATURE_VEL: float = 0.07

# Maximum creature velocity decrease coefficient (on each axis)
CREATURE_DECELERATION: float = 5e-7

# Amount of energy lost by idle creatures each second
CREATURE_STILL_ENERGY: float = 0.08

# Minimum creature size
MIN_CREATURE_SIZE: int = 1

# Average and simga creature size (using a gaussian curve)
CREATURE_SIZE_AVG: int = 4
CREATURE_SIZE_SIGMA: int = 3

# Average and sigma max damages done by a creature (gaussian curve)
CREATURE_DMG_AVG: int = 5
CREATURE_DMG_SIGMA: int = 2

# Minimum connections number in a creature neural network
CREATURES_MIN_CONNECTIONS: int = 2

# Maximum connections number in a creature neural network
CREATURES_MAX_CONNECTIONS: int = 30

# Maximum transitions ("hidden") neurons in a creature neural network
CREATURES_MAX_HIDDEN_NEURONS: int = 30

# Maximum visibility of emitted light
CREATURE_MAX_LIGHT_DISTANCE_EMISSION: int = 200

# Minimum neuron value for a creature to inflict damage
CREATURE_MIN_ATTACK_STATE: float = 0.3

# Minimum time in seconds between two damage actions
CREATURE_ATTACK_COOLDOWN: float = 1.0

# Minimum neuron value for a creature to reproduce with a partner
CREATURE_MIN_REPRODUCTION_STATE: float = 0.1

# Minimum time in seconds between two reproductions from the same creature
CREATURE_REPRO_COOLDOWN: int = 20

# Energy consumed by a creature when reproducing, multiplied by the size of the child
CREATURE_REPRO_ENERGY_FACTOR: float = 10.0

# Initial energy percentage of a child (multiplied by the energy lost by both parents)
CHILD_INITIAL_ENERGY_PERCENT: float = 0.6

# Initial life percentage of a child (multiplied by the average life percentage of both parents)
CHILD_INITIAL_LIFE_PERCENT: float = 0.7
