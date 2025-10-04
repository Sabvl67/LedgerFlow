import { useState, FormEvent } from 'react';
import { useRouter } from 'next/router';
import { invoiceAPI } from '../../lib/api';

export default function UploadInvoice() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [invoiceType, setInvoiceType] = useState('accounts_payable');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');
    setResult(null);

    try {
      const response = await invoiceAPI.uploadInvoice(file, invoiceType);
      setResult(response);
      setTimeout(() => {
        router.push(`/invoices/${response.invoice_id}`);
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Upload Invoice</h1>
        <button onClick={() => router.push('/')}>Back to Home</button>
      </header>

      <main className="main">
        <div className="upload-form">
          <h2>Real-Time Invoice Ingestion</h2>
          <p>Upload an invoice for AI-powered OCR extraction (>90% accuracy)</p>

          {error && <div className="error">{error}</div>}
          {result && (
            <div className="success">
              Invoice uploaded successfully! <br />
              Extraction confidence: {(result.extraction_confidence * 100).toFixed(1)}%<br />
              Redirecting to validation...
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="invoiceType">Invoice Type</label>
              <select
                id="invoiceType"
                value={invoiceType}
                onChange={(e) => setInvoiceType(e.target.value)}
                disabled={uploading}
              >
                <option value="accounts_payable">Accounts Payable (AP)</option>
                <option value="accounts_receivable">Accounts Receivable (AR)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="file">Invoice File</label>
              <input
                id="file"
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept="image/*,.pdf"
                disabled={uploading}
                required
              />
              <small>Supported formats: PDF, PNG, JPG</small>
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={uploading || !file}
            >
              {uploading ? 'Processing...' : 'Upload & Extract'}
            </button>
          </form>

          <div className="info-box">
            <h3>How it works:</h3>
            <ol>
              <li>Upload your invoice (PDF or image)</li>
              <li>AWS Textract OCR extracts data automatically</li>
              <li>Review and validate extracted information</li>
              <li>Submit for role-based approval</li>
              <li>Sync to QuickBooks when approved</li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  );
}
