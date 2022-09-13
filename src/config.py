# Window dimensions
HEIGHT: int = 800
WIDTH: int = 1200

# Max frames per second
FPS: int = 60

# Friction coefficient used in acceleration calculs
FRICTION: float = 0.2

# Creatures count at the beginning
CREATURES_COUNT: int = 200

# Energy points each creature has at the beginning
CREATURE_STARTING_ENERGY = 30

# Minimum food ready to be digested at the beginning
CREATURE_MIN_STARTING_DIGESTING_POINTS = 6

# Maximum creature acceleration (on each axis)
MAX_CREATURE_ACC = 0.0001

# Maximum creature veolocity (on each axis)
MAX_CREATURE_VEL = 0.1

# Maximum reature velocity decrease coefficient (on each axis)
CREATURE_DECELERATION = 1e-5

# Amount of energy lost by idle creatures each second
CREATURE_STILL_ENERGY = 0.15

# Minimum creature size
MIN_CREATURE_SIZE = 1

# Average and simga creature size (using a gaussian curve)
CREATURE_SIZE_AVG = 4
CREATURE_SIZE_SIGMA = 3

# Minimum connections number in a creature neural network
CREATURES_MIN_CONNECTIONS = 2

# Maximum connections number in a creature neural network
CREATURES_MAX_CONNECTIONS = 10

# Maximum transitions ("hidden") neurons in a creature neural network
CREATURES_MAX_HIDDEN_NEURONS = 20

# Maximum visibility of emitted light
CREATURE_MAX_LIGHT_DISTANCE_EMISSION = 200

# Minimum neuron value for a creature to reproduce with a partner
CREATURE_MIN_REPRODUCTION_STATE = 0.2

# Minimum time in seconds between two reproductions from the same creature
CREATURE_REPRO_COOLDOWN = 15