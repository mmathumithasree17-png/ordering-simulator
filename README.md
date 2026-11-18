# Message-Ordering Simulator

A small, dependency-free (Python 3.8+) discrete-event simulator that shows how
**FIFO**, **causal** and **total** ordering of broadcast messages are implemented,
and *verifies* each guarantee with an independent checker.

## Quick start

```bash
python main.py                      # all scenarios, all protocols, comparison tables
python main.py causal --trace       # event-by-event timeline (watch hold-back queues)
python main.py causal -p raw causal # compare only some protocols
python main.py random --seed 7 --procs 5 --msgs 3 --reply-prob 0.25
python -m unittest discover -s tests -v
```

## The three orderings

| Ordering | Guarantee | Mechanism here |
|---|---|---|
| **FIFO** | Messages from one sender are delivered in the order sent | per-sender sequence number + hold-back queue |
| **Causal** | If `a -> b` (a happened-before b), everyone delivers a before b | vector clocks (Birman-Schiper-Stephenson) + hold-back queue |
| **Total** | All processes deliver all messages in the same order | fixed sequencer stamps a global number; receivers deliver by number |

Protocols implemented (`ordersim/protocols.py`): `raw` (no ordering, baseline), `fifo`,
`causal`, `total`, and `fifo_total` (sequencer that also respects per-sender order).

Causal ⇒ FIFO (a sender's messages are causally chained), but FIFO ⇏ causal, and total
order says nothing about causality (the plain `total` protocol can break FIFO and causal
order because DATA packets race to the sequencer).

## Scenarios

* **fifo** – P0 sends x1,x2,x3 but the network delivers them reversed. `raw` fails FIFO.
* **causal** – P0 posts a photo, P1 comments on it, P2 receives the comment first.
  `raw` and `fifo` show the comment before the photo; `causal` holds the comment back
  until the photo arrives.
* **total** – two concurrent writes `x=1` / `x=2` reach replicas in different orders,
  so replicas diverge; `total` makes all replicas agree.
* **random** – random sends, random delays, probabilistic replies. Same workload for every protocol.

## Architecture

```
main.py                CLI
ordersim/core.py       Simulator (event queue), Network (non-FIFO, reliable), Message/Packet
ordersim/protocols.py  Process base + raw / fifo / causal / total / fifo_total
ordersim/checker.py    Independent checks: FIFO, causal, total, completeness
ordersim/scenarios.py  Deterministic demos + random workload
ordersim/runner.py     Runs one protocol on one scenario
ordersim/report.py     Delivery orders, PASS/FAIL table, example violations
tests/                 Checker unit tests, scenario matrix, 60-seed property test
```

Key design decisions:

* **Network** is reliable but reorders: each packet's delay comes from a scenario function, so
  packets overtake each other. Random delays are hashed from (seed, packet), so every
  protocol sees identical network behaviour per packet.
* **Delivery vs receipt**: the network *receives* packets; the protocol decides when to
  *deliver* to the application. Hold-back queues bridge the two (`--trace` shows `HOLD`).
* **Checker independence**: causality ground truth is rebuilt from each process's local
  send/deliver history (Lamport happened-before), not from the protocol's vector clocks,
  so a protocol bug would be caught. The "guarantees" column flags any broken guarantee.
* **Tests** run 60 random workloads per protocol and assert that every protocol upholds
  exactly what it promises, and that `raw` does break each property somewhere.

## Extending

* Combined causal + total order (e.g. sequencer built on causal broadcast, or ISIS/Lamport-clock agreement).
* Message loss / crashes, or a non-fixed sequencer.
* Export traces as space-time diagrams.
