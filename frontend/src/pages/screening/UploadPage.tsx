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
  const [kamcoFile, setKamcoFile] = useState<File | null>(null);
  const [blacklistFile, setBlacklistFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async () => {
    // Blacklist file is REQUIRED
    if (!blacklistFile) {
      toast.error('Blacklist file is required to start screening');
      return;
    }

    setIsUploading(true);
    try {
      // Upload blacklist file
      const blacklistFormData = new FormData();
      blacklistFormData.append('file', blacklistFile);

      const blacklistResponse = await apiClient.post('/upload/blacklist', blacklistFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!blacklistResponse.data.success) {
        throw new Error('Blacklist upload failed');
      }

      // Backend returns: { success, message, data: { valid_records, stored_count, ... } }
      const uploadData = blacklistResponse.data.data;
      toast.success(`Blacklist uploaded: ${uploadData.stored_count} of ${uploadData.valid_records} records processed`);

      // Upload Kamco file if provided (OPTIONAL)
      if (kamcoFile) {
        // Note: The backend doesn't have a specific kamco upload endpoint yet
        // This is a placeholder for future implementation
        toast('Kamco file upload endpoint coming soon', { icon: 'ℹ️' });
      }

      // Navigate to screening queue
      setTimeout(() => {
        navigate('/screening');
      }, 1500);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6 max-w-4xl mx-auto">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Upload Files</h1>
          <p className="text-muted-foreground">
            Upload blacklist file (required) and optionally Kamco database file for screening
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
                Upload Excel or CSV file containing blacklist data (sanctions, PEPs, watchlists)
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

          {/* Kamco File Upload - OPTIONAL */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5" />
                Kamco Database File
                <span className="ml-2 text-xs font-normal text-muted-foreground bg-muted px-2 py-1 rounded">
                  Optional
                </span>
              </CardTitle>
              <CardDescription>
                Upload Excel or CSV file containing Kamco customer/client data (optional - can screen blacklist only)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUploadComponent onUpload={setKamcoFile} />
              {kamcoFile && (
                <p className="mt-2 text-sm text-green-600 dark:text-green-400">
                  ✓ {kamcoFile.name} ready to upload
                </p>
              )}
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
                  Start Screening
                </>
              )}
            </Button>
          </div>
          
          {/* Helper text */}
          <div className="text-sm text-muted-foreground bg-muted/50 p-4 rounded-lg">
            <p className="font-medium mb-2">📋 How it works:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li><strong>Blacklist file (Required):</strong> Must contain sanctioned entities, PEPs, or watchlist data</li>
              <li><strong>Kamco file (Optional):</strong> If provided, will be screened against the blacklist</li>
              <li><strong>No Kamco file?</strong> You can still upload and manage blacklist data for future screenings</li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default UploadPage;
