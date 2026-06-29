# Can an AI system learn new things without forgetting the old ones?

*A plain-language look at the DARPA LYFT continual-learning research project.*

## The problem in one sentence

Most AI models are trained once and frozen. If you later teach them something
new -- a new type of threat to recognize, a new logistics rule -- they tend to
get *worse* at the things they used to know. This is called "catastrophic
forgetting," and it's a real obstacle to deploying AI in defense and logistics
settings where conditions change constantly and you can't always retrain a
model from scratch.

## What we're trying to do

This project (internally called DARPA LYFT) asks: can we build a learning
system that gets *better* at learning new things *because* of what it already
knows -- without forgetting the old things? In machine-learning terms, we want
high "forward transfer" (old knowledge helps with new tasks) and low
"forgetting" (old knowledge doesn't degrade) at the same time, and we want it
to run on small, low-power edge hardware (the kind of compute box you could
actually put on a drone or a forward operating base, not a server farm).

The design doc for this project proposes a method called **Meta-CL** -- a
combination of meta-learning (learning *how* to learn quickly) and a structural
regularizer -- and a benchmark called **LYFT-Bench** with 6 different
mission-relevant task types (threat classification, logistics routing, sensor
fusion, language understanding of orders, anomaly detection, and terrain
analysis).

## Where things actually stand today

This is the important, honest part. Right now:

- **The metrics are built.** We have working code that computes the key
  numbers researchers care about in continual learning: how much a model
  forgets old tasks ("backward transfer"), how much old knowledge helps with
  new tasks ("forward transfer"), and a few composite scores. These are tested
  and we ran them -- see `results/cl_metrics.md` for real, computed output.
- **The benchmark and the methods are not built yet.** LYFT-Bench's six real
  datasets don't exist yet, and none of the six learning methods compared in
  the design doc (plain fine-tuning, EWC, iCaRL, GEM, MAML, and our own
  Meta-CL) have been implemented or trained. The numbers in the design doc
  (e.g., "Meta-CL achieves FTR >= 0.50, 2x better than fine-tuning") are
  **targets and hypotheses**, not measured results.
- **The current code in this repo is mostly used for a different,
  related-but-distinct project** -- optimizing the physical design of a drone
  (motor count, materials, propeller size) to maximize how much cargo it can
  carry per kilogram of its own weight. That part *is* implemented, tested,
  and runnable end-to-end (`scripts/run_optimization.py`).
- We also added a small synthetic "toy" continual-learning module
  (`src/darpalyft/data.py`'s task-sequence generators) that lets us
  sanity-check the metric code using hand-built example data, before we have
  real trained models. It's useful for validating the metric math, but it's
  not a stand-in for actual experiments.

## Why this still matters

Even without a finished benchmark, the core question is a genuinely useful
one: most continual-learning research only tries to minimize forgetting. This
project's framing -- *optimize forward transfer and forgetting jointly, and
measure both under edge hardware constraints* -- is a more realistic framing for
real deployment, and the metric tooling for that framing now exists in this
repo and is unit-tested.

## What's next

The honest next steps are: (1) decide whether this repo is primarily the drone
design-optimization project or the continual-learning project, since right now
it's trying to be both; (2) implement at least one or two real CL baselines
(plain fine-tuning and EWC) on a small real dataset, replacing the synthetic
curves; and (3) only after that, start talking about Meta-CL's actual
performance rather than its target performance.

See `PAPER_DRAFT.md` for the more technical version of this status update, and
`results/cl_metrics.md` for the raw numbers we've actually computed so far.
