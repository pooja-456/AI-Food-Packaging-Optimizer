export interface PackagingRequest {
  commodity: string;
  product_form: string;
  ripeness_stage: string;
  target_shelf_life_days: number;
  storage_type: string;
  
  variety?: string;
  transportation_type?: string;
  transportation_duration_days?: number;
  
  storage_temperature_c?: number;
  relative_humidity_percent?: number;
  
  moisture_percent?: number;
  fat_percent?: number;
  ph?: number;
  respiration_rate?: number;
  
  package_surface_area_m2?: number;
  package_headspace_volume_cm3?: number;
  product_mass_kg?: number;
}

export interface RecommendationResponse {
  recommendation_run_id: string;
  timestamp: string;
  request: PackagingRequest;
  inference_profile: any;
  requirement_envelope: any;
  total_candidates_evaluated: number;
  feasible_candidates_count: number;
  infeasible_candidates_count: number;
  unknown_candidates_count: number;
  pareto_front: ParetoFront;
  candidate_summaries: any[];
  all_warnings: string[];
  traceability_log: any[];
  pipeline_explainability?: any;
}

export interface ParetoFront {
  optimization_run_id: string;
  timestamp: string;
  candidate_count: number;
  candidates: ParetoCandidate[];
  hypervolume_indicator?: number;
  solver_metadata: any;
  constraint_policy_version: string;
}

export interface ParetoCandidate {
  pareto_candidate_id: string;
  candidate_design: PackagingCandidate;
  objective_values: Record<string, ObjectiveValue>;
  constraint_compliance_summary: any;
  uncertainty_profile: any;
  evidence_tier: string;
  traceability: any;
  explanation_payload: ExplanationPayload;
}

export interface PackagingCandidate {
  candidate_id: string;
  material_id: string;
  material_name: string;
  brand_grade?: string;
  decision_variables: any;
  barrier_properties: any;
  condition_match: string;
  provenance: any;
}

export interface ObjectiveValue {
  objective_name: string;
  direction: string;
  value?: number;
  value_min?: number;
  value_max?: number;
  is_interval: boolean;
  unit: string;
  status: string;
  explanation_metadata?: string;
}

export interface ExplanationPayload {
  trade_off_summary: string;
  limiting_barrier: string;
  primary_strength: string;
}
