from pathlib import Path

import pandas as pd


def main() -> None:
    data_path = Path(__file__).resolve().parent.parent / "data" / "sample_campaign_data.csv"
    df = pd.read_csv(data_path)

    df["ctr"] = df["clicks"] / df["impressions"]
    df["conversion_rate"] = df["conversions"] / df["clicks"].replace(0, pd.NA)
    df["roas"] = df["revenue"] / df["spend"].replace(0, pd.NA)

    totals = df[["spend", "clicks", "conversions", "revenue"]].sum()
    print("=== Overall Totals ===")
    print(totals.to_string())

    by_channel = (
        df.groupby("channel", as_index=False)
        .agg(
            spend=("spend", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        )
    )
    by_channel["conversion_rate"] = by_channel["conversions"] / by_channel["clicks"].replace(0, pd.NA)
    by_channel = by_channel.sort_values("conversion_rate", ascending=False)

    print("\n=== Channel Performance (sorted by conversion_rate) ===")
    print(by_channel.to_string(index=False))

    by_type = (
        df.groupby("campaign_type", as_index=False)
        .agg(spend=("spend", "sum"), revenue=("revenue", "sum"))
    )
    by_type["roas"] = by_type["revenue"] / by_type["spend"].replace(0, pd.NA)
    by_type = by_type.sort_values("roas", ascending=False)

    print("\n=== ROAS by Campaign Type ===")
    print(by_type.to_string(index=False))


if __name__ == "__main__":
    main()
