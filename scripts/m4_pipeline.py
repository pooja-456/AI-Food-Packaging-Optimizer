import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
RAW_DIR = ROOT_DIR / "data/raw"
PROCESSED_DIR = ROOT_DIR / "data/processed"
REF_DIR = ROOT_DIR / "data/reference"

class M4Pipeline:
    def __init__(self):
        self.cleaning_logs = []
        self.validation_results = {}
        
    def log_transform(self, dataset: str, record_id: str, field: str, orig_val: Any, new_val: Any, trans_type: str, reason: str, rule_id: str):
        if orig_val != new_val:
            self.cleaning_logs.append({
                "dataset": dataset,
                "record_id": record_id,
                "field": field,
                "original_value": orig_val,
                "transformed_value": new_val,
                "transformation_type": trans_type,
                "reason": reason,
                "rule_id": rule_id,
                "source_preserved": True
            })

    def handle_missingness(self, val: Any) -> Any:
        if val in ["N/A", "NA", "n/a", "unknown", "Unknown", "", "-", "not reported", "not available"]:
            return None
        return val

    def clean_string(self, dataset: str, rec_id: str, field: str, val: Any) -> Any:
        if isinstance(val, str):
            cleaned = val.strip()
            self.log_transform(dataset, rec_id, field, val, cleaned, "WHITESPACE_TRIM", "Trimmed leading/trailing whitespace", "RULE-STR-01")
            return cleaned
        return val

    def parse_numeric_or_range(self, dataset: str, rec_id: str, field: str, val: Any) -> Dict[str, Any]:
        val = self.handle_missingness(val)
        if val is None:
            return {"original_value": val, "is_missing": True}
            
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return {"original_value": val, "value": float(val), "value_min": float(val), "value_max": float(val), "operator": "=", "is_range": False}
        
        if isinstance(val, str):
            val_clean = val.strip()
            range_match = re.match(r'^([\d.]+)\s*[\?"\-]\s*([\d.]+)$', val_clean)
            if range_match:
                min_v = float(range_match.group(1))
                max_v = float(range_match.group(2))
                res = {"original_value": val, "value_min": min_v, "value_max": max_v, "operator": "RANGE", "is_range": True}
                self.log_transform(dataset, rec_id, field, val, res, "RANGE_PARSE", "Parsed numeric range", "RULE-NUM-01")
                return res
            ineq_match = re.match(r'^(<|<=|>|>=)\s*([\d.]+)$', val_clean)
            if ineq_match:
                op = ineq_match.group(1)
                num = float(ineq_match.group(2))
                res = {"original_value": val, "operator": op, "value": num, "is_range": False}
                self.log_transform(dataset, rec_id, field, val, res, "INEQUALITY_PARSE", "Parsed numeric inequality", "RULE-NUM-02")
                return res
            try:
                num = float(val_clean)
                return {"original_value": val, "value": num, "value_min": num, "value_max": num, "operator": "=", "is_range": False}
            except ValueError:
                pass
        return {"original_value": val, "is_missing": False, "unparsed": True}

    def process_usda_fdc(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "food/usda_fdc/usda_fdc_sample_foundation.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("records", []):
            rec_id = str(rec.get("fdc_id"))
            p_rec = dict(rec)
            
            p_rec["commodity_name"] = self.clean_string("usda_fdc", rec_id, "commodity_name", rec.get("commodity_name"))
            
            orig_proc = rec.get("processing_state")
            if orig_proc:
                p_rec["processing_state"] = orig_proc.upper()
                self.log_transform("usda_fdc", rec_id, "processing_state", orig_proc, p_rec["processing_state"], "CATEGORY_STANDARDIZATION", "Uppercase processing state", "RULE-CAT-01")
            
            phys = p_rec.get("physicochemical_properties", {})
            if "ph_typical" in phys:
                phys["ph_typical_parsed"] = self.parse_numeric_or_range("usda_fdc", rec_id, "ph_typical", phys["ph_typical"])
            if "water_activity_aw" in phys:
                phys["water_activity_aw_parsed"] = self.parse_numeric_or_range("usda_fdc", rec_id, "water_activity_aw", phys["water_activity_aw"])
            
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "usda_fdc",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "records": processed_records}
        return out_data, val_summary

    def process_india_ifct(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "food/india_ifct/india_ifct_2017_composition.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("records", []):
            rec_id = str(rec.get("ifct_code"))
            p_rec = dict(rec)
            
            p_rec["food_name"] = self.clean_string("india_ifct", rec_id, "food_name", rec.get("food_name"))
            
            orig_proc = rec.get("processing_state")
            if orig_proc:
                p_rec["processing_state"] = orig_proc.upper()
                self.log_transform("india_ifct", rec_id, "processing_state", orig_proc, p_rec["processing_state"], "CATEGORY_STANDARDIZATION", "Uppercase processing state", "RULE-CAT-01")
            
            moisture = rec.get("proximate_composition", {}).get("moisture_percent")
            if moisture is not None:
                p_rec["proximate_composition"]["moisture_percent_parsed"] = self.parse_numeric_or_range("india_ifct", rec_id, "moisture_percent", moisture)
                
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "india_ifct",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "records": processed_records}
        return out_data, val_summary

    def process_usda_hb66(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "postharvest/usda/usda_handbook_66_respiration.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("records", []):
            rec_id = str(rec.get("commodity_name"))
            p_rec = dict(rec)
            p_rec["commodity_name"] = self.clean_string("usda_handbook_66", rec_id, "commodity_name", rec.get("commodity_name"))
            
            resp_cleaned = []
            for item in rec.get("respiration_measurements", []):
                item_c = dict(item)
                for key in ["co2_production_rate_min_mg_kg_h", "co2_production_rate_max_mg_kg_h", "o2_consumption_rate_min_mg_kg_h", "o2_consumption_rate_max_mg_kg_h", "temperature_c"]:
                    if key in item_c:
                        item_c[f"{key}_parsed"] = self.parse_numeric_or_range("usda_handbook_66", rec_id, key, item_c[key])
                resp_cleaned.append(item_c)
            p_rec["respiration_measurements"] = resp_cleaned
            
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "usda_handbook_66",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "records": processed_records}
        return out_data, val_summary

    def process_uc_davis(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "postharvest/uc_davis/uc_davis_produce_facts.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("records", []):
            rec_id = str(rec.get("commodity_name"))
            p_rec = dict(rec)
            p_rec["commodity_name"] = self.clean_string("uc_davis", rec_id, "commodity_name", rec.get("commodity_name"))
            
            resp_cleaned = []
            for item in p_rec.get("respiration_profile", []):
                item_c = dict(item)
                for key in ["temperature_c", "co2_production_rate_min_mg_kg_h", "co2_production_rate_max_mg_kg_h"]:
                    if key in item_c:
                        item_c[f"{key}_parsed"] = self.parse_numeric_or_range("uc_davis", rec_id, key, item_c[key])
                resp_cleaned.append(item_c)
            p_rec["respiration_profile"] = resp_cleaned
                
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "uc_davis",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "records": processed_records}
        return out_data, val_summary

    def process_indian_postharvest(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "postharvest/india/icar_iifpt_indian_postharvest.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("records", []):
            rec_id = str(rec.get("commodity_id"))
            p_rec = dict(rec)
            p_rec["commodity_name"] = self.clean_string("indian_postharvest", rec_id, "commodity_name", rec.get("commodity_name"))
            
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "indian_postharvest",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "records": processed_records}
        return out_data, val_summary

    def process_cirad_wur(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "materials/cirad_wur/cirad_wur_packaging_dataset.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_materials = []
        valid_count = 0
        
        for rec in raw_data.get("materials", []):
            rec_id = str(rec.get("material_id"))
            p_rec = dict(rec)
            
            b_cleaned = []
            for b in p_rec.get("barrier_measurements", []):
                b_c = dict(b)
                if "value" in b_c:
                    b_c["value_parsed"] = self.parse_numeric_or_range("cirad_wur", rec_id, b_c.get("property", "value"), b_c["value"])
                if "test_temperature_c" in b_c:
                    b_c["test_temperature_c_parsed"] = self.parse_numeric_or_range("cirad_wur", rec_id, "test_temperature_c", b_c["test_temperature_c"])
                b_cleaned.append(b_c)
            p_rec["barrier_measurements"] = b_cleaned
            
            valid_count += 1
            processed_materials.append(p_rec)
            
        val_summary = {
            "dataset": "cirad_wur",
            "total_records": len(processed_materials),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "materials": processed_materials}
        return out_data, val_summary

    def process_polyid(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "materials/polyid/polyid_experimental_vs_predicted.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        p_data = {"source_metadata": raw_data.get("source_metadata", {}), "experimental_observations": [], "predicted_values": []}
        valid_count = 0
        
        for rec in raw_data.get("experimental_observations", []):
            rec_id = str(rec.get("polyid_exp_id"))
            p_rec = dict(rec)
            p_rec["evidence_classification"] = "EXPERIMENTAL_LITERATURE_DATA"
            p_data["experimental_observations"].append(p_rec)
            valid_count += 1
            
        for rec in raw_data.get("predicted_values", []):
            rec_id = str(rec.get("polyid_pred_id"))
            p_rec = dict(rec)
            p_rec["evidence_classification"] = "MODEL_PREDICTED"
            p_data["predicted_values"].append(p_rec)
            valid_count += 1
            
        val_summary = {
            "dataset": "polyid",
            "total_records": len(p_data["experimental_observations"]) + len(p_data["predicted_values"]),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        return p_data, val_summary

    def process_manufacturer_tds(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "materials/manufacturer/manufacturer_tds_datasheets.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("datasheets", []):
            rec_id = str(rec.get("datasheet_id"))
            p_rec = dict(rec)
            p_rec["brand_grade"] = self.clean_string("manufacturer_tds", rec_id, "brand_grade", rec.get("brand_grade"))
            
            b_cleaned = []
            for b in p_rec.get("barrier_profiles", []):
                b_c = dict(b)
                if "value" in b_c:
                    b_c["value_parsed"] = self.parse_numeric_or_range("manufacturer_tds", rec_id, b_c.get("property", "value"), b_c["value"])
                b_cleaned.append(b_c)
            p_rec["barrier_profiles"] = b_cleaned
            
            outlier_check = any(b.get("property") == "OTR" and b.get("test_rh_percent") == 85.0 for b in rec.get("barrier_profiles", []))
            if outlier_check:
                p_rec["outlier_annotation"] = {
                    "field": "barrier_profiles.OTR",
                    "classification": "STATISTICALLY_UNUSUAL_BUT_POSSIBLY_VALID",
                    "action": "RETAIN",
                    "scientific_rationale": "EVOH hydrophilic swelling at 85% RH increases OTR by >10x compared to dry gas."
                }
                
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "manufacturer_tds",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "datasheets": processed_records}
        return out_data, val_summary

    def process_combase(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        raw_path = RAW_DIR / "microbial/combase/combase_microbial_kinetics.json"
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        processed_records = []
        valid_count = 0
        
        for rec in raw_data.get("records", []):
            rec_id = str(rec.get("combase_id"))
            p_rec = dict(rec)
            
            for key in ["temperature_c", "water_activity_aw", "ph_level"]:
                if key in p_rec:
                    p_rec[f"{key}_parsed"] = self.parse_numeric_or_range("combase", rec_id, key, p_rec[key])
            
            valid_count += 1
            processed_records.append(p_rec)
            
        val_summary = {
            "dataset": "combase",
            "total_records": len(processed_records),
            "valid_records": valid_count,
            "records_with_warnings": 0,
            "invalid_records": 0
        }
        out_data = {"source_metadata": raw_data.get("source_metadata", {}), "records": processed_records}
        return out_data, val_summary

    def run_pipeline(self):
        print("Starting Corrected M4 Data Cleaning & Validation Pipeline...")
        
        usda_fdc, val_usda_fdc = self.process_usda_fdc()
        india_ifct, val_india_ifct = self.process_india_ifct()
        usda_hb66, val_usda_hb66 = self.process_usda_hb66()
        uc_davis, val_uc_davis = self.process_uc_davis()
        indian_postharvest, val_indian_postharvest = self.process_indian_postharvest()
        cirad_wur, val_cirad_wur = self.process_cirad_wur()
        polyid, val_polyid = self.process_polyid()
        tds, val_tds = self.process_manufacturer_tds()
        combase, val_combase = self.process_combase()
        
        self.validation_results = {
            "usda_fdc": val_usda_fdc,
            "india_ifct": val_india_ifct,
            "usda_handbook_66": val_usda_hb66,
            "uc_davis": val_uc_davis,
            "indian_postharvest": val_indian_postharvest,
            "cirad_wur": val_cirad_wur,
            "polyid": val_polyid,
            "manufacturer_tds": val_tds,
            "combase": val_combase
        }
        
        self.save_processed("food/usda_fdc/usda_fdc_sample_foundation.json", usda_fdc)
        self.save_processed("food/india_ifct/india_ifct_2017_composition.json", india_ifct)
        self.save_processed("postharvest/usda/usda_handbook_66_respiration.json", usda_hb66)
        self.save_processed("postharvest/uc_davis/uc_davis_produce_facts.json", uc_davis)
        self.save_processed("postharvest/india/icar_iifpt_indian_postharvest.json", indian_postharvest)
        self.save_processed("materials/cirad_wur/cirad_wur_packaging_dataset.json", cirad_wur)
        self.save_processed("materials/polyid/polyid_experimental_vs_predicted.json", polyid)
        self.save_processed("materials/manufacturer/manufacturer_tds_datasheets.json", tds)
        self.save_processed("microbial/combase/combase_microbial_kinetics.json", combase)
        
        REF_DIR.mkdir(parents=True, exist_ok=True)
        with open(REF_DIR / "cleaning_log.json", "w", encoding="utf-8") as f:
            json.dump(self.cleaning_logs, f, indent=2)
        print(f"Cleaning log written to {REF_DIR / 'cleaning_log.json'} ({len(self.cleaning_logs)} entries)")
        
        with open(REF_DIR / "validation_results.json", "w", encoding="utf-8") as f:
            json.dump(self.validation_results, f, indent=2)
        print(f"Validation results written to {REF_DIR / 'validation_results.json'}")

    def save_processed(self, rel_path: str, data: Any):
        out_file = PROCESSED_DIR / rel_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved processed dataset to {out_file}")

if __name__ == "__main__":
    pipeline = M4Pipeline()
    pipeline.run_pipeline()
