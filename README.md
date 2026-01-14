# FRC-2026
This repository has a python script to run optimization/simulation of the rebuilt game.
The optimization software has different robots with strenghts/weaknesses and the goal is to determine
what is the optimal features combination.
________________________________________
🟦 ROLE 0 — Hopper
Core identity: High capacity, high throughput cycler
This robot is designed to collect a lot of Fuel and score it itself. It’s the classic “vacuum + shooter” robot.
Typical traits in the simulation
-	Very high center collection rate
-	Large max capacity (40–70 balls)
-	Prefers large cycles (cycle_size_preference ~0.8–1.0)
-	Uses center→bump→score or center→side→score paths
-	High shooting rate
-	High accuracy
-	Low defend aggressiveness
Strategic purpose
-	Main scoring engine
-	Best for raw Teleop throughput
-	Most sensitive to congestion in the center
________________________________________
🟩 ROLE 1 — Feeder
Core identity: Support robot that collects and delivers Fuel
This robot is meant to reduce congestion and support other scorers.
Typical traits
-	High collection rate (center or wing)
-	Large capacity
-	Medium or high shooting rate
-	Often avoids defended zones
-	Low defend aggressiveness
-	Often uses wing→side→score path
Strategic purpose
-	Reduce center congestion
-	Provide Fuel to shooters
-	Score when not feeding
-	Complement hopper robots
________________________________________
🟧 ROLE 2 — Shooter
Core identity: Fast cycle scoring specialist
This robot focuses on quick cycles, not huge capacity.
Typical traits
-	Medium cycle size
-	Very fast travel times
-	High accuracy
-	High shooting rate
-	Often uses center→side→score path
-	Low defend aggressiveness
Strategic purpose
-	Score frequently with small cycles
-	Avoid congestion by using side lanes
-	Provide consistent scoring even when center is contested
________________________________________
🟪 ROLE 3 — Hybrid
Core identity: Flexible robot that mixes behaviors
This robot can behave like a hopper, feeder, or shooter depending on:
-	Path choice
-	Collection rates
-	Travel times
-	Cycle size preference
Typical traits
-	Balanced stats
-	Medium or large capacity
-	Good accuracy
-	Moderate travel times
-	Can operate in center or wing
Strategic purpose
-	Adapt to congestion
-	Fill gaps in alliance composition
-	Provide redundancy
________________________________________
🟥 ROLE 4 — Defender
Core identity: Robot that disrupts opponents
This robot focuses on reducing opponent scoring rather than maximizing its own.
Typical traits
-	High defend aggressiveness
-	Lower shooting or collection stats
-	Often stays in bump or scoring zones
-	Interferes with opponent travel and accuracy
Strategic purpose
-	Slow down opponent cycles
-	Increase opponent congestion
-	Protect your alliance’s scoring lanes
________________________________________
🧠 How These Roles Interact in the Simulation
The simulation evaluates alliances of three robots, each with:
-	A role
-	A path choice
-	Collection rates
-	Travel times
-	Shooting rates
-	Accuracy
-	Capacity
-	Cycle size preference
-	Defend aggressiveness
The GA evolves combinations that maximize Teleop scoring under:
-	Congestion
-	Opponent defender interference
-	Travel penalties
-	Accuracy penalties
-	Path differences
This leads to emergent strategies like:
-	One hopper + one shooter + one feeder
-	One hopper + one hybrid + one defender
-	One wing specialist + two center robots
-	One fast shooter + two large capacity robots

