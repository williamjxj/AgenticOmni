/**
 * HuggingFace Datasets API client
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const BASE = `${API_BASE_URL}/api/v1/datasets`;

// ── Types ──────────────────────────────────────────────────────────────────

export interface HFDatasetImportRequest {
    dataset_name: string;
    tenant_id: number;
    split: 'train' | 'validation' | 'test';
    limit: number | null;
    user_id: number | null;
}

export interface HFDatasetImportResponse {
    message: string;
    job_id: string;
    dataset_name: string;
    split: string;
    limit: number | null;
}

export interface DatasetValidationResponse {
    dataset_name: string;
    accessible: boolean;
    message: string;
}

export interface SupportedDataset {
    name: string;
    description: string;
    use_case: string;
    size: string;
    recommended_limit: number;
}

export interface SupportedDatasetsResponse {
    supported_datasets: SupportedDataset[];
    tips: string[];
}

// ── API functions ──────────────────────────────────────────────────────────

export async function importHFDataset(
    req: HFDatasetImportRequest
): Promise<HFDatasetImportResponse> {
    const res = await fetch(`${BASE}/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

export async function validateHFDataset(
    datasetName: string
): Promise<DatasetValidationResponse> {
    const encoded = encodeURIComponent(datasetName);
    const res = await fetch(`${BASE}/validate/${encoded}`);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

export async function listSupportedDatasets(): Promise<SupportedDatasetsResponse> {
    const res = await fetch(`${BASE}/supported`);
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}
