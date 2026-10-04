import React from 'react';
import type { RecommendationResponse } from '../types/api';
import { ParetoCandidateCard } from './ParetoCandidateCard';

interface RecommendationResultsProps {
  results: RecommendationResponse;
}

export const RecommendationResults: React.FC<RecommendationResultsProps> = ({ results }) => {
  return (
    <div className="space-y-8">
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recommendation Run Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded text-center">
            <p className="text-sm text-blue-800 font-semibold uppercase">Candidates Evaluated</p>
            <p className="text-3xl font-bold text-blue-900">{results.total_candidates_evaluated}</p>
          </div>
          <div className="bg-green-50 p-4 rounded text-center">
            <p className="text-sm text-green-800 font-semibold uppercase">Feasible</p>
            <p className="text-3xl font-bold text-green-900">{results.feasible_candidates_count}</p>
          </div>
          <div className="bg-red-50 p-4 rounded text-center">
            <p className="text-sm text-red-800 font-semibold uppercase">Infeasible</p>
            <p className="text-3xl font-bold text-red-900">{results.infeasible_candidates_count}</p>
          </div>
          <div className="bg-amber-50 p-4 rounded text-center">
            <p className="text-sm text-amber-800 font-semibold uppercase">Pareto Optimal</p>
            <p className="text-3xl font-bold text-amber-900">{results.pareto_front.candidate_count}</p>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Pareto Candidates</h2>
        {results.pareto_front.candidates.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center text-gray-600">
            No feasible candidates found for these requirements.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.pareto_front.candidates.map((cand) => (
              <ParetoCandidateCard key={cand.pareto_candidate_id} candidate={cand} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
