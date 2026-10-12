# 🤖 Unibots UK: Multi-Agent Autonomous Navigation & Strategic RL

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![PettingZoo](https://img.shields.io/badge/PettingZoo-Multi--Agent%20MARL-orange.svg)](https://pettingzoo.farama.org/)
[![Stable-Baselines3](https://img.shields.io/badge/RL-Stable--Baselines3%20PPO-green.svg)](https://stable-baselines3.readthedocs.io/)
[![Hardware-Ready](https://img.shields.io/badge/Embedded-ESP32%20C%2B%2B%20Header-red.svg)](firmware/esp32_policy_tree.hpp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Autonomous multi-agent robotics platform developed for the Unibots UK Championship.**  
> Features realistic 130-size DC motor stiction and electrical dynamics, multi-robot spatial memory, auction-based multi-agent coordination, and a champion **Macro-Strategic Reinforcement Learning (Macro-RL)** architecture that outperforms classical Artificial Potential Fields (APF) by **+10.1 points per match** in 2v2 head-to-head tournaments—complete with an ultra-low-latency C++ decision tree exported for bare-metal ESP32 microcontrollers.

---

## 📖 Table of Contents
- [Project Journey & Motivation](#-project-journey--motivation)
  - [The 2025 Campaign & Strategic Perspectives](#the-2025-campaign--strategic-perspectives)
  - [The 2026 Revival: Attacking the Problem Head-On](#the-2026-revival-attacking-the-problem-head-on)
  - [Inspiration: Lin Yi's Street Fighter AI](#inspiration-lin-yis-street-fighter-ai)
- [System Architecture & Controller Spectrum](#-system-architecture--controller-spectrum)
- [Grand 5-Way Benchmark Results](#-grand-5-way-benchmark-results)
- [The 9 Optimization Breakthroughs](#-the-9-optimization-breakthroughs)
- [Physical Hardware & Actuator Realism](#-physical-hardware--actuator-realism)
  - [Arbitrary Match Rule Assumptions (10s Penalty & 30s Deposit)](#arbitrary-match-rule-assumptions-10s-penalty--30s-deposit)
- [Embedded Firmware Deployment (ESP32)](#-embedded-firmware-deployment-esp32)
- [Repository Structure](#-repository-structure)
- [Git Guide: What to Push vs. What to Ignore](#-git-guide-what-to-push-vs-what-to-ignore)
- [Quick Start & Usage](#-quick-start--usage)
  - [Installation](#1-installation)
  - [Interactive Simulator GUI](#2-interactive-simulator-gui)
  - [Running the Grand Tournament Benchmark](#3-running-the-grand-tournament-benchmark)
  - [Training Acceleration: CPU vs. GPU (Code Toggle & Performance)](#4-training-acceleration-cpu-vs-gpu-code-toggle--performance)
  - [Retraining the Models](#5-retraining-the-models)
- [AI Assistance & Attribution Disclaimer](#-ai-assistance--attribution-disclaimer)
- [License & Acknowledgements](#-license--acknowledgements)

---

## 🧭 Project Journey & Motivation

### The 2025 Campaign & Strategic Perspectives
In the **Unibots UK 2025 Autonomous Robotics Championship**, robots compete in a dynamic arena where each bot forages for **Atoms** (steel balls) and **Compounds** (Red, Green, Blue tokens), depositing them into assigned scoring nets within a strict 180-second match duration while avoiding severe collision penalties (teleportation to base, dumping all held items, and a 10-second penalty freeze).

#### Match Format: 4-Way Free-for-All & Same-School Pairings
In the official tournament, matches are fundamentally a **4-way free-for-all** (four independent teams competing against each other simultaneously). However, in actual tournament schedules, situations often arise where two teams from the same university or club end up drawn into the exact same arena heat. In those moments, inter-robot awareness and cooperative coordination—avoiding teammate collisions and deconflicting targets—proves decisive. For benchmarking clarity, modular analysis, and simplicity, our simulation framework models both full **4-way individual free-for-alls** and **cooperative 2v2 pairings**.

#### Open-Loop Scanning vs. Adaptive Autonomous Navigation
During the 2025 tournament, a podium-finishing team demonstrated how remarkably effective a disciplined, hardcoded open-loop scanning routine can be: by executing consistent, high-speed sweeping lines across the field with minimal sensor overhead, their bot secured an impressive **3rd place finish**. It proved just how fast, reliable, and competitive open-loop execution can be when tuned well.

However, our team was personally captivated by the deeper engineering challenge of **adaptive autonomous robotics**:
- Can a robot dynamically perceive contested elements and prioritize high-value clusters?
- Can it reactively evade unpredictable multi-robot traffic and negotiate close-quarters encounters?
- Can it dynamically self-correct against wheel slip, bumper deflections, and mechanical stiction?

Our 2025 entry took the autonomous route using **Artificial Potential Fields (APF)**. However, physical reality struck hard: **severe electrical and mechanical challenges** crippled our field performance. Gearbox stiction, sensor noise, and heavy stall current spikes frequently browned out our onboard ESP32 logic rail under locked-rotor conditions. Consequently, our 2025 results fell well short of our 2024 campaign.

### The 2026 Revival: Attacking the Problem Head-On
In 2026, armed with the improved **Unibots UK 2026–2027 Rulebook**, we decided to revisit the challenge. Rather than resorting to hardcoded paths, we set out to solve autonomous navigation from first principles—analyzing the problem across both **micro** (low-level motor physics, traction, slew rate, holonomic centering) and **macro** (high-level multi-agent game strategy, triad set completion, auction coordination) levels.

### Inspiration: Lin Yi's Street Fighter AI
Our approach was heavily inspired by the pioneering work of **Lin Yi** in [LYiHub/pub-street-fighter-ai](https://github.com/LYiHub/pub-street-fighter-ai) (Street Fighter II PPO & Hierarchical RL). Lin Yi highlighted that pure end-to-end RL often collapses due to high-frequency action dithering, credit assignment over extreme time horizons, and reward sparsity. 

We adapted four core principles from Lin Yi's work into multi-agent competitive robotics:

1. **Domain-Specific Asymmetric Reward Shaping**:  
   Instead of rewarding raw forward speed or trivial proximity, we shaped utility around marginal game value: compounding **18.0× bonuses** for completing Red-Green-Blue triads, dynamic container fullness incentives, and upfront docking credits to conquer the $(0.99)^{900}$ discount horizon barrier.
2. **Behavioral Cloning (BC) Bootstrapping**:  
   Rather than letting PPO wander blindly in random exploration, we pre-trained policies on 150,000 state-action pairs collected from an expert APF baseline, warm-starting the policy network before applying RL fine-tuning.
3. **Hierarchical Decoupling (Macro Strategy vs. Micro Physics)**:  
   Lin Yi used frame-skipping and macro-actions to avoid high-frequency button thrashing. Similarly, we decoupled **strategic high-level macro planning** (target auction, Voronoi partitioning, triad denial) from **30 Hz continuous holonomic low-level execution** (APF vector fields, acceleration slew-rate limiting, ColRegs obstacle evasion).
4. **Policy Distillation for Edge Hardware**:  
   Following distillation principles, we compressed 60,000 transitions of our champion policy into an ultra-compact C++ Decision Tree running on microcontrollers in under **0.01 ms**.

---

## 🏗 System Architecture & Controller Spectrum

To evaluate how different autonomy paradigms perform under realistic match physics, we implemented and benchmarked five distinct controller architectures:

```
                                      ┌─────────────────────────────────────────────────────────┐
                                      │              UNIBOTS ARENA SIMULATION (30 Hz)           │
                                      │  - 4-Wheel Mecanum Kinematics                           │
                                      │  - 130 DC Motor Stiction & 1500 mm/s² Slew Limiting     │
                                      │  - 32-dim Sensory: 16 Radar + 10 Camera + 3 Sonar + Ego │
                                      └────────────────────────────┬────────────────────────────┘
                                                                   │
               ┌───────────────────────────┬───────────────────────┼───────────────────────────┬───────────────────────────┐
               ▼                           ▼                       ▼                           ▼                           ▼
      ┌─────────────────┐         ┌─────────────────┐     ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
      │   Classic APF   │         │     Flat RL     │     │   HRL Hybrid    │         │  Macro-RL (🏆)  │         │   Tree Policy   │
      │  (Baseline)     │         │   (End-to-End)  │     │   (Option A)    │         │   (Option B)    │         │   (Option C)    │
      ├─────────────────┤         ├─────────────────┤     ├─────────────────┤         ├─────────────────┤         ├─────────────────┤
      │ Continuous      │         │ 32-dim Obs ->   │     │ Decision Tree   │         │ Macro Planner   │         │ Distilled Tree  │
      │ Attractive &    │         │ PPO Actor MLP   │     │ Goal Selector + │         │ (Voronoi/Triad/ │         │ Fitted on 60k   │
      │ Repulsive Vector│         │ -> Direct Motor │     │ RL Agility      │         │ Auction) +      │         │ Macro-RL pairs. │
      │ Fields.         │         │ Cmds (vx,vy,w). │     │ Pilot.          │         │ 30 Hz APF Driver│         │ Pure C++ Header.│
      └─────────────────┘         └─────────────────┘     └─────────────────┘         └─────────────────┘         └─────────────────┘
```

1. **Classical APF (Baseline)**:  
   Artificial Potential Fields with attractive goal pulls and repulsive obstacle/wall barriers. Fast and reactive, but suffers from greedy foraging (prematurely docking for 1–2 balls and freezing for 30s) and zero inter-robot coordination.
2. **Flat End-to-End RL (PPO)**:  
   Standard MLP policy mapping 32-dimensional egocentric observations directly to continuous $(v_x, v_y, \omega)$. Struggled with credit assignment across 5,400 timesteps (180 seconds); high-frequency neural jitter hit motor slew limits.
3. **Hierarchical Hybrid RL (Option A)**:  
   Discrete Decision Tree strategy for macro goal switching combined with a PPO neural pilot for low-level maneuvering. Boundary thrashing between discrete goal transitions degraded overall score.
4. **Macro-Strategic RL + APF Driver (Option B — Champion 🏆)**:  
   High-level strategic intelligence (Dynamic Relative Voronoi partitioning, cooperative auction blackboard, cluster value density, full-batch banking) paired with analytical 30 Hz APF + Mecanum holonomic velocity execution.
5. **Distilled Decision Tree Regressor (Option C — Embedded Ready)**:  
   Multi-output depth-9 decision tree fitted on 60,000 state-action pairs from the Macro-RL champion. Contains zero external dependencies and exports directly to standard C++ for bare-metal ESP32 execution in $\sim 0.01\text{ ms}$.

---

## 📊 Grand 5-Way Benchmark Results

Evaluated over full 180-second matches (5,400 physics steps per match) with realistic motor deadbands, inertia lag, and collision penalties:

| Rank | Controller Architecture | Paradigm | Isolated Avg Score | Head-to-Head vs. APF | Win/Tie Rate vs. APF | Penalty Avg | Peak Single Bot | Peak Team Score |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **Macro_RL (Option B)** | **Strategic RL + APF Driver** | **36.0 pts** | **41.3 vs 31.2 (+10.1)** | **80%** | **0.60** | **76.0 pts** | **104.0 pts** |
| 🥈 | **APF (Classical)** | Potential Fields | 35.5 pts | *Baseline* | *50%* | 0.50 | 48.0 pts | 68.0 pts |
| 🥉 | **Flat_RL** | End-to-End PPO | 32.4 pts | 28.2 vs 32.0 (-3.8) | 30% | 1.00 | 41.0 pts | 56.0 pts |
| 4 | **HRL_Hybrid (Option A)** | Tree Macro + RL Pilot | 27.5 pts | 29.5 vs 37.8 (-8.3) | 20% | 0.20 | 36.0 pts | 59.0 pts |
| 5 | **Tree_Policy (Option C)** | Distilled C++ Tree | 21.0 pts | 14.0 vs 32.0 (-18.0) | 10% | 2.10 | 28.0 pts | 32.0 pts |

### Key Benchmark Takeaways
- **The +10.1 Point Margin**: Macro_RL consistently out-scores classical APF by +10.1 points per match, posting team peaks of **104 points**.
- **Zero Teammate Collisions**: In 2v2 play, simulated ESP-NOW telemetry eliminated teammate-on-teammate collisions entirely.
- **Embedded Feasibility**: The distilled Decision Tree achieves 21.0 isolated points with zero neural dependencies, making it a viable fallback for constrained MCUs.

---

## 💡 The 9 Optimization Breakthroughs

The journey from initial baseline to champion policy was paved by diagnosing and eliminating nine distinct failure modes:

```
[Phase 1: Timid Veto Failure]  ──>  [Phase 2: 30s Docking Trap]  ──>  [Phase 3: Teammate Collisions]
               │                                   │                                    │
               ▼                                   ▼                                    ▼
 Cluster Value Density Utility        Full-Batch Super-Hold Policy         ESP-NOW Wireless Safety Bubble
  (Replaced Cowardly Retreat)          (Eliminated 30-60s Waste)            (0 Teammate Ramming Events)
               │                                   │                                    │
               ├───────────────────────────────────┼────────────────────────────────────┘
               ▼
[Phase 4: Static Sector Starvation] ──> Dynamic Relative Voronoi (Soft distance-weighted territory claims)
[Phase 5: Bumper Deflection Glitch] ──> Holonomic Mecanum Cross-Track Centering (vy = clip(ly * 2.5, -300, 300))
[Phase 6: Wall Net Repulsion Fight] ──> Dynamic Net Field Masking & Perpendicular Strafe Funneling
[Phase 7: Rolling Ball Misses]      ──> Lead-Pursuit Predictive Extrapolation (x_pred = x + vx * t_intercept)
[Phase 8: False-Full Lockup Bug]    ──> Belly Emptiness Verification on Penalty / Near-Net Reset
[Phase 9: Opening Triad Starvation] ──> Central Compound Denial (1.35x bonus for central tokens in opening 35s)
```

1. **Phase 1: Addressing the "Timid Veto" Failure**  
   *Problem:* An early heuristic heavily penalized balls near opponents (10× penalty within 350mm). Robots became cowardly, retreating to empty corners while aggressive APF bots swept the arena (scores dropped to 14.7 pts).  
   *Fix:* Replaced hard opponent vetoes with a continuous **Cluster Value Density** utility:  
   $$\text{Utility} = \frac{\text{Value} + \text{Cluster Density}}{\text{Distance}^{0.88}}$$  
   *Result:* Score recovered to 38.0+ pts; decisive snatching replaced timid retreats.

2. **Phase 2: Shattering the 30-Second Deposit Freeze Trap**  
   *Problem:* A deposit takes 30.0 seconds (16.7% of match time). Early policies docked whenever holding $\ge 2$ items. Two docking cycles consumed 60 seconds (33% of the match) for a trivial atom gain (+1 pt/atom), while unbanked compounds in the belly cavity already count for their full 4 points and triad bonuses at match end!  
   *Fix:* Implemented a **Full-Batch Super-Hold** policy: robots forage until holding $\ge 5$ items (capacity 6), or until match time reaches $t \ge 105\text{s}$ with $\ge 4$ items, or a buzzer rush at $t \ge 135\text{s}$ with $\ge 1$ item.  
   *Result:* Saved 30–40 seconds of active sweeping time per robot per match, yielding 2–3 additional compounds (8–16 points).

3. **Phase 3: Eliminating Teammate Collisions via ESP-NOW Safety Bubble**  
   *Problem:* Telemetry revealed that in 2v2 matches, multiple collision penalties were caused by teammates converging on the same central clusters and ramming each other.  
   *Fix:* Simulated wireless inter-robot telemetry (modeling **ESP-NOW** radio on ESP32, $<1\text{ ms}$ latency). Broadcasted live coordinates with mutual repulsion at 650mm and active reverse braking ($v_{\text{cmd}} < 0$) when closing within 420mm.  
   *Result:* Teammate collisions dropped to **exactly 0** across all seeds.

4. **Phase 4: True Dynamic Relative Voronoi vs. Static Quadrant Starvation**  
   *Problem:* Static quadrant splits (Robot 0 covering North/East, Robot 1 covering South/West) starved robots when random game element spawns clustered in the opposite half of the arena.  
   *Fix:* Replaced fixed coordinates with **Dynamic Relative Voronoi** partitioning based on live teammate proximity: if $d_{\text{teammate}} < 0.75 \times d_{\text{self}}$, yield with a $0.35\times$ factor; if $d_{\text{self}} < 0.85 \times d_{\text{teammate}}$, claim aggressively with a $1.35\times$ bonus.  
   *Result:* Teammates dynamically fan out across any random distribution with zero coordination deadlocks.

5. **Phase 5: Holonomic Mecanum Cross-Track Intake Centering**  
   *Problem:* Approaching balls at 500 mm/s with 120ms motor inertia lag caused minor 5–10° heading errors, resulting in balls striking the outer 25mm bumper wall and deflecting away at 300+ mm/s.  
   *Fix:* Exploited 4-wheel Mecanum holonomic drive: when within 400mm of a target ball, applied lateral strafe centering:  
   $$v_y = \text{clip}(l_y \times 2.5, -300, 300)$$  
   pulling the 150mm mouth directly over the ball midline.  
   *Result:* Intake capture success jumped from $\sim 70\%$ to **$>95\%$** on first-pass approaches.

6. **Phase 6: Wall Net Repulsion Masking & Square Dock Funneling**  
   *Problem:* APF repulsive wall fields fought the robot as it approached the scoring net, causing deceleration and hesitations right at the dock threshold.  
   *Fix:* Dynamically masked normal wall repulsion along the assigned net opening when docking. Added perpendicular heading pre-alignment ($\theta \to \pm\pi/2$ or $0/\pi$) and lateral strafe funneling toward the 1,250mm net centerline.  
   *Result:* Instant first-touch deposit triggers on arrival; transit and banking delay reduced by 2–4 seconds per cycle.

7. **Phase 7: Lead-Pursuit Predictive Ball Interception**  
   *Problem:* Navigating toward static memory coordinates caused missed intakes on rolling or bouncing balls (20–150 mm/s).  
   *Fix:* Added finite-difference velocity tracking in spatial memory $(v_{x,\text{ball}}, v_{y,\text{ball}})$ and linear trajectory extrapolation:  
   $$x_{\text{intercept}} = x_{\text{ball}} + v_{x,\text{ball}} \cdot t_{\text{intercept}}, \quad t_{\text{intercept}} = \min(1.2, d / 420)$$  
   *Result:* Bouncing elements caught on the first pass; single-robot peak score surged to **76.0 points**.

8. **Phase 8: Resolving Container False-Full Lockup Bug**  
   *Problem:* In Seed 3, Robot 0 scored 0 points because an early collision penalty dumped its held balls, but `postulated_held` retained a stale count of 5. The robot drove to the net with an empty container where the deposit timer never triggered (`held == 0`), preventing `postulated_held` from resetting and trapping Robot 0 in an infinite dock loop.  
   *Fix:* Added physical belly emptiness verification: `postulated_held` resets to 0 whenever penalized or when within 300mm of the net with `total_held_elements == 0`.  
   *Result:* 100% elimination of dock lockups; Seed 3 score jumped to 80 team points (40, 40).

9. **Phase 9: Dynamic Opponent Neutralization (Opening 35 Seconds)**  
   *Problem:* In seeds where APF scored well, APF completed early triads in the uncontested center and their own half.  
   *Fix:* Added an opening 35-second contested compound denial ($1.35\times$ bonus for compounds in the central neutral zone), vacuuming key colors before APF could reach them.  
   *Result:* Suppressed opponent APF scores (dropping them to 0 in Seed 1); secured the **104-point team peak** and solidified our **+10.1 pt tournament margin**.

---

## ⚙ Physical Hardware & Actuator Realism

A major flaw of many RL robotics simulators is operating under idealized physics, resulting in the notorious **sim-to-real gap**. Our simulation explicitly models physical constraints derived from our 2025 hardware post-mortem:

- **Chassis & Drive**: 4-wheel Mecanum holonomic drive ($200 \times 200\text{ mm}$ footprint, 150mm intake mouth, C-shaped belly cavity holding up to 6 elements).
- **130-Size Toy DC Motors**: ~1:48 gearbox reduction, 3V–6V operating range, 70–250 mA no-load current.
- **ESP32 Brownout Prevention via Slew-Rate Limiting**: Clamped maximum linear acceleration to $1,500\text{ mm/s}^2$ and angular acceleration to $9.42\text{ rad/s}^2$. This eliminates high-current $1.5\text{ A}$ stall spikes that would otherwise collapse the onboard ESP32 3.3V logic regulator.
- **Actuator Deadband & Stiction**: Simulated a $30\text{ mm/s}$ velocity deadband and $0.2\text{ rad/s}$ angular deadband to replicate gearbox stiction and motor back-EMF thresholds.
- **Mechanical Inertia Lag**: $120\text{ ms}$ exponential first-order response lag between commanded velocity and physical wheel acceleration.

### Arbitrary Match Rule Assumptions (10s Penalty & 30s Deposit)
In [`simulation/core.py`](file:///c:/Users/user/Documents/Arduino/UnibotsUK_25_Codebase/simulation/core.py#L28-L29), two timing parameters dictate match pacing:

```python
# Penalty & Deposit durations in simulation/core.py
PENALTY_FREEZE_SECONDS = 10.0
DEPOSIT_DURATION_SECONDS = 30.0 # Docking & depositing takes 30s
```

> [!NOTE]
> **Context on these arbitrary parameters:**
> 1. **10.0-Second Penalty Freeze**: This value was modeled after what competition organizers and marshals enforced on site during the live event for infractions, collisions, or robot interventions.
> 2. **30.0-Second Deposit Duration**: This was an assumed arbitrary duration chosen to reflect the physical time an electromechanical mechanism (servo-actuated gate, ramp tilt, or continuous reverse-belt conveyor) would realistically take to discharge captured elements into the scoring net.
> 
> Both values are fully configurable in `core.py` if your team's physical ejector operates faster or competition rule updates modify penalty freeze durations.

---

## 🔌 Embedded Firmware Deployment (ESP32)

To deploy our autonomous policy directly onto the physical robot, we distilled the Macro-RL champion into a pure C++ decision tree header:

📁 **[`firmware/esp32_policy_tree.hpp`](file:///c:/Users/user/Documents/Arduino/UnibotsUK_25_Codebase/firmware/esp32_policy_tree.hpp)**

### Microcontroller Execution Specs
- **Inference Latency**: $\sim 0.01\text{ ms}$ on an ESP32 @ 240 MHz.
- **Memory Footprint**: $< 5\text{ KB}$ RAM, zero dynamic allocations (`malloc`/`new`).
- **Dependencies**: Pure standard C++ (`<stdint.h>`), no PyTorch, no TensorFlow Lite, no matrix math libraries.
- **Signature**:
  ```cpp
  #include "esp32_policy_tree.hpp"

  // Evaluates 32-dim sensory observation and outputs normalized actions:
  // obs[32]   : [3 sonar, 10 camera rays, 16 radar sectors, 2 net vec, 1 timer]
  // action[3] : [normalized vx, vy, omega] in range [-1.0, 1.0]
  float obs[32];
  float action[3];

  evaluate_policy_tree(obs, action);

  float vx_cmd    = action[0] * 500.0f;  // mm/s
  float vy_cmd    = action[1] * 300.0f;  // mm/s
  float omega_cmd = action[2] * 3.14159f; // rad/s
  ```

---

## 📁 Repository Structure

```
UnibotsUK_25_Codebase/
├── README.md                              # This manifesto & documentation
├── .gitignore                             # Clean repository exclusion rules
├── requirements.txt                       # Reproducible Python dependencies
├── TRAINING_AND_OPTIMIZATION_SUMMARY.json # Full benchmark & chronology manifesto
├── AI Algorithms in Robotic Navigation.pdf# Research paper reference
├── Unibots Rulebook 2026-2027 v1.0-1.pdf  # Official Unibots UK rulebook
├── Unibots26-AprilTags-0-23.pdf           # AprilTag vision fiducial sheets
│
├── firmware/                              # Embedded Microcontroller Firmware
│   └── esp32_policy_tree.hpp              # Distilled C++ policy header for ESP32
│
├── models/                                # Trained Policies & Artifacts
│   ├── decision_tree_policy.pkl           # Distilled Python Decision Tree model
│   ├── learning_curve_dashboard.html      # Interactive training dashboard
│   ├── training_log.csv                   # Timestep, reward, and KL metric logs
│   ├── unibots_bc_ppo.zip                 # PPO policy fine-tuned from BC warm-start
│   ├── unibots_bc_pretrained.zip          # Pure Behavioral Cloning actor model
│   ├── unibots_ppo_v1.zip                 # Flat end-to-end PPO neural network
│   └── checkpoints/                       # Intermediate training step snapshots
│
└── simulation/                            # Simulation & RL Training Pipeline
    ├── core.py                            # Arena physics, Mecanum kinematics, scoring
    ├── sensors.py                         # 32-dim sensor suite & spatial memory
    ├── env.py                             # PettingZoo Parallel multi-agent gym env
    ├── controllers.py                     # All 5 controllers (APF, Flat, HRL, Macro, Tree)
    ├── planner.py                         # APF vector field navigation planner
    ├── render.py                          # Pygame 60 FPS real-time arena visualizer
    ├── play.py                            # Interactive GUI simulator with 7 match modes
    ├── benchmark_all.py                   # Grand 5-way tournament benchmarking suite
    ├── compare_controllers.py             # Head-to-head match runner
    ├── train.py                           # Clean PPO training runner with CSV logger
    ├── train_bc_rl.py                     # 2-Phase pipeline: BC Warm-Start + PPO Fine-Tune
    ├── train_tree_policy.py               # Macro-RL sampler & C++ tree header generator
    ├── inspect_metrics.py                 # Telemetry & penalty distribution inspector
    ├── evaluate_checkpoints.py            # Checkpoint performance scanner
    └── plot_learning_curve.py             # Learning curve generator
```

---

## 📦 Git Guide: What to Push vs. What to Ignore

When preparing to publish this repository to GitHub, follow these best practices for tracking and ignoring files:

### ✅ Documents to Track & Push
1. **Source Code**:
   - `simulation/*.py`: The complete multi-agent physics, sensor, environment, controller, and training pipeline.
   - `firmware/esp32_policy_tree.hpp`: The embedded C++ header for ESP32.
2. **Key Model Weights & Dashboards**:
   - `models/*.zip` (`unibots_bc_ppo.zip`, `unibots_bc_pretrained.zip`, `unibots_ppo_v1.zip`): Consolidated neural weights (<200 KB each).
   - `models/decision_tree_policy.pkl`: Python decision tree artifact (34 KB).
   - `models/learning_curve_dashboard.html` & `models/training_log.csv`: Visual dashboard and metric logs.
3. **Documentation & Manifestos**:
   - `README.md`: Project documentation.
   - `requirements.txt`: Python package dependencies.
   - `TRAINING_AND_OPTIMIZATION_SUMMARY.json`: Detailed 250-line experiment data and optimization chronology.
   - `AI Algorithms in Robotic Navigation.pdf`, `Unibots Rulebook 2026-2027 v1.0-1.pdf`, `Unibots26-AprilTags-0-23.pdf`: Reference PDFs.

### 🚫 Documents to Ignore (`.gitignore`)
The provided [`.gitignore`](file:///.gitignore) automatically filters out:
- **Virtual Environments (`.venv/`, `venv/`)**: Never push local virtual environments containing gigabytes of compiled binaries.
- **Python Bytecode (`__pycache__/`, `*.pyc`)**: Machine-specific compiled bytecode.
- **Intermediate RL Checkpoints (`models/checkpoints/`)**: Redundant step-by-step model backups (e.g., `*_2000000_steps.zip`). Keep only the final models in `models/`.
- **Operating System & Editor Files**: `.DS_Store`, `Thumbs.db`, `.vscode/`, `.idea/`.

---

## 🚀 Quick Start & Usage

### 1. Installation
Clone the repository and install the dependencies in a Python 3.11+ environment:

```bash
git clone https://github.com/Mengcer/Unibots_UK25.git
cd Unibots_UK25

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Interactive Simulator GUI
Launch the real-time Pygame simulator:

```bash
python -m simulation.play
```

- **Press `M`**: Cycle through **7 competitive matchup modes**:
  - `2v2: Macro-RL (Yellow/Orange) vs. APF (Purple/Green)`
  - `2v2: APF vs. Flat RL`
  - `2v2: HRL Hybrid vs. Tree Policy`
  - `All 4: Macro-RL Champions`
  - `All 4: Classical APF`
  - `All 4: Distilled Decision Tree`
  - `All 4: Flat RL Neural Policy`
- **Press `R`**: Re-scatter elements and reset match.

### 3. Running the Grand Tournament Benchmark
Run the comprehensive 5-way benchmark comparing all controllers:

```bash
python -m simulation.benchmark_all
```

### 4. Training Acceleration: CPU vs. GPU (Code Toggle & Performance)

#### Which Files & Lines to Change
Hardware acceleration is toggled directly in the training scripts:

1. **[`simulation/train.py`](file:///c:/Users/user/Documents/Arduino/UnibotsUK_25_Codebase/simulation/train.py#L50)** (Line 50):
   ```python
   # Default: auto-detects CUDA
   device = "cuda" if torch.cuda.is_available() else "cpu"

   # To force CPU (Fastest FPS):
   device = "cpu"

   # To force GPU (Offloads CPU cores):
   device = "cuda"
   ```

2. **[`simulation/train_bc_rl.py`](file:///c:/Users/user/Documents/Arduino/UnibotsUK_25_Codebase/simulation/train_bc_rl.py#L77-L162)** (Line 77 in `pretrain_behavior_cloning` and Line 160 in `main`):
   ```python
   # Line 77:
   device = "cpu"  # or "cuda"

   # Line 160:
   device = "cpu"  # or "cuda"
   ```

#### ⚡ Performance Difference: Why CPU is Often Faster
In deep reinforcement learning with robotics simulators, hardware performance can be counter-intuitive:
- **Small Neural Network Footprint**: The PPO actor-critic network is a lightweight MLP ($32 \to 64 \to 64 \to 3$). The computational cost of the forward pass is minimal ($\ll 1\text{ ms}$).
- **PCIe Bus Bottleneck**: The custom 30 Hz multi-agent arena physics, ball bouncing, raycasts, and spatial memory updates run in Python on the host CPU. Moving small 32-dimensional tensors back and forth across the PCIe bus between system RAM and GPU VRAM introduces data-transfer latency and CUDA synchronization overhead.
- **Result**: In raw frames-per-second (FPS), **running purely on CPU is actually faster** than GPU for this specific environment!
- **Why GPU was Used**: GPU (`cuda`) was explicitly selected during our training runs because the host system needed to execute other CPU-intensive multitasking workloads simultaneously. Offloading tensor batches to the GPU allowed training to proceed smoothly in the background without starving or throttling host CPU cores.

---

### 5. Retraining the Models
- **Train Behavior Cloning + PPO**:
  ```bash
  python -m simulation.train_bc_rl
  ```
- **Distill Macro-RL into C++ ESP32 Header**:
  ```bash
  python -m simulation.train_tree_policy
  ```
- **Inspect Telemetry & Penalties**:
  ```bash
  python -m simulation.inspect_metrics
  ```

---

## 🤖 AI Assistance & Attribution Disclaimer

In the spirit of open scientific disclosure:
- **2025 Original Foundation**: The initial 2025 baseline code and preliminary navigation concepts were developed with the assistance of **Gemini 2.0 Pro**.
- **2026 Multi-Agent RL & Strategic Architecture**: The 2026 revival, including the PettingZoo environment, realistic 130-motor stiction physics, the 9 optimization breakthroughs, tournament benchmarking, Lin Yi Street Fighter AI adaptations, and ESP32 C++ decision tree distillation, was designed and implemented with the assistance of **Gemini 3.1 Pro**.

---

## 📄 License & Acknowledgements

- **License**: MIT License. See [LICENSE](LICENSE) for details.
- **Inspiration**: Special thanks to **Lin Yi** for open-sourcing [LYiHub/pub-street-fighter-ai](https://github.com/LYiHub/pub-street-fighter-ai), demonstrating practical reinforcement learning, reward shaping, and hierarchical distillation.
- **Competition**: [Unibots UK](https://unibots.uk/) for organizing the university autonomous robotics competition.
