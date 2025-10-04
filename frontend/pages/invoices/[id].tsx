import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { invoiceAPI, Invoice, LineItem } from '../../lib/api';

export default function InvoiceDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    if (id) {
      loadInvoice();
    }
  }, [id]);

  const loadInvoice = async () => {
    try {
      const data = await invoiceAPI.getInvoice(Number(id));
      setInvoice(data);
      setFormData(data);
    } catch (error) {
      console.error('Failed to load invoice', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await invoiceAPI.updateInvoice(Number(id), formData);
      setEditing(false);
      loadInvoice();
    } catch (error) {
      console.error('Failed to update invoice', error);
      alert('Failed to update invoice');
    }
  };

  if (loading) {
    return (
      <div className="container">
        <p>Loading...</p>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="container">
        <p>Invoice not found</p>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <h1>Invoice #{invoice.invoice_number || invoice.id}</h1>
        <div>
          {!editing && invoice.status === 'pending_validation' && (
            <button onClick={() => setEditing(true)}>Edit / Validate</button>
          )}
          {editing && (
            <>
              <button onClick={handleSave} className="primary-button">
                Save & Submit for Approval
              </button>
              <button onClick={() => setEditing(false)}>Cancel</button>
            </>
          )}
          <button onClick={() => router.push('/invoices')}>Back to List</button>
        </div>
      </header>

      <main className="main">
        <div className="invoice-detail">
          <div className="section">
            <h2>Invoice Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <label>Status</label>
                <span className="badge">{invoice.status.replace('_', ' ')}</span>
              </div>
              <div className="info-item">
                <label>Type</label>
                <span>{invoice.invoice_type === 'accounts_payable' ? 'Accounts Payable' : 'Accounts Receivable'}</span>
              </div>
              <div className="info-item">
                <label>Extraction Confidence</label>
                <span>
                  {invoice.extraction_confidence
                    ? `${(invoice.extraction_confidence * 100).toFixed(1)}%`
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <div className="section">
            <h2>Details (Human-in-the-Loop Validation)</h2>
            {editing ? (
              <div className="form-grid">
                <div className="form-group">
                  <label>Invoice Number</label>
                  <input
                    type="text"
                    value={formData.invoice_number || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, invoice_number: e.target.value })
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Vendor/Customer Name</label>
                  <input
                    type="text"
                    value={
                      formData.vendor_name ||
                      formData.customer_name ||
                      ''
                    }
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        vendor_name: e.target.value,
                        customer_name: e.target.value,
                      })
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Invoice Date</label>
                  <input
                    type="date"
                    value={formData.invoice_date?.split('T')[0] || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, invoice_date: e.target.value })
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Due Date</label>
                  <input
                    type="date"
                    value={formData.due_date?.split('T')[0] || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, due_date: e.target.value })
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Total Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.total_amount || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        total_amount: parseFloat(e.target.value),
                      })
                    }
                  />
                </div>
                <div className="form-group">
                  <label>Tax Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.tax_amount || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        tax_amount: parseFloat(e.target.value),
                      })
                    }
                  />
                </div>
              </div>
            ) : (
              <div className="info-grid">
                <div className="info-item">
                  <label>Invoice Number</label>
                  <span>{invoice.invoice_number || '-'}</span>
                </div>
                <div className="info-item">
                  <label>Vendor/Customer</label>
                  <span>{invoice.vendor_name || invoice.customer_name || '-'}</span>
                </div>
                <div className="info-item">
                  <label>Invoice Date</label>
                  <span>
                    {invoice.invoice_date
                      ? new Date(invoice.invoice_date).toLocaleDateString()
                      : '-'}
                  </span>
                </div>
                <div className="info-item">
                  <label>Due Date</label>
                  <span>
                    {invoice.due_date
                      ? new Date(invoice.due_date).toLocaleDateString()
                      : '-'}
                  </span>
                </div>
                <div className="info-item">
                  <label>Total Amount</label>
                  <span>${invoice.total_amount?.toFixed(2) || '0.00'}</span>
                </div>
                <div className="info-item">
                  <label>Tax Amount</label>
                  <span>${invoice.tax_amount?.toFixed(2) || '0.00'}</span>
                </div>
              </div>
            )}
          </div>

          <div className="section">
            <h2>Line Items</h2>
            <table>
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Category</th>
                  <th>Quantity</th>
                  <th>Unit Price</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {invoice.line_items.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.description}</td>
                    <td>{item.category || '-'}</td>
                    <td>{item.quantity}</td>
                    <td>${item.unit_price.toFixed(2)}</td>
                    <td>${item.amount.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
