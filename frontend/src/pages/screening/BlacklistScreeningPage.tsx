/**
 * Blacklist Screening Page - Upload blacklist CSV and review matches
 * New workflow: Upload BLACKLIST to screen against pre-loaded KAMCO entities
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Database,
} from 'lucide-react';
import {
  uploadBlacklistCSV,
  getKamcoEntities,
  getPendingMatches,
  getUploadHistory,
  BlacklistUploadResponse,
  KamcoEntity,
  PendingMatch,
  UploadHistory,
} from '../../services/screeningV2Api';

const BlacklistScreeningPage: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(70);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<BlacklistUploadResponse | null>(null);
  const [kamcoEntities, setKamcoEntities] = useState<KamcoEntity[]>([]);
  const [pendingMatches, setPendingMatches] = useState<PendingMatch[]>([]);
  const [uploadHistory, setUploadHistory] = useState<UploadHistory[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [entitiesRes, matchesRes, historyRes] = await Promise.all([
        getKamcoEntities({ limit: 10 }),
        getPendingMatches({ limit: 10 }),
        getUploadHistory(10),
      ]);

      setKamcoEntities(entitiesRes.entities);
      setPendingMatches(matchesRes.matches);
      setUploadHistory(historyRes.uploads);
    } catch (err: any) {
      console.error('Error loading dashboard:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await uploadBlacklistCSV(file, threshold);
      setUploadResult(result);
      
      // Reload dashboard data
      await loadDashboardData();
      
      // Clear file input
      setFile(null);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload blacklist');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Blacklist Screening
          </h1>
          <p className="text-gray-600">
            Upload blacklist CSV files to screen against pre-loaded KAMCO entities
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Upload className="mr-2" size={24} />
            Upload Blacklist CSV
          </h2>

          <div className="space-y-4">
            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Blacklist File (CSV)
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100
                  cursor-pointer"
              />
              {file && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                </p>
              )}
            </div>

            {/* Threshold Slider */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Match Threshold: {threshold}%
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0% (Show all)</span>
                <span>50% (Moderate)</span>
                <span>100% (Exact only)</span>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Only matches with score ≥ {threshold}% will be shown
              </p>
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className={`w-full py-3 px-4 rounded-lg font-semibold text-white
                ${
                  !file || uploading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }
                transition-colors duration-200 flex items-center justify-center`}
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="mr-2" size={20} />
                  Upload and Screen
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <XCircle className="text-red-500 mr-2 flex-shrink-0" size={20} />
              <div>
                <p className="text-red-800 font-semibold">Error</p>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Success Result */}
          {uploadResult && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start mb-3">
                <CheckCircle className="text-green-500 mr-2 flex-shrink-0" size={20} />
                <div>
                  <p className="text-green-800 font-semibold">Upload Successful!</p>
                  <p className="text-green-700 text-sm">
                    Processed {uploadResult.entries_processed} blacklist entries
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                <div className="bg-white p-3 rounded border border-green-200">
                  <p className="text-xs text-gray-600">Matches Found</p>
                  <p className="text-2xl font-bold text-green-700">
                    {uploadResult.matches_found}
                  </p>
                </div>
                <div className="bg-white p-3 rounded border border-green-200">
                  <p className="text-xs text-gray-600">Already Decided</p>
                  <p className="text-2xl font-bold text-gray-700">
                    {uploadResult.skipped_already_decided}
                  </p>
                </div>
                <div className="bg-white p-3 rounded border border-green-200">
                  <p className="text-xs text-gray-600">Re-reviews</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {uploadResult.re_reviews_flagged}
                  </p>
                </div>
                <div className="bg-white p-3 rounded border border-green-200">
                  <p className="text-xs text-gray-600">Threshold Used</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {uploadResult.threshold_used}%
                  </p>
                </div>
              </div>

              {uploadResult.matches.length > 0 && (
                <button
                  onClick={() => navigate('/screener/pending-matches')}
                  className="mt-4 w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors"
                >
                  View {uploadResult.matches_found} Pending Match{uploadResult.matches_found !== 1 ? 'es' : ''}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Dashboard Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* KAMCO Entities */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center">
                <Database className="mr-2 text-blue-600" size={20} />
                KAMCO Entities
              </h3>
            </div>
            <p className="text-3xl font-bold text-blue-600">{kamcoEntities.length}+</p>
            <p className="text-sm text-gray-600 mt-2">Pre-loaded in database</p>
          </div>

          {/* Pending Matches */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center">
                <AlertTriangle className="mr-2 text-orange-600" size={20} />
                Pending Matches
              </h3>
            </div>
            <p className="text-3xl font-bold text-orange-600">{pendingMatches.length}</p>
            <p className="text-sm text-gray-600 mt-2">Awaiting decision</p>
          </div>

          {/* Recent Uploads */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center">
                <FileText className="mr-2 text-green-600" size={20} />
                Recent Uploads
              </h3>
            </div>
            <p className="text-3xl font-bold text-green-600">{uploadHistory.length}</p>
            <p className="text-sm text-gray-600 mt-2">Last 10 uploads</p>
          </div>
        </div>

        {/* Recent Upload History */}
        {uploadHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <FileText className="mr-2" size={24} />
              Recent Upload History
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Filename
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Uploaded By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Entries
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Matches
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Threshold
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {uploadHistory.map((upload) => (
                    <tr key={upload.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {upload.filename}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {upload.uploaded_by}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(upload.uploaded_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {upload.total_entries}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                          {upload.matches_found}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {upload.threshold_used}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BlacklistScreeningPage;
