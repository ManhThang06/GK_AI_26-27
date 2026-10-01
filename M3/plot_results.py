import csv
import matplotlib.pyplot as plt
ASTAR_LABEL = "A* (h = 0)"

def read_map_size(map_path):
    with open(map_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    n_rows = len(lines)
    n_cols = max(len(line) for line in lines)
    return n_rows, n_cols

def load_results(path="results.csv"):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["map"]
            if name not in data:
                data[name] = {}
            data[name][row["algo"]] = row
    return data

def plot_metric(data, names, sizes, key, title, ylabel, filename):
    x = list(range(len(names)))
    width = 0.38
    ucs_vals = [float(data[n]["UCS"][key]) for n in names]
    astar_vals = [float(data[n]["A*"][key]) for n in names]
    labels = [f"{n.replace('_map.txt', '')}\n{sizes[n][0]}x{sizes[n][1]}" for n in names]

    plt.figure(figsize=(8, 6))
    plt.bar([i - width / 2 for i in x], ucs_vals, width,
            label="UCS", color="white", edgecolor="black", hatch="//")
    plt.bar([i + width / 2 for i in x], astar_vals, width,
            label=ASTAR_LABEL, color="gray", edgecolor="black")
    plt.yscale("log")
    plt.xticks(x, labels)
    plt.xlabel("Bản đồ (tên, số hàng x số cột) - sắp theo kích thước tăng dần")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(axis="y", linestyle=":")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print("Da luu", filename)

def main():
    data = load_results()
    sizes = {name: read_map_size(name) for name in data}
    names = sorted(data, key=lambda n: sizes[n][0] * sizes[n][1])

    plot_metric(data, names, sizes, "avg_time",
                "Thời gian chạy: UCS và A*", "Thời gian TB (giây, thang log)",
                "chart_time.png")
    plot_metric(data, names, sizes, "expanded",
                "Số node đã mở rộng: UCS và A*", "Số node (thang log)",
                "chart_expanded.png")
    plot_metric(data, names, sizes, "max_frontier",
                "Kích thước frontier lớn nhất: UCS và A*", "Số node trong frontier (thang log)",
                "chart_frontier.png")
    plot_metric(data, names, sizes, "peak_mb",
                "Bộ nhớ đỉnh: UCS và A*", "Bộ nhớ đỉnh (MB, thang log)",
                "chart_memory.png")

if __name__ == "__main__":
    main()