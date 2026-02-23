import yappi
import os
import pstats
import io

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
OUTPUT_PROF = "profile.prof"
OUTPUT_PROF_FILTERED = "profile_filtered.prof"
OUTPUT_FLAME = "flamegraph.folded"
# ─────────────────────────────────────────────────────────────────────────────


def is_project_func(func_stat):
    """Return True only for functions living inside ./src/"""
    mod = func_stat.module or ""
    norm = os.path.normpath(os.path.abspath(mod))
    if not norm.startswith(PROJECT_ROOT):
        return False
    bad = (".venv", "site-packages", "dist-packages", "lib/python")
    return not any(b in norm for b in bad)


def is_project_key(key):
    file = os.path.normpath(os.path.abspath(key[0]))
    if not file.startswith(PROJECT_ROOT):
        return False
    bad = (".venv", "site-packages", "dist-packages")
    return not any(b in file for b in bad)


# ── Run ───────────────────────────────────────────────────────────────────────
from src.main import main  # import AFTER defining helpers so path is clean

yappi.set_clock_type("cpu")
yappi.start()
main()
yappi.stop()


# ── Filtered stats ────────────────────────────────────────────────────────────
stats = yappi.get_func_stats(filter_callback=is_project_func)
stats.sort("ttot", "desc")

# Pretty-print top 30
print(f"\n{'Module':<60} {'Function':<30} {'Calls':>7} {'TTotal':>10} {'TSelf':>10}")
print("─" * 120)
for f in stats.get()[:30]:
    mod = os.path.relpath(f.module, os.path.dirname(PROJECT_ROOT)) if f.module else "?"
    print(f"{mod:<60} {f.name:<30} {f.ncall:>7} {f.ttot:>10.4f}s {f.tsub:>10.4f}s")

# Save raw pstats first (needed as input for filtering steps below)
stats.save(OUTPUT_PROF, type="pstat")
print(f"\n✓ pstats saved → {OUTPUT_PROF}")


# ── Flamegraph (folded stacks format) ────────────────────────────────────────
def pstats_to_folded(prof_path: str, out_path: str):
    ps = pstats.Stats(prof_path, stream=io.StringIO())
    ps.calc_callees()

    raw = ps.stats  # {(file, line, name): (cc, nc, tt, ct, callers)}

    folded: dict[str, float] = {}

    def label(key):
        file, line, name = key
        file = os.path.basename(file)
        return f"{file}:{line}({name})"

    for callee_key, (cc, nc, tt, ct, callers) in raw.items():
        if not is_project_key(callee_key):
            continue
        if not callers:
            stack = label(callee_key)
            folded[stack] = folded.get(stack, 0) + tt
        else:
            for caller_key in callers:
                if not is_project_key(caller_key):
                    stack = label(callee_key)
                else:
                    stack = f"{label(caller_key)};{label(callee_key)}"
                folded[stack] = folded.get(stack, 0) + tt

    with open(out_path, "w") as fh:
        for stack, t in sorted(folded.items(), key=lambda x: -x[1]):
            fh.write(f"{stack} {max(1, int(t * 10000))}\n")

    print(f"✓ folded stacks saved → {out_path}")


pstats_to_folded(OUTPUT_PROF, OUTPUT_FLAME)


# ── Filtered SnakeViz prof ────────────────────────────────────────────────────
def save_filtered_prof(input_path: str, output_path: str):
    ps = pstats.Stats(input_path, stream=io.StringIO())
    raw = ps.stats  # {(file, line, name): (cc, nc, tt, ct, callers)}

    # Keep only project keys, strip non-project callers too
    filtered = {}
    for callee_key, (cc, nc, tt, ct, callers) in raw.items():
        if not is_project_key(callee_key):
            continue
        filtered_callers = {k: v for k, v in callers.items() if is_project_key(k)}
        filtered[callee_key] = (cc, nc, tt, ct, filtered_callers)

    ps2 = pstats.Stats(input_path, stream=io.StringIO())
    ps2.stats = filtered
    ps2.dump_stats(output_path)
    print(f"✓ filtered pstats saved → {output_path}")


save_filtered_prof(OUTPUT_PROF, OUTPUT_PROF_FILTERED)
