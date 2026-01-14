## How to read the results:
To understand the results of this simulation, think of it as a "Digital Coach" that has run thousands of practice matches to find the perfect team setup. Each block of code represents one of the three robots in your alliance, and the Fitness is your total score.
Heres is an example output:
__________________________________________________
Best genome after evolution:
{'role': 3, 'path_choice': 1, 'collection_rate_center': 5.0, 'collection_rate_wing': 2.2648356619390526, 'shooting_rate': 5.0, 'travel_center_to_bump': 0.9017300268559718, 'travel_center_to_side': 0.5, 'travel_side_to_score': 0.5, 'travel_bump_to_score': 2.206616520274589, 'accuracy_open': 0.99, 'accuracy_defended': 0.7891039007424523, 'max_capacity': 70.0, 'cycle_size_preference': 0.8015966552201115, 'defend_aggressiveness': 0.21618276050206786}
{'role': 3, 'path_choice': 2, 'collection_rate_center': 2.700878345878092, 'collection_rate_wing': 5.0, 'shooting_rate': 5.0, 'travel_center_to_bump': 8.0, 'travel_center_to_side': 5.046151760964397, 'travel_side_to_score': 0.5, 'travel_bump_to_score': 2.59644345179946, 'accuracy_open': 0.99, 'accuracy_defended': 0.65626959576728, 'max_capacity': 57.93784764708916, 'cycle_size_preference': 0.88265040039687, 'defend_aggressiveness': 0.21473913342336515}
{'role': 1, 'path_choice': 2, 'collection_rate_center': 4.394846982606549, 'collection_rate_wing': 5.0, 'shooting_rate': 5.0, 'travel_center_to_bump': 5.478287687200953, 'travel_center_to_side': 3.629133483667994, 'travel_side_to_score': 0.5902062146016249, 'travel_bump_to_score': 1.5816344774107196, 'accuracy_open': 0.9877631798404283, 'accuracy_defended': 0.95, 'max_capacity': 63.99205600099536, 'cycle_size_preference': 0.9907673177527109, 'defend_aggressiveness': 0.8060155452702513}
Best fitness: 700.8
__________________________________________________
# Here is how to read and interpret the data:
1. The Goal: Fitness Score
"Best Fitness: 700.8"
This is the "High Score" for this specific alliance during a 135-second match. In this simulation, 700.8 is an exceptionally high score, indicating that the robots are working in perfect harmony without bumping into each other.
2. The Robot "DNA" (The Data Blocks)
Each robot has "genes" that determine its behavior. Let’s break down the key parts using your example data:
A. The Robot’s Job (Role)
The simulation assigns numbers to roles (0–4).
Roles 1 & 3: Your result shows two Hybrids (Role 3) and one Feeder (Role 1).
What this means: The "Coach" decided that instead of having three shooters, it is more efficient to have one robot dedicated to gathering balls (the Feeder) to keep the other two (the Hybrids) supplied.
B. The Driving Route (Path Choice)
This tells the robot which way to drive to avoid traffic jams.
Robot 1: Path 1 (Center-Side)
Robot 2 & 3: Path 2 (Wing-Side)
What this means: The simulation "realized" that if everyone drives through the middle, they slow down. It has split the team up—one robot takes the center lane, while the other two handle the side/wing lanes.
C. Performance Stats (Rates & Accuracy)
These stats describe how "good" the physical robot is:
Collection/Shooting Rate: These robots are at 5.0 (the maximum). This means they are incredibly fast at picking up and shooting balls.
Accuracy Open (0.99): When no one is guarding them, they almost never miss (99% success).
Accuracy Defended (0.65 – 0.95): This shows how much a robot "chokes" under pressure. Robot 3 is the "star" here—it maintains 95% accuracy even when being defended, making it the most reliable member of the team.
D. Capacity & Logic (Storage)
Max Capacity (57 – 70): These are "heavy-duty" robots that can hold a lot of balls at once.
Cycle Size Preference (0.80 – 0.99): This is a key behavioral trait. It means the robots are programmed to wait until they are 80% to 99% full before driving to the goal.
The Lesson: The simulation found that making fewer trips with more balls is more efficient than making many trips with only 1 or 2 balls.
Summary Checklist for Interpretation
When you look at new results, ask yourself:
Did they spread out? (Are the path_choices different or the same?)
Who is the "tank"? (Which robot has the highest accuracy_defended?)
Is the strategy "Bulk" or "Small"? (Is cycle_size_preference high or low?)
Is the score higher? (Is the Best fitness increasing compared to the last test?)
