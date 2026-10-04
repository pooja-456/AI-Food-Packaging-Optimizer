import { useState } from 'react';
import { PackagingRequestForm } from './components/PackagingRequestForm';
import { RecommendationResults } from './components/RecommendationResults';
import { fetchRecommendation } from './api/client';
import type { PackagingRequest, RecommendationResponse } from './types/api';

function App() {
  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRequestSubmit = async (request: PackagingRequest) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await fetchRecommendation(request);
      setResults(response);
    } catch (err: any) {
      setError(err.message || 'An unknown error occurred during recommendation execution.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8 font-sans text-gray-900">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-700">
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">AI Food Packaging Optimizer</h1>
          <p className="text-lg text-gray-600 mt-2">Scientific Inverse-Design Recommendation Engine</p>
        </header>

        <PackagingRequestForm onSubmit={handleRequestSubmit} isLoading={isLoading} />

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded text-red-800">
            <h3 className="font-bold">Execution Failed</h3>
            <p>{error}</p>
          </div>
        )}

        {results && <RecommendationResults results={results} />}
      </div>
    </div>
  );
}

export default App;
