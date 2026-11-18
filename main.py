#!/usr/bin/env python3
"""Message-ordering simulator: FIFO vs causal vs total order broadcast."""
import argparse
import sys

from ordersim.protocols import PROTOCOLS
from ordersim.report import print_scenario
from ordersim.runner import run_protocol
from ordersim.scenarios import SCENARIOS, random_scenario


def main(argv=None) -> int:
    sys.setrecursionlimit(20000)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scenario", nargs="?", default="all",
                    choices=["all", *SCENARIOS], help="scenario to run (default: all)")
    ap.add_argument("-p", "--protocol", nargs="+", choices=list(PROTOCOLS),
                    default=list(PROTOCOLS), help="protocols to compare")
    ap.add_argument("-t", "--trace", action="store_true",
                    help="print the event-by-event timeline (shows hold-back queues)")
    ap.add_argument("--seed", type=int, default=1, help="random scenario seed")
    ap.add_argument("--procs", type=int, default=4, help="random scenario: processes")
    ap.add_argument("--msgs", type=int, default=2, help="random scenario: msgs per process")
    ap.add_argument("--reply-prob", type=float, default=0.2,
                    help="random scenario: probability of replying to a delivery")
    args = ap.parse_args(argv)

    names = list(SCENARIOS) if args.scenario == "all" else [args.scenario]
    for name in names:
        if name == "random":
            sc = random_scenario(args.procs, args.msgs, args.seed, args.reply_prob)
        else:
            sc = SCENARIOS[name]()
        results = [run_protocol(sc, proto) for proto in args.protocol]
        print_scenario(sc, results, trace=args.trace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
