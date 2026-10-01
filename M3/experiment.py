import time
import csv
import tracemalloc
from engine_stub import SokobanProblem
from search_stub import ucs, astar
from heuristics_stub import zero_heuristic

MAPS = [
       "tiny_map.txt",
       "small_map.txt",
       "medium1_map.txt",
       "example_map.txt",
       "large_map.txt",
       "big1_map.txt",
       "big2_map.txt",
   ]
REPEATS = 3

def run_once(algo_name, algo_func, problem):
    start = time.perf_counter()
    path, cost, expanded, max_frontier = algo_func(problem)
    elapsed = time.perf_counter() - start
    return {
        "algo": algo_name,
        "steps": len(path) if path is not None else None,
        "cost": cost,
        "expanded": expanded,
        "max_frontier": max_frontier,
        "time": elapsed,
    }

def average_runs(algo_name, algo_func, map_path):
    results = []
    for _ in range(REPEATS):
        problem = SokobanProblem(map_path)
        results.append(run_once(algo_name, algo_func, problem))

    avg_time = sum(r["time"] for r in results) / REPEATS
    sample = results[0]
    return {
        "algo": algo_name,
        "steps": sample["steps"],
        "cost": sample["cost"],
        "expanded": sample["expanded"],
        "max_frontier": sample["max_frontier"],
        "avg_time": avg_time,
        "peak_mb": measure_memory(algo_func, map_path),
    }

def measure_memory(algo_func, map_path):
    problem = SokobanProblem(map_path)
    tracemalloc.start()
    algo_func(problem)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return peak / (1024 * 1024)

def save_csv(rows, path="results.csv"):
    fields = ["map", "algo", "steps", "cost", "expanded",
              "max_frontier", "avg_time", "peak_mb"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    print(f"{'Map':<18}{'Algo':<6}{'Steps':<8}{'Cost':<8}{'Expanded':<12}{'MaxFrontier':<14}{'AvgTime(s)':<12}{'PeakMem(MB)':<10}")

    rows = []

    for map_path in MAPS:
        ucs_result = average_runs("UCS", ucs, map_path)
        astar_result = average_runs(
            "A*",
            lambda p: astar(p, zero_heuristic),
            map_path,
        )

        for r in (ucs_result, astar_result):
            r["map"] = map_path
            rows.append(r)
            print(f"{map_path:<18}{r['algo']:<6}{r['steps']:<8}{r['cost']:<8}"
                  f"{r['expanded']:<12}{r['max_frontier']:<14}{r['avg_time']:<12.4f}{r['peak_mb']:<10.1f}")

    save_csv(rows)
    print("Da luu results.csv")

if __name__ == "__main__":
    main()