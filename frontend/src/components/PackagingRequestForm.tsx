import React, { useState } from 'react';
import type { PackagingRequest } from '../types/api';

interface PackagingRequestFormProps {
  onSubmit: (request: PackagingRequest) => void;
  isLoading: boolean;
}

export const PackagingRequestForm: React.FC<PackagingRequestFormProps> = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState<Partial<PackagingRequest>>({
    commodity: 'strawberry',
    product_form: 'whole',
    ripeness_stage: 'ripe',
    target_shelf_life_days: 14,
    storage_type: 'chilled',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    let parsedValue: string | number = value;

    if (type === 'number') {
      parsedValue = value === '' ? '' : Number(value);
    }

    setFormData((prev) => ({
      ...prev,
      [name]: parsedValue === '' ? undefined : parsedValue,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData as PackagingRequest);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 className="text-xl font-bold text-gray-900 mb-6">New Recommendation Request</h2>
      
      <div className="space-y-6">
        <section>
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mb-4">Required Parameters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Commodity</label>
              <input required type="text" name="commodity" value={formData.commodity || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" placeholder="e.g. strawberry" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Form</label>
              <input required type="text" name="product_form" value={formData.product_form || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" placeholder="e.g. whole" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ripeness Stage</label>
              <input required type="text" name="ripeness_stage" value={formData.ripeness_stage || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" placeholder="e.g. ripe" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Shelf Life (days)</label>
              <input required type="number" min="1" name="target_shelf_life_days" value={formData.target_shelf_life_days || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Storage Type</label>
              <select required name="storage_type" value={formData.storage_type || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md bg-white">
                <option value="chilled">Chilled</option>
                <option value="ambient">Ambient</option>
                <option value="frozen">Frozen</option>
              </select>
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mb-4">Logistics & Environment (Optional)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Variety</label>
              <input type="text" name="variety" value={formData.variety || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Transportation Type</label>
              <input type="text" name="transportation_type" value={formData.transportation_type || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Transportation Duration (days)</label>
              <input type="number" step="0.1" min="0" name="transportation_duration_days" value={formData.transportation_duration_days || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Storage Temperature (°C)</label>
              <input type="number" step="0.1" name="storage_temperature_c" value={formData.storage_temperature_c || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Relative Humidity (%)</label>
              <input type="number" step="0.1" min="0" max="100" name="relative_humidity_percent" value={formData.relative_humidity_percent || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
          </div>
        </section>

        <section>
          <div className="flex justify-between items-end border-b pb-2 mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Scientific Overrides (Optional)</h3>
            <span className="text-sm text-gray-500">Leave blank to allow inference engine resolution</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Moisture (%)</label>
              <input type="number" step="0.1" min="0" max="100" name="moisture_percent" value={formData.moisture_percent || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fat (%)</label>
              <input type="number" step="0.1" min="0" max="100" name="fat_percent" value={formData.fat_percent || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">pH</label>
              <input type="number" step="0.1" min="0" max="14" name="ph" value={formData.ph || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Respiration Rate</label>
              <input type="number" step="0.1" min="0" name="respiration_rate" value={formData.respiration_rate || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mb-4">Package Geometry (Optional)</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Surface Area (m²)</label>
              <input type="number" step="0.01" min="0" name="package_surface_area_m2" value={formData.package_surface_area_m2 || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Headspace Volume (cm³)</label>
              <input type="number" step="0.1" min="0" name="package_headspace_volume_cm3" value={formData.package_headspace_volume_cm3 || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Product Mass (kg)</label>
              <input type="number" step="0.01" min="0" name="product_mass_kg" value={formData.product_mass_kg || ''} onChange={handleChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
          </div>
        </section>

        <div className="pt-4 flex justify-end">
          <button 
            type="submit" 
            disabled={isLoading}
            className="px-6 py-2 bg-blue-700 text-white font-semibold rounded-md shadow hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Running Scientific Pipeline...' : 'Generate Recommendation'}
          </button>
        </div>
      </div>
    </form>
  );
};
