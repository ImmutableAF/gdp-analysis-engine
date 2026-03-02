# profiler.py
import os
import io
import time
import threading
import pstats
import yappi
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
OUTPUT_PROF = ".dev/profile/profile.prof"
OUTPUT_PROF_FILTERED = ".dev/profile/profile_filtered.prof"
OUTPUT_FLAME = ".dev/flamegraph/flamegraph.folded"
# ──────────────────────────────────────────────────────

from src.main import main  # import your app AFTER setting paths


# ── HELPERS ────────────────────────────────────────────
def is_project_func(func_stat):
    """Keep only functions defined in ./src/"""
    if not func_stat.module:
        return False
    norm = os.path.normpath(os.path.abspath(func_stat.module))
    return norm.startswith(PROJECT_ROOT)


def is_project_key(key):
    """Keep only (file,line,name) entries inside ./src/"""
    file = os.path.normpath(os.path.abspath(key[0]))
    return file.startswith(PROJECT_ROOT)


# ── RUN MAIN IN THREAD ─────────────────────────────────
def run_main():
    """Run main() in a separate thread if it spawns daemons"""
    t = threading.Thread(target=main, daemon=False)
    t.start()
    return t


# ── PROFILING ─────────────────────────────────────────
yappi.set_clock_type("cpu")
yappi.start()

# Run your main() and let it do some work
main_thread = run_main()

# Wait a bit to let daemon threads inside main() execute
time.sleep(5)  # adjust higher if your APIs take longer to spin up

# Stop profiling
yappi.stop()

# ── EXTRACT STATS ─────────────────────────────────────
stats = yappi.get_func_stats(filter_callback=is_project_func)
stats.sort("ttot", "desc")

print(f"\n{'Module':<60} {'Function':<30} {'Calls':>7} {'TTotal':>10} {'TSelf':>10}")
print("─" * 120)
for f in stats.get()[:30]:
    mod = os.path.relpath(f.module or "?", os.path.dirname(PROJECT_ROOT))
    print(f"{mod:<60} {f.name:<30} {f.ncall:>7} {f.ttot:>10.4f}s {f.tsub:>10.4f}s")

# ── SAVE RAW STATS ────────────────────────────────────
stats.save(OUTPUT_PROF, type="pstat")
print(f"✓ Saved raw pstats → {OUTPUT_PROF}")


# ── GENERATE FOLDED FLAMEGRAPH ───────────────────────
def pstats_to_folded(prof_path: str, out_path: str):
    ps = pstats.Stats(prof_path, stream=io.StringIO())
    ps.calc_callees()
    raw = ps.stats  # {(file, line, name): (cc, nc, tt, ct, callers)}

    folded = {}

    def label(key):
        file, line, name = key
        file = os.path.basename(file)
        return f"{file}:{line}({name})"

    for callee_key, (cc, nc, tt, ct, callers) in raw.items():
        if not is_project_key(callee_key):
            continue
        if not callers:
            folded[label(callee_key)] = folded.get(label(callee_key), 0) + tt
        else:
            for caller_key in callers:
                stack = (
                    f"{label(caller_key)};{label(callee_key)}"
                    if is_project_key(caller_key)
                    else label(callee_key)
                )
                folded[stack] = folded.get(stack, 0) + tt

    with open(out_path, "w") as fh:
        for stack, t in sorted(folded.items(), key=lambda x: -x[1]):
            fh.write(f"{stack} {max(1,int(t*10000))}\n")

    print(f"✓ Saved folded stacks → {out_path}")


pstats_to_folded(OUTPUT_PROF, OUTPUT_FLAME)


# ── SAVE FILTERED PS STATS ───────────────────────────
def save_filtered_prof(input_path: str, output_path: str):
    ps = pstats.Stats(input_path, stream=io.StringIO())
    raw = ps.stats

    filtered = {}
    for callee_key, (cc, nc, tt, ct, callers) in raw.items():
        if not is_project_key(callee_key):
            continue
        filtered_callers = {k: v for k, v in callers.items() if is_project_key(k)}
        filtered[callee_key] = (cc, nc, tt, ct, filtered_callers)

    ps2 = pstats.Stats(input_path, stream=io.StringIO())
    ps2.stats = filtered
    ps2.dump_stats(output_path)
    print(f"✓ Saved filtered pstats → {output_path}")


save_filtered_prof(OUTPUT_PROF, OUTPUT_PROF_FILTERED)

# ── DONE ─────────────────────────────────────────────
print("\nProfiling complete!")
