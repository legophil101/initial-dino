# 🦖 Initial Dino — Real-Time Chrome Dino Automation Engine

> “At first, I thought this project would just be:
> see obstacle → make dino jump.
>
> Turns out real-time systems are a little more complicated than that.”

A Python-based real-time Chrome Dino automation bot built using computer vision, pixel scanning, heuristic detection systems, and a hybrid FSM/reactive architecture.

This project evolved through multiple experimental “Stages,” inspired by iterative optimization, latency tuning, and real-time decision system design under increasing game speed constraints.

---

# 🏁 Project Overview

Initial Dino is an experimental real-time automation system that plays the Chrome Dino game using:

* screen capture
* pixel-based obstacle detection
* heuristic scanning
* finite state machine (FSM) logic
* low-latency input automation

The project was intentionally built without:

* game memory access
* cheats
* machine learning models

Instead, the goal was to explore:

* real-time computer vision fundamentals
* reactive system design
* latency-sensitive architecture
* engineering tradeoffs between “smart” systems vs stable systems

---

# 🧠 Core Concepts Explored

* Real-time computer vision
* FSM architecture
* Heuristic-based detection systems
* Latency optimization
* Reactive automation
* Timing synchronization
* Constraint-driven engineering
* Stability vs complexity tradeoffs

---

# 🏗️ System Architecture

The final version uses a hybrid layered architecture:

## 1. Vision Layer

* Screen capture using `mss`
* Region-based scanning for low-latency processing
* Dynamic forward scan positioning based on game speed

---

## 2. Detection Layer

* Pixel-based scanning using `Pillow`
* Grayscale conversion
* Threshold-based obstacle detection
* Lightweight heuristic classification system

No machine learning models were used.

---

## 3. Decision Layer

Hybrid system combining:

* reactive “tier-style” reflex logic
* finite state machine architecture

FSM States:

* `GROUND`
* `JUMP`
* `AIR`

Additional systems:

* chain jump handling
* fast-fall optimization
* decision locking
* rebound jump queueing

---

## 4. Input Layer

* Keyboard automation via `pyautogui`
* Controlled jump timing
* Duck hold system
* State-synchronized input release

---

# ⚡ Key Features

## ✔ Real-time obstacle detection

Detects incoming obstacles through pixel intensity analysis.

---

## ✔ Hybrid FSM + Reactive Architecture

The final system combines:

* the speed of the earlier “reflex/tier” system
* the stability of FSM-based logic

This hybrid approach became the most stable architecture during testing.

---

## ✔ Dynamic speed scaling

The bot adapts scan distance and timing behavior as game speed increases.

Modes:

* Early A
* Early B
* Mid Game

Each mode uses different:

* scan widths
* timing windows
* reaction thresholds

---

## ✔ Chain-aware jump system

Handles consecutive obstacle sequences using rebound jump logic and queued follow-up jumps.

---

## ✔ Fast-fall optimization

Uses controlled ducking during airtime to reduce recovery time between jumps.

---

## ✔ Simplified “Jump Over Everything” Strategy

Late-stage versions attempted bird classification and advanced threat differentiation.

However, the final stable version intentionally simplified the system:

> treat all major threats as jumpable obstacles

This reduced race conditions and improved overall consistency.

---

# 🏆 Performance

## Best Recorded Score

**24,781**

---

## Typical Stable Range

* 3K–6K consistently
* occasional high-score runs depending on:

  * obstacle spacing
  * frame timing
  * latency consistency

---

# 🚗 Technical Evolution — The Stages

---

# Stage 1 — Reflex Era

Initial approach:

* simple reactive jumping
* tier-based logic
* no FSM architecture
* heavy reliance on direct reactions

At this stage:

* code became increasingly spaghetti-like
* logic worked surprisingly well early on
* but stability became difficult to maintain at higher speeds

Originally used:

* `pyautogui` screen capture

Performance:
~2K–4K average range

---

# Stage 2 — FSM Era

As the project evolved, a major problem started appearing:

## Input Race Conditions

The original reflex/tier system worked surprisingly well early on, but new mechanics introduced increasing instability:

* ducking logic
* fast-fall optimization
* bird handling
* chained obstacle reactions

The biggest issue:

> multiple systems could attempt conflicting actions at the same time.

Examples:

* duck while preparing a jump
* fast-fall triggering during rebound timing
* bird detection interfering with cactus jump logic
* input release timing becoming inconsistent

At higher speeds, these conflicts became increasingly difficult to manage using pure reactive logic.

---

To solve this, the project transitioned into a more structured architecture:

## FSM Introduction

The system introduced a Finite State Machine (FSM) with explicit movement states:

* `GROUND`
* `JUMP`
* `AIR`

This allowed the bot to:

* synchronize movement behavior
* reduce contradictory inputs
* stabilize jump timing
* control duck release timing
* coordinate fast-fall behavior more safely

The FSM significantly improved:

* consistency
* predictability
* architectural organization

However, a new issue appeared:

> the system became “too smart.”

The additional structure and checks introduced slight overhead during early-game sections where pure reflexive reactions were actually more effective.

This led to one of the project's biggest realizations:

> in real-time systems, stability and speed constantly compete with each other.

The eventual solution would become a hybrid architecture combining:

* Stage 1 reflex speed
* Stage 2 FSM stability

---

# Stage 3 — Hybrid Evolution

This became the final successful architecture.

The project combined:

* Stage 1 reactive/tier behavior
* Stage 2 FSM stability
* MSS low-latency screen capture

Result:
a hybrid system balancing:

* reflex speed
* architectural stability
* lower latency

This stage produced the highest-performing runs.

---

# Stage 4 — Optimization & Tuning

Focused heavily on:

* scan tuning
* timing windows
* chain jump handling
* fast-fall behavior
* dynamic offsets
* frame timing synchronization

This stage achieved the project’s best score:

## 24,781

---

# Stage 5 — Experimental Vision Systems (Rolled Back)

Several advanced systems were attempted:

## Experimental Features

* NumPy-based scanner
* Vision preprocessing pipeline
* Horizontal slice ground scanner
* Alternative classification systems

Goals:

* faster detection
* cleaner architecture
* improved prediction stability

However, real-world testing revealed:

* increased latency
* detection instability
* invisible obstacle failures
* debugging complexity

Ironically:
the “more advanced” systems often performed worse than the simpler heuristic pipeline.

These systems were ultimately removed from the final version.

One of the biggest lessons from the project:

> simpler systems can outperform theoretically “better” systems under tight real-time constraints.

---

# ⚠️ Development Constraints

This project was developed under several practical limitations:

* Single-monitor setup
* Broken laptop display
* External monitor-only workflow
* Real-time debugging limitations
* Timing-sensitive testing environment

Debugging advanced vision systems became particularly difficult because:

* failures occurred extremely quickly
* visual debugging tools were limited
* latency changes were difficult to isolate in real time

---

# 🖥️ Environment Notes

Final tested setup:

* 1080p monitor
* Windows scaling at 120%
* External monitor setup

The bot may require adjustment of:

* scan positions
* offsets
* thresholds
* pixel coordinates

depending on monitor resolution and scaling settings.

---

# ▶️ How To Run

## 1. Install dependencies

Install:

* `pyautogui`
* `pillow`
* `mss`

---

## 2. Open Chrome Dino

Launch the Chrome Dino game in browser.

Tested primarily using:

https://elgoog.im/dinosaur-game/

You can also:

* disconnect internet and open Chrome
* or use an online Dino clone

---

## 3. Adjust monitor configuration variables if needed

Depending on your setup, you may need to modify:

* scan coordinates
* base positions
* offsets
* pixel locations

Especially if:

* using different monitor resolutions
* using different Windows scaling settings

---

## 4. Run the script

After starting the script:

* quickly switch to the Chrome Dino window
* the bot includes a short startup delay for focus switching

---

# 🧩 Tech Stack

* Python
* PyAutoGUI
* Pillow (PIL)
* MSS
* time/perf_counter timing system

---

# 🧠 Key Learnings

This project taught me:

* Real-time systems are heavily constraint-driven
* Lower latency often beats “smarter” logic
* Simpler heuristics can outperform complex pipelines
* FSM architecture improves stability but may introduce overhead
* Optimization is often about removing complexity, not adding it
* Debugging time-sensitive systems is fundamentally different from debugging traditional applications

Most importantly:

> engineering is iterative.
> A failed experiment is still useful if it reveals system limitations.

---

# 🚧 Future Improvements

Potential future directions:

* Revisit NumPy vectorized scanning with better tooling
* Multi-frame obstacle tracking
* Temporal smoothing
* Modular architecture split into separate engine components
* Reinforcement learning version
* Visualization/debug overlay system
* Multi-monitor debugging workflow

---

# 🏁 Final Thoughts

This project started as:

> “make dino jump over obstacle”

It eventually evolved into an exploration of:

* latency
* architecture
* state systems
* real-time engineering tradeoffs

Initial Dino became less about “beating the game”
and more about understanding why real-time systems behave the way they do.

---

# 📌 Author Note

Built as part of a self-directed Python and systems programming learning journey focused on:

* real-time automation
* computer vision
* reactive architectures
* performance-oriented engineering
