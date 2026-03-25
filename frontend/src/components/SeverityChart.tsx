import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from 'recharts';

export function SeverityChart({ severity }: { severity: Record<string, number> }) {
  const data = Object.entries(severity).map(([name, value]) => ({ name, value }));
  return (
    <div className="card h-64">
      <h3 className="font-semibold mb-2">Severity Distribution</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Bar dataKey="value" fill="#06b6d4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
