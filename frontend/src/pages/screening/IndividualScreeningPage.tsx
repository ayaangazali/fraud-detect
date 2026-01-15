import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import { 
  Search, 
  User, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Loader2,
  FileText,
  Shield,
  CreditCard,
  Globe,
  Calendar,
  Building,
  UserCheck,
  AlertCircle
} from 'lucide-react';
import apiClient from '@/services/apiClient';

interface ScreenMatch {
  kamco_entity_id: number;
  kamco_customer_id: string | null;
  kamco_name: string;
  kamco_name_arabic: string | null;
  kamco_type: string;
  kamco_civil_id: string | null;
  kamco_passport: string | null;
  kamco_nationality: string | null;
  kamco_category: string | null;
  kamco_risk_level: string | null;
  kamco_account_status: string | null;
  match_score: number;
  match_percentage: string;
  match_reasons: string[];
  risk_level: string;
}

interface ScreeningResult {
  success: boolean;
  query: {
    name_english: string;
    name_arabic: string | null;
    civil_id: string | null;
    passport_number: string | null;
    nationality: string | null;
    date_of_birth: string | null;
    notes: string | null;
  };
  total_matches: number;
  matches: ScreenMatch[];
  screened_at: string;
  screened_by: string;
  message: string;
}

const IndividualScreeningPage: React.FC = () => {
  const [formData, setFormData] = useState({
    name_english: '',
    name_arabic: '',
    civil_id: '',
    passport_number: '',
    nationality: '',
    date_of_birth: '',
    notes: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name_english.trim()) {
      setError('Please enter at least an English name to search');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await apiClient.post('/screening/v2/individual-screen', {
        name_english: formData.name_english.trim(),
        name_arabic: formData.name_arabic.trim() || null,
        civil_id: formData.civil_id.trim() || null,
        passport_number: formData.passport_number.trim() || null,
        nationality: formData.nationality.trim() || null,
        date_of_birth: formData.date_of_birth || null,
        notes: formData.notes.trim() || null
      });
      
      setResult(response.data);
    } catch (err: any) {
      console.error('Screening error:', err);
      setError(err.response?.data?.detail || 'Failed to perform screening. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setFormData({
      name_english: '',
      name_arabic: '',
      civil_id: '',
      passport_number: '',
      nationality: '',
      date_of_birth: '',
      notes: ''
    });
    setResult(null);
    setError(null);
  };

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'CRITICAL':
        return 'bg-red-600 text-white';
      case 'HIGH':
        return 'bg-orange-500 text-white';
      case 'MEDIUM':
        return 'bg-yellow-500 text-black';
      case 'LOW':
        return 'bg-blue-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.95) return 'text-red-600 font-bold';
    if (score >= 0.85) return 'text-orange-500 font-semibold';
    if (score >= 0.75) return 'text-yellow-600';
    return 'text-blue-500';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Search className="h-6 w-6 text-blue-600" />
              Individual Screening
            </h1>
            <p className="text-muted-foreground mt-1">
              Check a person against the Kamco database for potential matches
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Search Form - Left Side */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Person Details
                </CardTitle>
                <CardDescription>
                  Enter the details of the person you want to screen against Kamco database
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Name English - Required */}
                  <div className="space-y-2">
                    <Label htmlFor="name_english" className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      Name (English) <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="name_english"
                      name="name_english"
                      value={formData.name_english}
                      onChange={handleInputChange}
                      placeholder="e.g., Mohammed Ahmed Al-Rashid"
                      required
                    />
                  </div>

                  {/* Name Arabic */}
                  <div className="space-y-2">
                    <Label htmlFor="name_arabic" className="flex items-center gap-1">
                      <User className="h-4 w-4" />
                      Name (Arabic)
                    </Label>
                    <Input
                      id="name_arabic"
                      name="name_arabic"
                      value={formData.name_arabic}
                      onChange={handleInputChange}
                      placeholder="محمد أحمد الراشد"
                      dir="rtl"
                    />
                  </div>

                  {/* Civil ID */}
                  <div className="space-y-2">
                    <Label htmlFor="civil_id" className="flex items-center gap-1">
                      <CreditCard className="h-4 w-4" />
                      Civil ID
                    </Label>
                    <Input
                      id="civil_id"
                      name="civil_id"
                      value={formData.civil_id}
                      onChange={handleInputChange}
                      placeholder="e.g., 123456789012"
                    />
                  </div>

                  {/* Passport Number */}
                  <div className="space-y-2">
                    <Label htmlFor="passport_number" className="flex items-center gap-1">
                      <FileText className="h-4 w-4" />
                      Passport Number
                    </Label>
                    <Input
                      id="passport_number"
                      name="passport_number"
                      value={formData.passport_number}
                      onChange={handleInputChange}
                      placeholder="e.g., A12345678"
                    />
                  </div>

                  {/* Nationality */}
                  <div className="space-y-2">
                    <Label htmlFor="nationality" className="flex items-center gap-1">
                      <Globe className="h-4 w-4" />
                      Nationality
                    </Label>
                    <Input
                      id="nationality"
                      name="nationality"
                      value={formData.nationality}
                      onChange={handleInputChange}
                      placeholder="e.g., Kuwaiti"
                    />
                  </div>

                  {/* Date of Birth */}
                  <div className="space-y-2">
                    <Label htmlFor="date_of_birth" className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      Date of Birth
                    </Label>
                    <Input
                      id="date_of_birth"
                      name="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={handleInputChange}
                    />
                  </div>

                  {/* Notes */}
                  <div className="space-y-2">
                    <Label htmlFor="notes">Additional Notes</Label>
                    <Textarea
                      id="notes"
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      placeholder="Any additional information about this person..."
                      rows={2}
                    />
                  </div>

                  {/* Error Message */}
                  {error && (
                    <Alert variant="destructive">
                      <XCircle className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-3 pt-2">
                    <Button 
                      type="submit" 
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Screening...
                        </>
                      ) : (
                        <>
                          <Search className="mr-2 h-4 w-4" />
                          Screen Person
                        </>
                      )}
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline"
                      onClick={handleClear}
                      disabled={isLoading}
                    >
                      Clear
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Results Section - Right Side */}
          <div className="lg:col-span-3 space-y-4">
            {/* Results Header */}
            {result && (
              <Card className={result.total_matches > 0 ? 'border-orange-300' : 'border-green-300'}>
                <CardHeader className={
                  result.total_matches > 0 
                    ? 'bg-orange-50' 
                    : 'bg-green-50'
                }>
                  <CardTitle className="flex items-center gap-2">
                    {result.total_matches > 0 ? (
                      <>
                        <AlertTriangle className="h-5 w-5 text-orange-600" />
                        <span className="text-orange-700">
                          {result.total_matches} Potential Match{result.total_matches !== 1 ? 'es' : ''} Found
                        </span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-green-700">No Matches Found - Clear</span>
                      </>
                    )}
                  </CardTitle>
                  <CardDescription>
                    Screened by {result.screened_by} at {new Date(result.screened_at).toLocaleString()}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="text-sm space-y-1">
                    <p><strong>Searched:</strong> {result.query.name_english}</p>
                    {result.query.civil_id && <p><strong>Civil ID:</strong> {result.query.civil_id}</p>}
                    {result.query.passport_number && <p><strong>Passport:</strong> {result.query.passport_number}</p>}
                    {result.query.nationality && <p><strong>Nationality:</strong> {result.query.nationality}</p>}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Match Results */}
            {result && result.matches.length > 0 && (
              <div className="space-y-3">
                <h3 className="font-semibold text-lg flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-orange-500" />
                  Matching Kamco Records
                </h3>
                {result.matches.map((match) => (
                  <Card key={match.kamco_entity_id} className="border-l-4 border-l-orange-500">
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-semibold text-lg flex items-center gap-2">
                            <Building className="h-4 w-4" />
                            {match.kamco_name}
                          </h4>
                          {match.kamco_name_arabic && (
                            <p className="text-gray-600" dir="rtl">{match.kamco_name_arabic}</p>
                          )}
                          {match.kamco_customer_id && (
                            <p className="text-sm text-muted-foreground">ID: {match.kamco_customer_id}</p>
                          )}
                        </div>
                        <div className="flex gap-2 flex-wrap justify-end">
                          <Badge className={getRiskBadgeColor(match.risk_level)}>
                            {match.risk_level} RISK
                          </Badge>
                          <Badge variant="outline" className={getScoreColor(match.match_score)}>
                            {match.match_percentage} Match
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm mb-3">
                        <div>
                          <span className="text-muted-foreground">Type:</span>{' '}
                          <Badge variant="secondary">{match.kamco_type}</Badge>
                        </div>
                        {match.kamco_civil_id && (
                          <div>
                            <span className="text-muted-foreground">Civil ID:</span>{' '}
                            <span className="font-mono">{match.kamco_civil_id}</span>
                          </div>
                        )}
                        {match.kamco_passport && (
                          <div>
                            <span className="text-muted-foreground">Passport:</span>{' '}
                            <span className="font-mono">{match.kamco_passport}</span>
                          </div>
                        )}
                        {match.kamco_nationality && (
                          <div>
                            <span className="text-muted-foreground">Nationality:</span>{' '}
                            <span>{match.kamco_nationality}</span>
                          </div>
                        )}
                        {match.kamco_category && (
                          <div>
                            <span className="text-muted-foreground">Category:</span>{' '}
                            <span>{match.kamco_category}</span>
                          </div>
                        )}
                        {match.kamco_account_status && (
                          <div>
                            <span className="text-muted-foreground">Status:</span>{' '}
                            <Badge variant={match.kamco_account_status === 'active' ? 'default' : 'secondary'}>
                              {match.kamco_account_status}
                            </Badge>
                          </div>
                        )}
                      </div>

                      {/* Match Reasons */}
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                          <Shield className="h-4 w-4" />
                          Why This Matched:
                        </p>
                        <ul className="text-sm space-y-1">
                          {match.match_reasons.map((reason, i) => (
                            <li key={i} className="flex items-center gap-2">
                              <span className="w-1.5 h-1.5 bg-orange-500 rounded-full flex-shrink-0"></span>
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* No Results Yet State */}
            {!result && !isLoading && (
              <Card className="border-dashed">
                <CardContent className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                  <UserCheck className="h-16 w-16 mb-4 opacity-30" />
                  <p className="text-lg font-medium">Enter person details to screen</p>
                  <p className="text-sm">Results will appear here after screening</p>
                  <p className="text-xs mt-4 text-center max-w-md">
                    This tool checks if a person (e.g., from a blacklist) has any matching records 
                    in the Kamco database including clients, vendors, staff, and other entities.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Loading State */}
            {isLoading && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <Loader2 className="h-12 w-12 animate-spin text-blue-600 mb-4" />
                  <p className="text-lg font-medium">Screening in progress...</p>
                  <p className="text-sm text-muted-foreground">Checking against Kamco database</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default IndividualScreeningPage;
