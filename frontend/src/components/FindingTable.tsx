import type { Finding } from '../types';

export function FindingTable({ findings, onSelect }: { findings: Finding[]; onSelect: (f: Finding) => void }) {
  return (
    <div className="card overflow-auto">
      <h3 className="font-semibold mb-2">Findings</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left border-b border-slate-700">
            <th>Severity</th><th>Title</th><th>File</th><th>Line</th><th>Category</th>
          </tr>
        </thead>
        <tbody>
          {findings.map((f) => (
            <tr key={f.id} className="border-b border-slate-800 cursor-pointer" onClick={() => onSelect(f)}>
              <td>{f.severity}</td><td>{f.title}</td><td>{f.file_path}</td><td>{f.line_number}</td><td>{f.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
