const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  analysis_id: string;
  dataset_stats: {
    rows: number;
    features: number;
    missing: Record<string, number>;
    data_types: Record<string, string>;
  };
  model_type: string;
}

export interface ComputeResponse {
  analysis_id: string;
  status: string;
  sample_index: number;
  techniques: string[];
}

export interface ResultsResponse {
  [key: string]: any;
}

export async function uploadFiles(
  csvFile: File,
  modelFile: File
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('csv_file', csvFile);
  formData.append('model_file', modelFile);

  const response = await fetch(`${API_URL}/api/analyses`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) throw new Error('Upload failed');
  return response.json();
}

export async function computeExplanations(
  analysisId: string,
  techniques: string[],
  sampleIndex: number
): Promise<ComputeResponse> {
  const params = new URLSearchParams();
  techniques.forEach(t => params.append('techniques', t));
  params.append('sample_index', String(sampleIndex));

  const response = await fetch(
    `${API_URL}/api/analyses/${analysisId}/compute?${params}`,
    { method: 'POST' }
  );

  if (!response.ok) throw new Error('Compute failed');
  return response.json();
}

export async function getResults(
  analysisId: string,
  technique: string
): Promise<ResultsResponse> {
  const response = await fetch(
    `${API_URL}/api/analyses/${analysisId}/results/${technique}`
  );

  if (!response.ok) throw new Error(`Failed to fetch ${technique} results`);
  return response.json();
}

export async function pollResults(
  analysisId: string,
  techniques: string[],
  maxWait: number = 60000
): Promise<Record<string, ResultsResponse>> {
  const startTime = Date.now();
  const results: Record<string, ResultsResponse> = {};

  while (Date.now() - startTime < maxWait) {
    let allDone = true;

    for (const technique of techniques) {
      if (results[technique]) continue;

      const result = await getResults(analysisId, technique);
      if (!result.status || result.status !== 'computing') {
        results[technique] = result;
      } else {
        allDone = false;
      }
    }

    if (allDone) return results;
    await new Promise(r => setTimeout(r, 2000)); // Wait 2 seconds before polling again
  }

  return results;
}