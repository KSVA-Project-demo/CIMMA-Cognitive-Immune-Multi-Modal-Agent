# CIMMA-DEMO — Agents Overview

This repository contains three complementary agent subsystems developed as part of the CIMMA demo. The goal of this top-level README is to give a concise, illustrated introduction and a comparative analysis of each agent module, explain how they interact, and provide quick-start steps for exploring them locally.

Below you'll find: a short one-paragraph summary for each agent, an architectural diagram (ASCII + placeholder image references) and practical notes about running, testing and integrating the agents together.

---

## 1) safeAndVerifyAgent (Adversarial attack framework + Agent wrapper)

Purpose
- Provides a multi-modal adversarial attack framework (image, audio, text) and a simple agent wrapper that programmatically runs attacks for testing perception pipelines.

Key components
- `multiModalAdversarialAttackFramework/` — core attack library (image/audio/text attacks; uses Foolbox/ART and text attacks). The entry points include `common.py`, modality-specific scripts and a JSON-driven runner (`subprocess0319.py`) that reads `AE_thread_info.json` to launch attacks.
- `coreAgent-demo/` — lightweight agent wrapper and orchestrator:
	- `adversarial_agent.py` — AdversarialAgent class that writes the framework JSON config and launches the framework runner (supports background execution).
	- `agentWorkflow.py` — RobotAdversarialAgent: robot-facing orchestration functions (attack_image, attack_text, attack_audio) and `orchestrate_for_robot()` to coordinate attacks for tasks like sorting or navigation.
	- `agent_test.py` — small import/test harness.

Quick diagram

ASCII:

	[Robot Perception] --> [RobotAdversarialAgent] --> [AdversarialAgent wrapper] --> [multiModalAdversarialAttackFramework/src]

Placeholder image: docs/images/adversarial_flow.png (optional, create for presentations)

When to use
- Security testing, robustness evaluation, and red-team style adversarial experiments that inject perturbed inputs into vision/audio/text stacks.

Notes & caveats
- The attack framework expects model checkpoints and may require GPU. Many operations call external APIs or load model weights in `model-weights/`.
- The wrapper uses the framework's JSON invocation contract to remain non-invasive.

---

## 2) graphPruningAgent (Knowledge graph extraction & pruning)

Purpose
- Converts visual/textual scene descriptions into an initial knowledge graph, prunes it with a hybrid LLM-driven approach, visualizes the KG, and matches the pruned KG to an exam-style KB to extract core concepts.

Key components
- `workflow.py` — orchestration: summarization (via LLM), KG extraction, pruning with Gemini, analysis, SVG scene generation, and KB matching.
- `api.py` — image+text summarizer wrapper (uses Google Gemini client); returns an LLM-produced summary that is fed into KG extraction.
- `generateKG.py` — extracts entities/relations and renders graphs (NetworkX + matplotlib) and saves JSON artifacts.
- `pruningKG.py` — LLM-guided pruning helpers.
- `match_kb.py` — embedding-based KB matching and ranking (computes candidate scores combining centrality and embedding similarity).

Quick diagram

ASCII:

	[image/text/audio] --> [api.py (summarize)] --> [generateKG.extract_knowledge_graph] --> [pruningKG.prune_graph_with_gemini] --> [match_kb.match_and_rank]

Placeholder image: docs/images/graph_pipeline.png

Recent additions
- Phase‑0 audio scaffold added: `audio_api.py` provides a whisper-based (if available) fallback and `workflow.py` now optionally appends an audio transcript to the LLM prompt for multimodal context.

When to use
- Structured extraction of scene knowledge, KG-based reasoning, and curriculum/KB alignment tasks (e.g., mapping scenes to exam concepts).

Notes & caveats
- Requires valid `GOOGLE_API_KEY` for LLM/embedding calls. The repository currently uses `google.generativeai` (deprecated) — consider migrating to `google.genai`.
- The KG matching step caches embeddings in `exam_kb.json` to reduce repeated embedding costs.

---

## 3) embodiedControlAgent (Embodied control scaffold)

Purpose
- Scaffold and initial code for integrating with humanoid robot hardware or simulation. Provides HAL stubs, demo behavior scripts, and a path forward to ros2/ros2_control-based controllers and simulation.

Key components (Phase‑0 scaffold)
- `hal/joint_state_publisher.py` — ROS2-aware joint state publisher; falls back to a simulated stdout loop if ROS2 is not installed.
- `behaviors/demo_bt.py` — a minimal behavior demo (CLI or ROS2 subscriber) showing a plan→execute→done flow.
- `tests/smoke_test.py` — smoke import test to validate the scaffold.

Quick diagram

ASCII:

	[sim / robot hardware] <--> [HAL adapters] <--> [controllers / planners] <--> [behaviors]

Placeholder image: docs/images/embodied_arch.png

When to use
- Start here when you want to build robot controllers, run HIL tests, or simulate pick-and-place and navigation tasks. The scaffold intentionally avoids forcing ROS2; nodes run in fallback mode for local development.

Notes & caveats
- The workbench assumes ROS2 will be adopted for full-featured control, MoveIt2 for arm planning, and ros2_control for controllers. Those are not enforced in Phase‑0 but are recommended.

---

## How the three agents fit together

- Perception & adversarial testing: `safeAndVerifyAgent` produces adversarial examples (image/audio/text). Those inputs can be fed into the perception topics consumed by `embodiedControlAgent` (for HIL testing) and consumed by `graphPruningAgent` to see how KG extraction changes under adversarial perturbations.
- The `graphPruningAgent` provides structured evidence and core concepts which higher-level planners/behaviors in `embodiedControlAgent` can use to produce semantically-aware actions (e.g., sorting an object labeled as "flammable" vs "fragile").
- This yields a modular testbed: generate adversarial inputs, evaluate KG changes, and observe embodied behavior in simulation or hardware.

Integration diagram (ASCII):

	[AdversarialAgent] --> (adversarial inputs) --> [Perception] --> [graphPruningAgent] --> (KG evidence) --> [Behavior planner / embodiedControlAgent]

---

## Quickstart — run local smoke checks

1) Adversarial agent import/test (coreAgent-demo)

```powershell
python coreAgent-demo/agent_test.py
```

2) Graph pruning pipeline (local mode)

```powershell
# ensure GOOGLE_API_KEY set for full functionality (otherwise you'll see warnings)
python graphPruningAgent/workflow.py
```

3) Embodied scaffold smoke test

```powershell
python -m embodiedControlAgent.tests.smoke_test
# or run the example publisher (fallback non-ROS mode):
python embodiedControlAgent/hal/joint_state_publisher.py
```

---


