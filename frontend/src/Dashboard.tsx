
import React, { useEffect, useState } from 'react';

interface Relayer {
  id: string;
  name: string;
  network: string;
  address: string;
  paused: boolean;
}

interface Transaction {
  id: string;
  status: string;
  hash?: string;
  nonce?: number;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const [relayers, setRelayers] = useState<Relayer[]>([]);
  const [selectedRelayerId, setSelectedRelayerId] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchRelayers();
  }, []);

  useEffect(() => {
    if (selectedRelayerId) {
      fetchTransactions(selectedRelayerId);
    }
  }, [selectedRelayerId]);

  const fetchRelayers = async () => {
    try {
      const response = await fetch('/api/v1/relayers');
      if (response.ok) {
        const data = await response.json();
        setRelayers(data.items || []);
        if (data.items && data.items.length > 0) {
           setSelectedRelayerId(data.items[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch relayers:', error);
    }
  };

  const fetchTransactions = async (relayerId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/relayers/${relayerId}/transactions`);
      if (response.ok) {
        const data = await response.json();
        setTransactions(data.items || []);
      }
    } catch (error) {
       console.error('Failed to fetch transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="sidebar">
        <h2>Relayers</h2>
        <ul>
          {relayers.map((relayer) => (
            <li 
              key={relayer.id} 
              onClick={() => setSelectedRelayerId(relayer.id)}
              className={selectedRelayerId === relayer.id ? 'active' : ''}
            >
              {relayer.name} ({relayer.network})
            </li>
          ))}
        </ul>
      </div>
      <div className="main-content">
        <h1>Relayer Dashboard</h1>
        {selectedRelayerId && (
          <>
            <h2>Transactions for {relayers.find(r => r.id === selectedRelayerId)?.name}</h2>
            {loading ? <p>Loading...</p> : (
              <table className="transaction-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Hash</th>
                    <th>Nonce</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id}>
                      <td>{tx.id}</td>
                      <td>{tx.status}</td>
                      <td>{tx.hash || '-'}</td>
                      <td>{tx.nonce?.toString() || '-'}</td>
                      <td>{new Date(tx.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                  {transactions.length === 0 && <tr><td colSpan={5}>No transactions found</td></tr>}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
