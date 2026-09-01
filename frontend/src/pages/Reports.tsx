import { useState, useEffect } from 'react';
import { Download, FileText } from 'lucide-react';

const API_BASE = 'http://localhost:5000/api/v1';

interface Report {
  report_id: string;
  patient_name: string;
  generated_at: string;
  overall_emotion: string;
}

const Reports = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await fetch(`${API_BASE}/reports`);
      const data = await res.json();
      if (data.success) {
        setReports(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch reports');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (reportId: string, format: string) => {
    window.open(`${API_BASE}/reports/${reportId}/download?format=${format}`, '_blank');
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 className="subheader">Generated Clinical Reports</h3>
      
      {loading ? (
        <div className="text-muted">Loading reports...</div>
      ) : reports.length === 0 ? (
        <div className="text-muted">No reports generated yet. Start an assessment to generate one.</div>
      ) : (
        <div style={{ overflowY: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Report ID</th>
                <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Patient Name</th>
                <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Date</th>
                <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Emotion</th>
                <th style={{ padding: '12px 8px', color: 'var(--text-muted)', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map(report => (
                <tr key={report.report_id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '12px 8px' }}>
                    <div className="flex items-center gap-2">
                      <FileText size={16} className="text-accent-blue" />
                      {report.report_id}
                    </div>
                  </td>
                  <td style={{ padding: '12px 8px' }}>{report.patient_name}</td>
                  <td style={{ padding: '12px 8px' }}>{new Date(report.generated_at).toLocaleString()}</td>
                  <td style={{ padding: '12px 8px' }}>{report.overall_emotion}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                    <div className="flex gap-2 justify-center" style={{ justifyContent: 'flex-end' }}>
                      <button 
                        className="btn-primary flex items-center gap-1" 
                        style={{ padding: '6px 10px', fontSize: '12px' }}
                        onClick={() => downloadReport(report.report_id, 'pdf')}
                      >
                        <Download size={14} /> PDF
                      </button>
                      <button 
                        className="btn-outline flex items-center gap-1" 
                        style={{ padding: '6px 10px', fontSize: '12px' }}
                        onClick={() => downloadReport(report.report_id, 'csv')}
                      >
                        CSV
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Reports;
