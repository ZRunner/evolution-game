# Window dimensions
from typing import Optional


HEIGHT: int = 800
WIDTH: int = 1200

# Number of parallel processes to use, None to get 1 per CPU
PROCESSES_COUNT: Optional[int] = None

# Max frames per second
FPS: int = 60

# Friction coefficient used in acceleration calculs
FRICTION: float = 0.2

# Approximative Initial food quantities per generator
INITIAL_FOOD_QUANTITY: int = 200

# Creatures count at the beginning
CREATURES_COUNT: int = 200

# Energy points each creature has at the beginning
CREATURE_STARTING_ENERGY: int = 30

# Minimum food ready to be digested at the beginning
CREATURE_MIN_STARTING_DIGESTING_POINTS: int = 6

# Maximum creature acceleration (on each axis)
MAX_CREATURE_ACC: float = 0.0001

# Maximum creature veolocity (on each axis)
MAX_CREATURE_VEL: float = 0.08

# Maximum reature velocity decrease coefficient (on each axis)
CREATURE_DECELERATION: float = 1e-5

# Amount of energy lost by idle creatures each second
CREATURE_STILL_ENERGY: float = 0.15

# Minimum creature size
MIN_CREATURE_SIZE: int = 1

# Average and simga creature size (using a gaussian curve)
CREATURE_SIZE_AVG: int = 4
CREATURE_SIZE_SIGMA: int = 3

# Minimum connections number in a creature neural network
CREATURES_MIN_CONNECTIONS: int = 2

# Maximum connections number in a creature neural network
CREATURES_MAX_CONNECTIONS: int = 12

# Maximum transitions ("hidden") neurons in a creature neural network
CREATURES_MAX_HIDDEN_NEURONS: int = 25

# Maximum visibility of emitted light
CREATURE_MAX_LIGHT_DISTANCE_EMISSION: int = 200

# Minimum neuron value for a creature to reproduce with a partner
CREATURE_MIN_REPRODUCTION_STATE: float = 0.1

# Minimum time in seconds between two reproductions from the same creature
CREATURE_REPRO_COOLDOWN: int = 20
