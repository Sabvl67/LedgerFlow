import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { approvalAPI, invoiceAPI, Approval, Invoice } from '../../lib/api';

export default function ApprovalsList() {
  const router = useRouter();
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [invoices, setInvoices] = useState<{ [key: number]: Invoice }>({});
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('pending');

  useEffect(() => {
    loadApprovals();
  }, [statusFilter]);

  const loadApprovals = async () => {
    try {
      const data = await approvalAPI.listApprovals(statusFilter || undefined);
      setApprovals(data);

      // Load invoice details for each approval
      const invoiceIds = [...new Set(data.map((a) => a.invoice_id))];
      const invoiceMap: { [key: number]: Invoice } = {};

      for (const invoiceId of invoiceIds) {
        try {
          const invoice = await invoiceAPI.getInvoice(invoiceId);
          invoiceMap[invoiceId] = invoice;
        } catch (error) {
          console.error(`Failed to load invoice ${invoiceId}`, error);
        }
      }

      setInvoices(invoiceMap);
    } catch (error) {
      console.error('Failed to load approvals', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (approvalId: number) => {
    if (!confirm('Are you sure you want to approve this invoice?')) {
      return;
    }

    try {
      await approvalAPI.updateApproval(approvalId, 'approved');
      loadApprovals();
      alert('Invoice approved successfully!');
    } catch (error) {
      console.error('Failed to approve', error);
      alert('Failed to approve invoice');
    }
  };

  const handleReject = async (approvalId: number) => {
    const comments = prompt('Enter rejection reason:');
    if (!comments) {
      return;
    }

    try {
      await approvalAPI.updateApproval(approvalId, 'rejected', comments);
      loadApprovals();
      alert('Invoice rejected');
    } catch (error) {
      console.error('Failed to reject', error);
      alert('Failed to reject invoice');
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Approval Requests (Role-Based)</h1>
        <button onClick={() => router.push('/')}>Back to Home</button>
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
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        {loading ? (
          <p>Loading approvals...</p>
        ) : approvals.length === 0 ? (
          <p>No approval requests found.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Invoice #</th>
                  <th>Vendor/Customer</th>
                  <th>Amount</th>
                  <th>Required Role</th>
                  <th>Status</th>
                  <th>Comments</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {approvals.map((approval) => {
                  const invoice = invoices[approval.invoice_id];
                  return (
                    <tr key={approval.id}>
                      <td>{approval.id}</td>
                      <td>
                        {invoice?.invoice_number || approval.invoice_id}
                      </td>
                      <td>
                        {invoice?.vendor_name || invoice?.customer_name || '-'}
                      </td>
                      <td>
                        ${invoice?.total_amount?.toFixed(2) || '0.00'}
                      </td>
                      <td>
                        <span className="badge">{approval.required_role}</span>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            approval.status === 'approved'
                              ? 'badge-success'
                              : approval.status === 'rejected'
                              ? 'badge-danger'
                              : 'badge-warning'
                          }`}
                        >
                          {approval.status}
                        </span>
                      </td>
                      <td>{approval.comments || '-'}</td>
                      <td>
                        <button
                          className="small-button"
                          onClick={() =>
                            router.push(`/invoices/${approval.invoice_id}`)
                          }
                        >
                          View
                        </button>
                        {approval.status === 'pending' && (
                          <>
                            <button
                              className="small-button success"
                              onClick={() => handleApprove(approval.id)}
                            >
                              Approve
                            </button>
                            <button
                              className="small-button danger"
                              onClick={() => handleReject(approval.id)}
                            >
                              Reject
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
