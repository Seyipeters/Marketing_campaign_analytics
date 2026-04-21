from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def write_bar_chart_svg(labels, values, title, y_label, output_path, color="#4f6ef7"):
    width, height = 860, 520
    margin_left, margin_right, margin_top, margin_bottom = 70, 30, 70, 100
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_val = max(values) if values else 1
    max_val = max_val if max_val > 0 else 1
    bar_count = len(values)
    gap = 16
    bar_width = (plot_width - gap * (bar_count - 1)) / max(bar_count, 1)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="36" text-anchor="middle" font-size="24" font-family="Segoe UI" fill="#172033">{title}</text>',
        f'<text x="20" y="{margin_top + plot_height/2}" transform="rotate(-90 20 {margin_top + plot_height/2})" text-anchor="middle" font-size="14" font-family="Segoe UI" fill="#5f6c87">{y_label}</text>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>'
    ]

    for i, (label, val) in enumerate(zip(labels, values)):
        bar_h = (val / max_val) * (plot_height - 10)
        x = margin_left + i * (bar_width + gap)
        y = margin_top + plot_height - bar_h

        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_h:.1f}" fill="{color}" rx="4"/>')
        svg.append(f'<text x="{x + bar_width/2:.1f}" y="{margin_top + plot_height + 22}" text-anchor="middle" font-size="12" font-family="Segoe UI" fill="#172033" transform="rotate(15 {x + bar_width/2:.1f} {margin_top + plot_height + 22})">{label}</text>')
        svg.append(f'<text x="{x + bar_width/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-size="12" font-family="Segoe UI" fill="#172033">{val:.2f}</text>')

    svg.append('</svg>')
    output_path.write_text("\n".join(svg), encoding="utf-8")


def write_line_chart_svg(x_labels, y1, y2, title, output_path):
    width, height = 900, 520
    margin_left, margin_right, margin_top, margin_bottom = 70, 40, 70, 90
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_val = max(max(y1), max(y2)) if y1 and y2 else 1
    max_val = max_val if max_val > 0 else 1
    count = len(x_labels)

    def points(series):
        coords = []
        for i, val in enumerate(series):
            x = margin_left + (i / max(count - 1, 1)) * plot_width
            y = margin_top + plot_height - (val / max_val) * (plot_height - 10)
            coords.append((x, y))
        return coords

    p1 = points(y1)
    p2 = points(y2)

    def path_str(pts):
        return " ".join([f"{x:.1f},{y:.1f}" for x, y in pts])

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="36" text-anchor="middle" font-size="24" font-family="Segoe UI" fill="#172033">{title}</text>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>',
        f'<polyline fill="none" stroke="#e76f51" stroke-width="3" points="{path_str(p1)}"/>',
        f'<polyline fill="none" stroke="#2a9d8f" stroke-width="3" points="{path_str(p2)}"/>',
        '<rect x="690" y="82" width="14" height="14" fill="#e76f51"/><text x="710" y="94" font-size="12" font-family="Segoe UI" fill="#172033">Spend</text>',
        '<rect x="770" y="82" width="14" height="14" fill="#2a9d8f"/><text x="790" y="94" font-size="12" font-family="Segoe UI" fill="#172033">Revenue</text>'
    ]

    for i, lbl in enumerate(x_labels):
        x = margin_left + (i / max(count - 1, 1)) * plot_width
        svg.append(f'<text x="{x:.1f}" y="{margin_top + plot_height + 22}" text-anchor="middle" font-size="12" font-family="Segoe UI" fill="#172033">{lbl}</text>')

    for x, y in p1:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#e76f51"/>')
    for x, y in p2:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2a9d8f"/>')

    svg.append('</svg>')
    output_path.write_text("\n".join(svg), encoding="utf-8")


def safe_div(a: float, b: float) -> float:
    return (a / b) if b else 0.0


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "sample_campaign_data.csv"
    figures_dir = project_root / "reports" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    with data_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                {
                    "date": r["date"],
                    "channel": r["channel"],
                    "campaign_type": r["campaign_type"],
                    "impressions": int(r["impressions"]),
                    "clicks": int(r["clicks"]),
                    "conversions": int(r["conversions"]),
                    "spend": float(r["spend"]),
                    "revenue": float(r["revenue"]),
                }
            )

    totals = {
        "spend": sum(r["spend"] for r in rows),
        "clicks": sum(r["clicks"] for r in rows),
        "conversions": sum(r["conversions"] for r in rows),
        "revenue": sum(r["revenue"] for r in rows),
    }
    print("=== Overall Totals ===")
    for k, v in totals.items():
        print(f"{k}: {v}")

    by_channel = defaultdict(lambda: {"spend": 0.0, "clicks": 0, "conversions": 0, "revenue": 0.0})
    for r in rows:
        d = by_channel[r["channel"]]
        d["spend"] += r["spend"]
        d["clicks"] += r["clicks"]
        d["conversions"] += r["conversions"]
        d["revenue"] += r["revenue"]

    channel_items = []
    for channel, vals in by_channel.items():
        vals["conversion_rate"] = safe_div(vals["conversions"], vals["clicks"])
        channel_items.append((channel, vals))
    channel_items.sort(key=lambda x: x[1]["conversion_rate"], reverse=True)

    print("\n=== Channel Performance (sorted by conversion_rate) ===")
    for channel, vals in channel_items:
        print(
            f"{channel:15} spend={vals['spend']:.2f} clicks={vals['clicks']} "
            f"conversions={vals['conversions']} revenue={vals['revenue']:.2f} "
            f"conversion_rate={vals['conversion_rate']:.4f}"
        )

    by_type = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0})
    for r in rows:
        d = by_type[r["campaign_type"]]
        d["spend"] += r["spend"]
        d["revenue"] += r["revenue"]

    type_items = []
    for campaign_type, vals in by_type.items():
        vals["roas"] = safe_div(vals["revenue"], vals["spend"])
        type_items.append((campaign_type, vals))
    type_items.sort(key=lambda x: x[1]["roas"], reverse=True)

    print("\n=== ROAS by Campaign Type ===")
    for campaign_type, vals in type_items:
        print(f"{campaign_type:15} spend={vals['spend']:.2f} revenue={vals['revenue']:.2f} roas={vals['roas']:.4f}")

    write_bar_chart_svg(
        labels=[name for name, _ in channel_items],
        values=[vals["conversion_rate"] * 100 for _, vals in channel_items],
        title="Conversion Rate by Channel",
        y_label="Conversion Rate (%)",
        output_path=figures_dir / "conversion_rate_by_channel.svg",
        color="#4f6ef7",
    )

    write_bar_chart_svg(
        labels=[name for name, _ in type_items],
        values=[vals["roas"] for _, vals in type_items],
        title="ROAS by Campaign Type",
        y_label="ROAS",
        output_path=figures_dir / "roas_by_campaign_type.svg",
        color="#7c4dff",
    )

    daily = defaultdict(lambda: {"spend": 0.0, "revenue": 0.0})
    for r in rows:
        daily[r["date"]]["spend"] += r["spend"]
        daily[r["date"]]["revenue"] += r["revenue"]
    daily_dates = sorted(daily.keys())

    write_line_chart_svg(
        x_labels=daily_dates,
        y1=[daily[d]["spend"] for d in daily_dates],
        y2=[daily[d]["revenue"] for d in daily_dates],
        title="Daily Spend vs Revenue",
        output_path=figures_dir / "daily_spend_vs_revenue.svg",
    )

    print(f"\nSaved charts to: {figures_dir}")


if __name__ == "__main__":
    main()
