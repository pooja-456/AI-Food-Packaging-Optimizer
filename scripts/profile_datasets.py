import json
import os
import math
from pathlib import Path

DATA_DIR = Path("C:/Users/itsme/OneDrive/Documents/PROJECTS 2026/uni projects/AI-Food-Packaging-Optimizer/data/raw")

DATASETS = [
    ("usda_fdc", DATA_DIR / "food/usda_fdc/usda_fdc_sample_foundation.json", "records"),
    ("india_ifct", DATA_DIR / "food/india_ifct/india_ifct_2017_composition.json", "records"),
    ("usda_handbook_66", DATA_DIR / "postharvest/usda/usda_handbook_66_respiration.json", "records"),
    ("uc_davis", DATA_DIR / "postharvest/uc_davis/uc_davis_produce_facts.json", "records"),
    ("indian_postharvest", DATA_DIR / "postharvest/india/icar_iifpt_indian_postharvest.json", "records"),
    ("cirad_wur", DATA_DIR / "materials/cirad_wur/cirad_wur_packaging_dataset.json", "materials"),
    ("polyid", DATA_DIR / "materials/polyid/polyid_experimental_vs_predicted.json", "polyid_root"),
    ("manufacturer_tds", DATA_DIR / "materials/manufacturer/manufacturer_tds_datasheets.json", "datasheets"),
    ("combase", DATA_DIR / "microbial/combase/combase_microbial_kinetics.json", "records"),
]

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)

def calc_stats(values):
    nums = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not nums:
        return None
    n = len(nums)
    min_v = min(nums)
    max_v = max(nums)
    mean_v = sum(nums) / n
    sorted_nums = sorted(nums)
    median_v = sorted_nums[n // 2] if n % 2 == 1 else (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2.0
    var_v = sum((x - mean_v) ** 2 for x in nums) / n if n > 1 else 0.0
    std_v = math.sqrt(var_v)
    return {
        "count": n,
        "min": round(min_v, 4),
        "max": round(max_v, 4),
        "mean": round(mean_v, 4),
        "median": round(median_v, 4),
        "std": round(std_v, 4)
    }

def profile_dataset(name, path, root_key):
    if not path.exists():
        print(f"File missing: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    file_size_bytes = os.path.getsize(path)
    
    if root_key == "polyid_root":
        records = []
        for exp in data.get("experimental_observations", []):
            exp_copy = dict(exp)
            exp_copy["record_subset"] = "experimental_observations"
            records.append(exp_copy)
        for pred in data.get("predicted_values", []):
            pred_copy = dict(pred)
            pred_copy["record_subset"] = "predicted_values"
            records.append(pred_copy)
    else:
        records = data.get(root_key, [])
    
    record_count = len(records)
    
    field_data = {}
    
    for rec in records:
        flat = flatten_dict(rec)
        for k, v in flat.items():
            if k not in field_data:
                field_data[k] = []
            field_data[k].append(v)
            
    fields_profile = {}
    for k, vals in field_data.items():
        null_count = sum(1 for v in vals if v is None or v == "" or v == "N/A" or v == "NA")
        non_null_count = len(vals) - null_count
        null_pct = round((null_count / len(vals)) * 100, 2) if len(vals) > 0 else 0.0
        
        non_null_vals = [v for v in vals if v is not None and v != "" and v != "N/A" and v != "NA"]
        
        types = set(type(v).__name__ for v in non_null_vals)
        dtype = "/".join(types) if types else "null"
        
        str_vals = [str(v) for v in non_null_vals if not isinstance(v, (dict, list))]
        unique_vals = set(str_vals)
        unique_count = len(unique_vals)
        
        stats = calc_stats(non_null_vals)
        
        fields_profile[k] = {
            "dtype": dtype,
            "non_null_count": non_null_count,
            "null_count": null_count,
            "null_pct": null_pct,
            "unique_count": unique_count,
            "sample_values": str_vals[:5],
            "numerical_stats": stats
        }
        
    return {
        "dataset_name": name,
        "path": str(path),
        "file_size_bytes": file_size_bytes,
        "record_count": record_count,
        "total_fields": len(fields_profile),
        "top_level_keys": list(data.keys()),
        "fields": fields_profile
    }

def main():
    profile = {}
    for name, path, root_key in DATASETS:
        res = profile_dataset(name, path, root_key)
        if res:
            profile[name] = res
            print(f"Profiled {name}: {res['record_count']} records, {res['total_fields']} fields.")
            
    out_path = Path("C:/Users/itsme/OneDrive/Documents/PROJECTS 2026/uni projects/AI-Food-Packaging-Optimizer/data/reference/data_profile.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    print(f"Data profile written to {out_path}")

if __name__ == "__main__":
    main()
