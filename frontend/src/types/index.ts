export type Finding = {
  id: number;
  title: string;
  category: string;
  severity: string;
  confidence: number;
  rule_id: string;
  file_path: string;
  line_number: number;
  snippet: string;
  explanation: string;
  remediation: string;
  cwe?: string;
  policy_rationale: string;
};

export type Scan = {
  id: number;
  scan_type: string;
  source: string;
  status: string;
  recommendation: string;
  summary: {
    total: number;
    severity: Record<string, number>;
    categories: Record<string, number>;
  };
  findings: Finding[];
};

export type ScanSummaryResponse = {
  scan: Scan;
  pr_summary: string;
  comments: string[];
};
