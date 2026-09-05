export interface Citation {
  document_id: string;
  source_name: string;
  page_number: number;
  section: string;
  text: string;
  bbox: [number, number, number, number];
}

export interface StatutoryResponse {
  answer: string;
  citations: Citation[];
  confidence?: "High" | "Medium" | "Low" | "Insufficient";
}

export interface ChatExchange {
  id: string;
  query: string;
  response: StatutoryResponse;
}