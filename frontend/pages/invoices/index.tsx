import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { invoiceAPI, Invoice } from '../../lib/api';

export default function InvoicesList() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadInvoices();
  }, [statusFilter]);

  const loadInvoices = async () => {
    try {
      const data = await invoiceAPI.listInvoices(statusFilter || undefined);
      setInvoices(data);
    } catch (error) {
      console.error('Failed to load invoices', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'approved':
      case 'synced':
        return 'badge-success';
      case 'rejected':
        return 'badge-danger';
      case 'pending_validation':
        return 'badge-warning';
      default:
        return 'badge-info';
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Invoices</h1>
        <div>
          <button onClick={() => router.push('/invoices/upload')}>Upload New</button>
          <button onClick={() => router.push('/')}>Back to Home</button>
        </div>
      </header>

      <main className="main">
        <div className="filters">
          <label htmlFor="statusFilter">Filter by Status:</label>
          <select
            id="statusFilter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All</option>
            <option value="pending_extraction">Pending Extraction</option>
            <option value="pending_validation">Pending Validation</option>
            <option value="pending_approval">Pending Approval</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="synced">Synced</option>
          </select>
        </div>

        {loading ? (
          <p>Loading invoices...</p>
        ) : invoices.length === 0 ? (
          <p>No invoices found.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Invoice #</th>
                  <th>Type</th>
                  <th>Vendor/Customer</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Confidence</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>{invoice.id}</td>
                    <td>{invoice.invoice_number || '-'}</td>
                    <td>{invoice.invoice_type === 'accounts_payable' ? 'AP' : 'AR'}</td>
                    <td>{invoice.vendor_name || invoice.customer_name || '-'}</td>
                    <td>${invoice.total_amount?.toFixed(2) || '0.00'}</td>
                    <td>
                      <span className={`badge ${getStatusBadgeClass(invoice.status)}`}>
                        {invoice.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      {invoice.extraction_confidence
                        ? `${(invoice.extraction_confidence * 100).toFixed(1)}%`
                        : '-'}
                    </td>
                    <td>{new Date(invoice.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="small-button"
                        onClick={() => router.push(`/invoices/${invoice.id}`)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
