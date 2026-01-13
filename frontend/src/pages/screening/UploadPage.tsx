import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import FileUploadComponent from '@/components/screening/FileUploadComponent';
import { Upload as UploadIcon, FileSpreadsheet, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import apiClient from '@/services/apiClient';

const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const [blacklistFile, setBlacklistFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(70);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async () => {
    // Blacklist file is REQUIRED (to screen against KAMCO entities)
    if (!blacklistFile) {
      toast.error('Blacklist file is required to start screening');
      return;
    }

    setIsUploading(true);
    try {
      // Upload blacklist file to screen against pre-loaded KAMCO entities
      const formData = new FormData();
      formData.append('file', blacklistFile);
      formData.append('threshold', threshold.toString());

      const response = await apiClient.post('/screening/v2/upload-blacklist', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.data.success) {
        throw new Error('Blacklist upload failed');
      }

      const uploadData = response.data;
      const entriesProcessed = uploadData.entries_processed || 0;
      const matchesFound = uploadData.matches_found || 0;
      
      toast.success(`✅ Processed ${entriesProcessed} blacklist entries successfully!`);
      
      if (matchesFound > 0) {
        toast.success(`🎯 Found ${matchesFound} potential matches against KAMCO entities!`, {
          duration: 5000,
        });
      } else {
        toast.success('No matches found - all clear!');
      }

      // Navigate to screening queue
      setTimeout(() => {
        navigate('/screening');
      }, 2000);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.detail?.message || error.response?.data?.detail || error.message || 'Upload failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6 max-w-4xl mx-auto">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Upload Blacklist File</h1>
          <p className="text-muted-foreground">
            Upload blacklist CSV file to screen against KAMCO entities database
          </p>
        </div>

        <div className="grid gap-6">
          {/* Blacklist File Upload - REQUIRED */}
          <Card className="border-2 border-red-200 dark:border-red-900">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-600" />
                Blacklist File
                <span className="ml-2 text-xs font-normal text-red-600 bg-red-100 dark:bg-red-950 px-2 py-1 rounded">
                  Required
                </span>
              </CardTitle>
              <CardDescription>
                Upload CSV file containing blacklisted individuals/entities (sanctions, PEPs, watchlists) - sample_blacklist.csv format
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUploadComponent onUpload={setBlacklistFile} />
              {blacklistFile && (
                <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                  ✓ {blacklistFile.name} ready to upload
                </p>
              )}
            </CardContent>
          </Card>

          {/* Threshold Slider */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5" />
                Match Threshold
              </CardTitle>
              <CardDescription>
                Set minimum match score to consider (0-100%). Higher = stricter matching
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Threshold: {threshold}%</label>
                  <span className="text-xs text-muted-foreground">
                    {threshold < 50 ? 'Very Loose' : threshold < 70 ? 'Moderate' : threshold < 85 ? 'Strict' : 'Very Strict'}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={threshold}
                  onChange={(e) => setThreshold(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0% (All)</span>
                  <span>50%</span>
                  <span>100% (Exact)</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Recommended: 70% for balanced screening
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!blacklistFile || isUploading}
              className="min-w-[150px]"
            >
              {isUploading ? (
                <>Processing...</>
              ) : (
                <>
                  <UploadIcon className="mr-2 h-4 w-4" />
                  Upload & Screen
                </>
              )}
            </Button>
          </div>
          
          {/* Helper text */}
          <div className="text-sm text-muted-foreground bg-muted/50 p-4 rounded-lg">
            <p className="font-medium mb-2">📋 How it works:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li><strong>KAMCO Entities (Pre-loaded):</strong> Your KAMCO database (clients, vendors, staff) is already in the system</li>
              <li><strong>Blacklist Upload (Required):</strong> Upload blacklist CSV with sanctions, PEPs, watchlists</li>
              <li><strong>Weighted Matching:</strong> System uses fuzzy matching (Name 40%, Arabic 35%, ID 15%, Nationality 10%)</li>
              <li><strong>Threshold:</strong> Only matches above your set threshold will be shown</li>
              <li><strong>Smart Filtering:</strong> Already-decided cases are automatically skipped</li>
              <li><strong>Results:</strong> Any matches will appear in the Screening Queue for review</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default UploadPage;
