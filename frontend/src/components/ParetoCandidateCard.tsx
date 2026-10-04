import React from 'react';
import type { ParetoCandidate } from '../types/api';

interface ParetoCandidateCardProps {
  candidate: ParetoCandidate;
}

export const ParetoCandidateCard: React.FC<ParetoCandidateCardProps> = ({ candidate }) => {
  const { candidate_design, objective_values, explanation_payload } = candidate;

  const renderObjective = (key: string, label: string) => {
    const obj = objective_values[key];
    if (!obj) return null;

    return (
      <div className="text-sm">
        <span className="font-semibold text-gray-700">{label}: </span>
        <span className="text-gray-900">
          {obj.is_interval ? `[${obj.value_min?.toFixed(2)}, ${obj.value_max?.toFixed(2)}]` : obj.value?.toFixed(2)} {obj.unit}
        </span>
        <span className="text-xs text-gray-500 ml-1">({obj.direction})</span>
      </div>
    );
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
      <h3 className="text-lg font-bold text-blue-900 mb-2">{candidate_design.material_name}</h3>
      <p className="text-xs text-gray-500 mb-4 font-mono">{candidate.pareto_candidate_id}</p>

      <div className="mb-4">
        <h4 className="text-md font-semibold text-gray-800 mb-1">Objectives</h4>
        <div className="space-y-1">
          {renderObjective('f_thickness', 'Thickness')}
          {renderObjective('f_moisture_margin', 'Moisture Margin')}
          {renderObjective('f_gas_alignment', 'Gas Alignment')}
          {renderObjective('f_shelf_life_margin', 'Shelf Life Margin')}
        </div>
      </div>

      <div className="mb-4 bg-gray-50 p-3 rounded text-sm">
        <h4 className="font-semibold text-gray-800 mb-1">Trade-off Summary</h4>
        <p className="text-gray-700">{explanation_payload.trade_off_summary}</p>
      </div>
      
      <div className="flex gap-4 text-sm">
        <div>
          <span className="font-semibold text-gray-700">Strength: </span>
          <span className="text-green-700">{explanation_payload.primary_strength}</span>
        </div>
        <div>
          <span className="font-semibold text-gray-700">Limiting: </span>
          <span className="text-amber-700">{explanation_payload.limiting_barrier}</span>
        </div>
      </div>
    </div>
  );
};
