import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { authAPI, User } from '../lib/api';

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          router.push('/login');
          return;
        }
        const currentUser = await authAPI.getCurrentUser();
        setUser(currentUser);
        setLoading(false);
      } catch (error) {
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  if (loading) {
    return (
      <div className="container">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <h1>LedgerFlow</h1>
        <div className="user-info">
          <span>{user?.full_name || user?.email}</span>
          <span className="badge">{user?.role}</span>
          <button
            onClick={() => {
              localStorage.removeItem('token');
              router.push('/login');
            }}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="main">
        <h2>AI-Powered AP/AR Workflow</h2>
        <p className="description">
          Real-time invoice ingestion with human-in-loop validation and role-based approvals
        </p>

        <div className="features">
          <div className="feature-card">
            <h3>✓ AWS OCR Integration</h3>
            <p>&gt;90% extraction accuracy on synthetic data</p>
          </div>
          <div className="feature-card">
            <h3>✓ Human-in-the-Loop</h3>
            <p>Validate and correct OCR results</p>
          </div>
          <div className="feature-card">
            <h3>✓ Role-Based Approvals</h3>
            <p>Multi-level approval workflows</p>
          </div>
          <div className="feature-card">
            <h3>✓ QuickBooks Integration</h3>
            <p>Automatic sync when approved</p>
          </div>
        </div>

        <div className="actions">
          <button
            className="primary-button"
            onClick={() => router.push('/invoices/upload')}
          >
            Upload Invoice
          </button>
          <button
            className="secondary-button"
            onClick={() => router.push('/invoices')}
          >
            View Invoices
          </button>
          {(user?.role === 'approver' || user?.role === 'admin') && (
            <button
              className="secondary-button"
              onClick={() => router.push('/approvals')}
            >
              Pending Approvals
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
