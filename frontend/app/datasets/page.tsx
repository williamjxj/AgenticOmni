'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
    ArrowLeft,
    Database,
    Download,
    CheckCircle2,
    XCircle,
    Loader2,
    AlertCircle,
    ChevronRight,
    Sparkles,
    BookOpen,
    FlaskConical,
    BrainCircuit,
    Globe,
    FileText,
    Clock,
    Hash,
    Layers,
    ExternalLink,
    RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import {
    importHFDataset,
    validateHFDataset,
    listSupportedDatasets,
    type HFDatasetImportResponse,
    type SupportedDataset,
} from '@/lib/api/datasets';

// ── Helpers ────────────────────────────────────────────────────────────────

const USE_CASE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
    'QA over documents': BookOpen,
    'Document visual QA': FileText,
    'Scientific document RAG': FlaskConical,
    'General QA': BrainCircuit,
    'Multi-doc dialogue': Layers,
    'General knowledge RAG': Globe,
};

const USE_CASE_COLORS: Record<string, string> = {
    'QA over documents': 'from-blue-500 to-blue-600',
    'Document visual QA': 'from-purple-500 to-purple-600',
    'Scientific document RAG': 'from-green-500 to-green-600',
    'General QA': 'from-orange-500 to-orange-600',
    'Multi-doc dialogue': 'from-pink-500 to-pink-600',
    'General knowledge RAG': 'from-teal-500 to-teal-600',
};

const BADGE_COLORS: Record<string, string> = {
    'QA over documents': 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
    'Document visual QA': 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
    'Scientific document RAG': 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
    'General QA': 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
    'Multi-doc dialogue': 'bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-300',
    'General knowledge RAG': 'bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300',
};

// ── Sub-components ─────────────────────────────────────────────────────────

interface ImportJob {
    jobId: string;
    datasetName: string;
    split: string;
    limit: number | null;
    startedAt: string;
    status: 'queued' | 'running';
}

function JobToast({ job }: { job: ImportJob }) {
    return (
        <div className="flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm dark:border-blue-800 dark:bg-blue-950/40">
            <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-blue-600 dark:text-blue-400" />
            <div className="flex-1 min-w-0">
                <p className="font-medium text-blue-900 dark:text-blue-100 truncate">
                    Importing <span className="font-mono">{job.datasetName}</span>
                </p>
                <p className="text-blue-600 dark:text-blue-400 mt-0.5">
                    Split: {job.split} · {job.limit ? `${job.limit} records` : 'all records'} ·{' '}
                    <span className="font-mono text-xs">job {job.jobId.substring(0, 8)}…</span>
                </p>
            </div>
            <span className="text-xs text-blue-500 shrink-0">{job.startedAt}</span>
        </div>
    );
}

interface DatasetCardProps {
    dataset: SupportedDataset;
    onImport: (dataset: SupportedDataset) => void;
    isImporting: boolean;
}

function DatasetCard({ dataset, onImport, isImporting }: DatasetCardProps) {
    const [validating, setValidating] = useState(false);
    const [validation, setValidation] = useState<{
        checked: boolean;
        accessible: boolean;
    } | null>(null);

    const Icon = USE_CASE_ICONS[dataset.use_case] ?? Database;
    const gradient = USE_CASE_COLORS[dataset.use_case] ?? 'from-slate-500 to-slate-600';
    const badge = BADGE_COLORS[dataset.use_case] ?? 'bg-slate-100 text-slate-700';

    const handleValidate = useCallback(async () => {
        setValidating(true);
        try {
            const result = await validateHFDataset(dataset.name);
            setValidation({ checked: true, accessible: result.accessible });
        } catch {
            setValidation({ checked: true, accessible: false });
        } finally {
            setValidating(false);
        }
    }, [dataset.name]);

    return (
        <Card className="group relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5 border border-slate-200 dark:border-slate-700">
            {/* Gradient accent bar */}
            <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${gradient}`} />

            <CardHeader className="pb-3 pt-5">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                        <div className={`rounded-lg bg-gradient-to-br ${gradient} p-2.5 text-white shadow-sm`}>
                            <Icon className="h-5 w-5" />
                        </div>
                        <div className="min-w-0">
                            <CardTitle className="text-base leading-tight">{dataset.description}</CardTitle>
                            <div className="mt-1.5 flex items-center gap-2 flex-wrap">
                                <code className="rounded bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 text-xs font-mono text-slate-600 dark:text-slate-300">
                                    {dataset.name}
                                </code>
                                <a
                                    href={`https://huggingface.co/datasets/${dataset.name}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-blue-500 transition-colors"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <ExternalLink className="h-3 w-3" />
                                    HF Hub
                                </a>
                            </div>
                        </div>
                    </div>

                    {validation?.checked && (
                        <div className="shrink-0">
                            {validation.accessible ? (
                                <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
                                    <CheckCircle2 className="h-3.5 w-3.5" />
                                    Accessible
                                </span>
                            ) : (
                                <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 px-2.5 py-1 text-xs font-medium text-red-700 dark:bg-red-900/40 dark:text-red-300">
                                    <XCircle className="h-3.5 w-3.5" />
                                    Not accessible
                                </span>
                            )}
                        </div>
                    )}
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                <div className="flex items-center flex-wrap gap-2 text-xs">
                    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-medium ${badge}`}>
                        <Sparkles className="h-3 w-3" />
                        {dataset.use_case}
                    </span>
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 dark:bg-slate-800 px-2.5 py-1 font-medium text-slate-600 dark:text-slate-300">
                        <Hash className="h-3 w-3" />
                        {dataset.size}
                    </span>
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 dark:bg-slate-800 px-2.5 py-1 font-medium text-slate-600 dark:text-slate-300">
                        <Layers className="h-3 w-3" />
                        Limit {dataset.recommended_limit.toLocaleString()}
                    </span>
                </div>

                <div className="flex gap-2 pt-1">
                    <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={handleValidate}
                        disabled={validating}
                        id={`validate-${dataset.name.replace(/\//g, '-')}`}
                    >
                        {validating ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                            <CheckCircle2 className="h-3.5 w-3.5" />
                        )}
                        {validating ? 'Checking…' : 'Validate'}
                    </Button>
                    <Button
                        size="sm"
                        className="flex-[2] text-xs"
                        onClick={() => onImport(dataset)}
                        disabled={isImporting || (validation?.checked && !validation?.accessible)}
                        id={`import-${dataset.name.replace(/\//g, '-')}`}
                    >
                        {isImporting ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                            <Download className="h-3.5 w-3.5" />
                        )}
                        Import ({dataset.recommended_limit.toLocaleString()} recs)
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}

// ── Import Modal ─────────────────────────────────────────────────────────

interface ImportModalProps {
    dataset: SupportedDataset | null;
    onClose: () => void;
    onConfirm: (
        datasetName: string,
        split: 'train' | 'validation' | 'test',
        limit: number | null
    ) => Promise<void>;
}

function ImportModal({ dataset, onClose, onConfirm }: ImportModalProps) {
    const [split, setSplit] = useState<'train' | 'validation' | 'test'>('train');
    const [limitMode, setLimitMode] = useState<'recommended' | 'custom' | 'all'>('recommended');
    const [customLimit, setCustomLimit] = useState('100');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!dataset) return null;

    const resolvedLimit =
        limitMode === 'recommended'
            ? dataset.recommended_limit
            : limitMode === 'custom'
                ? parseInt(customLimit, 10) || 100
                : null;

    const handleConfirm = async () => {
        setSubmitting(true);
        setError(null);
        try {
            await onConfirm(dataset.name, split, resolvedLimit);
            onClose();
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Import failed');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
            onClick={(e) => e.target === e.currentTarget && onClose()}
        >
            <div className="w-full max-w-md rounded-2xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-700">
                {/* Header */}
                <div className="flex items-center gap-3 border-b border-slate-200 dark:border-slate-700 px-6 py-4">
                    <div className="rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 p-2 text-white">
                        <Download className="h-5 w-5" />
                    </div>
                    <div>
                        <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                            Configure Import
                        </h2>
                        <p className="text-xs text-slate-500 font-mono mt-0.5">{dataset.name}</p>
                    </div>
                </div>

                <div className="px-6 py-5 space-y-5">
                    {/* Split selector */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Dataset Split
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                            {(['train', 'validation', 'test'] as const).map((s) => (
                                <button
                                    key={s}
                                    onClick={() => setSplit(s)}
                                    className={`rounded-lg border py-2 text-sm font-medium transition-all ${split === s
                                            ? 'border-blue-500 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-950/50 dark:text-blue-300'
                                            : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-600'
                                        }`}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Limit selector */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Record Limit
                        </label>
                        <div className="space-y-2">
                            {[
                                {
                                    key: 'recommended',
                                    label: `Recommended (${dataset.recommended_limit.toLocaleString()})`,
                                    desc: 'Best for initial testing',
                                },
                                { key: 'custom', label: 'Custom limit', desc: 'Set your own number' },
                                { key: 'all', label: 'All records', desc: 'May take a long time' },
                            ].map(({ key, label, desc }) => (
                                <label
                                    key={key}
                                    className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition-all ${limitMode === key
                                            ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950/50'
                                            : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                                        }`}
                                >
                                    <input
                                        type="radio"
                                        className="mt-0.5 accent-blue-600"
                                        checked={limitMode === key}
                                        onChange={() => setLimitMode(key as typeof limitMode)}
                                    />
                                    <div>
                                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                                            {label}
                                        </p>
                                        <p className="text-xs text-slate-500">{desc}</p>
                                    </div>
                                </label>
                            ))}
                        </div>

                        {limitMode === 'custom' && (
                            <div className="mt-3">
                                <input
                                    type="number"
                                    min="1"
                                    max="10000"
                                    value={customLimit}
                                    onChange={(e) => setCustomLimit(e.target.value)}
                                    className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                                    placeholder="Enter record count (max 10,000)"
                                />
                            </div>
                        )}
                    </div>

                    {/* Summary */}
                    <div className="rounded-lg bg-slate-50 dark:bg-slate-800 p-3 text-xs space-y-1.5">
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Dataset</span>
                            <span className="font-mono text-slate-800 dark:text-slate-200">{dataset.name}</span>
                        </div>
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Split</span>
                            <span className="font-mono text-slate-800 dark:text-slate-200">{split}</span>
                        </div>
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Records</span>
                            <span className="font-mono text-slate-800 dark:text-slate-200">
                                {resolvedLimit ? resolvedLimit.toLocaleString() : 'all'}
                            </span>
                        </div>
                    </div>

                    {error && (
                        <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/40 px-3 py-2 text-sm text-red-700 dark:text-red-300">
                            <AlertCircle className="h-4 w-4 shrink-0" />
                            {error}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex gap-3 border-t border-slate-200 dark:border-slate-700 px-6 py-4">
                    <Button variant="outline" className="flex-1" onClick={onClose} disabled={submitting}>
                        Cancel
                    </Button>
                    <Button
                        className="flex-[2] bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                        onClick={handleConfirm}
                        disabled={submitting}
                    >
                        {submitting ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Starting import…
                            </>
                        ) : (
                            <>
                                <Download className="h-4 w-4" />
                                Start Import
                            </>
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
}

// ── Custom dataset form ───────────────────────────────────────────────────

interface CustomImportFormProps {
    onImport: (
        datasetName: string,
        split: 'train' | 'validation' | 'test',
        limit: number | null
    ) => Promise<void>;
}

function CustomImportForm({ onImport }: CustomImportFormProps) {
    const [datasetName, setDatasetName] = useState('');
    const [split, setSplit] = useState<'train' | 'validation' | 'test'>('train');
    const [limit, setLimit] = useState('500');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!datasetName.trim()) return;
        setSubmitting(true);
        setError(null);
        try {
            await onImport(datasetName.trim(), split, parseInt(limit, 10) || 500);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Import failed');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                    Dataset identifier
                </label>
                <input
                    type="text"
                    value={datasetName}
                    onChange={(e) => setDatasetName(e.target.value)}
                    placeholder="e.g. rajpurkar/squad or wikitext"
                    className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    required
                />
            </div>

            <div className="grid grid-cols-2 gap-3">
                <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                        Split
                    </label>
                    <select
                        value={split}
                        onChange={(e) => setSplit(e.target.value as typeof split)}
                        className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    >
                        <option value="train">train</option>
                        <option value="validation">validation</option>
                        <option value="test">test</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                        Record limit
                    </label>
                    <input
                        type="number"
                        min="1"
                        max="10000"
                        value={limit}
                        onChange={(e) => setLimit(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm text-slate-900 dark:text-slate-100 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                    />
                </div>
            </div>

            {error && (
                <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/40 px-3 py-2 text-sm text-red-700 dark:text-red-300">
                    <AlertCircle className="h-4 w-4 shrink-0" />
                    {error}
                </div>
            )}

            <Button type="submit" className="w-full" disabled={submitting || !datasetName.trim()}>
                {submitting ? (
                    <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Starting import…
                    </>
                ) : (
                    <>
                        <Download className="h-4 w-4" />
                        Import Dataset
                    </>
                )}
            </Button>
        </form>
    );
}

// ── Main Page ─────────────────────────────────────────────────────────────

export default function DatasetsPage() {
    const [datasets, setDatasets] = useState<SupportedDataset[]>([]);
    const [tips, setTips] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);
    const [selectedDataset, setSelectedDataset] = useState<SupportedDataset | null>(null);
    const [activeJobs, setActiveJobs] = useState<ImportJob[]>([]);
    const [importingName, setImportingName] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    // Load supported datasets on mount
    useEffect(() => {
        (async () => {
            try {
                const data = await listSupportedDatasets();
                setDatasets(data.supported_datasets);
                setTips(data.tips);
            } catch (e) {
                setLoadError(e instanceof Error ? e.message : 'Failed to load datasets');
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    const handleImport = useCallback(
        async (
            datasetName: string,
            split: 'train' | 'validation' | 'test',
            limit: number | null
        ) => {
            setImportingName(datasetName);
            try {
                const result: HFDatasetImportResponse = await importHFDataset({
                    dataset_name: datasetName,
                    tenant_id: 1,
                    split,
                    limit,
                    user_id: 1,
                });

                const job: ImportJob = {
                    jobId: result.job_id,
                    datasetName: result.dataset_name,
                    split: result.split,
                    limit: result.limit,
                    startedAt: new Date().toLocaleTimeString(),
                    status: 'queued',
                };

                setActiveJobs((prev) => [job, ...prev]);
                setSuccessMessage(
                    `Import started for "${datasetName}" — Job ID: ${result.job_id.substring(0, 12)}…`
                );
                setTimeout(() => setSuccessMessage(null), 6000);
            } finally {
                setImportingName(null);
            }
        },
        []
    );

    const handleCardImport = useCallback((dataset: SupportedDataset) => {
        setSelectedDataset(dataset);
    }, []);

    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
            {/* Header */}
            <header className="sticky top-0 z-40 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
                <div className="container mx-auto px-4 py-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Button variant="ghost" size="sm" asChild>
                                <Link href="/">
                                    <ArrowLeft className="h-4 w-4 mr-1.5" />
                                    Back
                                </Link>
                            </Button>
                            <div className="flex items-center gap-2.5">
                                <div className="rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 p-1.5 text-white">
                                    <Database className="h-4 w-4" />
                                </div>
                                <div>
                                    <h1 className="text-lg font-bold text-slate-900 dark:text-slate-100 leading-none">
                                        HuggingFace Datasets
                                    </h1>
                                    <p className="text-xs text-slate-500 mt-0.5">Import datasets into your RAG pipeline</p>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" size="sm" asChild>
                                <Link href="/documents">
                                    <FileText className="h-4 w-4 mr-1.5" />
                                    View Documents
                                </Link>
                            </Button>
                            <Button variant="outline" size="sm" asChild>
                                <Link href="/search">
                                    <ChevronRight className="h-4 w-4 mr-1.5" />
                                    Search
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8 max-w-7xl">
                {/* Success banner */}
                {successMessage && (
                    <div className="mb-6 flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950/40 px-4 py-3 text-sm text-green-800 dark:text-green-200">
                        <CheckCircle2 className="h-5 w-5 shrink-0 text-green-600 dark:text-green-400" />
                        <p>{successMessage}</p>
                    </div>
                )}

                {/* Active jobs */}
                {activeJobs.length > 0 && (
                    <div className="mb-6 space-y-2">
                        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                            <Clock className="h-4 w-4" />
                            Active Import Jobs ({activeJobs.length})
                            <Button
                                variant="ghost"
                                size="sm"
                                className="ml-auto h-7 text-xs"
                                onClick={() => setActiveJobs([])}
                            >
                                <RefreshCw className="h-3 w-3 mr-1" />
                                Clear
                            </Button>
                        </div>
                        {activeJobs.map((job) => (
                            <JobToast key={job.jobId} job={job} />
                        ))}
                    </div>
                )}

                <div className="grid gap-8 xl:grid-cols-[1fr_340px]">
                    {/* Left — dataset grid */}
                    <div className="space-y-6">
                        {/* Hero banner */}
                        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700 px-8 py-8 text-white shadow-lg">
                            {/* Decorative circles */}
                            <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-white/5" />
                            <div className="pointer-events-none absolute -bottom-8 -left-8 h-48 w-48 rounded-full bg-white/5" />

                            <div className="relative">
                                <div className="flex items-center gap-2 mb-3">
                                    <BrainCircuit className="h-5 w-5 text-blue-200" />
                                    <span className="text-sm font-medium text-blue-200">AgenticOmni × HuggingFace Hub</span>
                                </div>
                                <h2 className="text-2xl font-bold mb-2">Import Training Data</h2>
                                <p className="text-blue-100 max-w-xl text-sm leading-relaxed">
                                    Pull datasets directly from HuggingFace Hub, auto-chunk them into 512-token
                                    segments, generate embeddings, and make them instantly searchable in your RAG
                                    pipeline — all in one click.
                                </p>
                                <div className="mt-5 flex flex-wrap gap-4 text-sm">
                                    {[
                                        { label: '512-token chunks', icon: Layers },
                                        { label: 'Deduplication', icon: Hash },
                                        { label: 'Background job', icon: Clock },
                                        { label: 'pgvector storage', icon: Database },
                                    ].map(({ label, icon: I }) => (
                                        <span key={label} className="flex items-center gap-1.5 text-blue-100">
                                            <I className="h-4 w-4 text-blue-300" />
                                            {label}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Supported datasets grid */}
                        <div>
                            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">
                                Supported Datasets
                            </h2>

                            {loading && (
                                <div className="grid sm:grid-cols-2 gap-4">
                                    {Array.from({ length: 6 }).map((_, i) => (
                                        <div
                                            key={i}
                                            className="h-52 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"
                                        />
                                    ))}
                                </div>
                            )}

                            {loadError && (
                                <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/40 p-4 text-sm text-red-700 dark:text-red-300">
                                    <AlertCircle className="h-5 w-5 shrink-0" />
                                    <div>
                                        <p className="font-medium">Failed to load datasets</p>
                                        <p className="text-xs mt-0.5 opacity-80">{loadError}</p>
                                        <p className="text-xs mt-1 opacity-60">
                                            Make sure the API server is running at{' '}
                                            {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {!loading && !loadError && (
                                <div className="grid sm:grid-cols-2 gap-4">
                                    {datasets.map((ds) => (
                                        <DatasetCard
                                            key={ds.name}
                                            dataset={ds}
                                            onImport={handleCardImport}
                                            isImporting={importingName === ds.name}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right — sidebar */}
                    <div className="space-y-6">
                        {/* Custom import form */}
                        <Card className="border-slate-200 dark:border-slate-700">
                            <CardHeader className="pb-3">
                                <div className="flex items-center gap-2">
                                    <div className="rounded-md bg-gradient-to-br from-orange-500 to-rose-600 p-1.5 text-white">
                                        <Database className="h-4 w-4" />
                                    </div>
                                    <CardTitle className="text-base">Custom Dataset</CardTitle>
                                </div>
                                <CardDescription className="text-xs">
                                    Import any HuggingFace Hub dataset by its identifier
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <CustomImportForm onImport={handleImport} />
                            </CardContent>
                        </Card>

                        {/* Pipeline steps */}
                        <Card className="border-slate-200 dark:border-slate-700">
                            <CardHeader className="pb-3">
                                <CardTitle className="text-base flex items-center gap-2">
                                    <Sparkles className="h-4 w-4 text-purple-500" />
                                    Import Pipeline
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ol className="space-y-3">
                                    {[
                                        { step: '1', label: 'Load from HuggingFace Hub', color: 'bg-blue-500' },
                                        { step: '2', label: 'Create document records', color: 'bg-indigo-500' },
                                        { step: '3', label: 'Chunk text (512 tokens)', color: 'bg-violet-500' },
                                        { step: '4', label: 'Generate embeddings', color: 'bg-purple-500' },
                                        { step: '5', label: 'Store in pgvector', color: 'bg-fuchsia-500' },
                                        { step: '6', label: 'Ready for search & RAG', color: 'bg-pink-500' },
                                    ].map(({ step, label, color }) => (
                                        <li key={step} className="flex items-center gap-3 text-sm">
                                            <span
                                                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${color} text-[11px] font-bold text-white`}
                                            >
                                                {step}
                                            </span>
                                            <span className="text-slate-600 dark:text-slate-400">{label}</span>
                                        </li>
                                    ))}
                                </ol>
                            </CardContent>
                        </Card>

                        {/* Tips */}
                        {tips.length > 0 && (
                            <Card className="border-slate-200 dark:border-slate-700">
                                <CardHeader className="pb-3">
                                    <CardTitle className="text-base flex items-center gap-2">
                                        <AlertCircle className="h-4 w-4 text-amber-500" />
                                        Tips
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ul className="space-y-2">
                                        {tips.map((tip, i) => (
                                            <li key={i} className="flex items-start gap-2 text-xs text-slate-600 dark:text-slate-400">
                                                <span className="mt-0.5 h-4 w-4 shrink-0 rounded-full bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center text-amber-700 dark:text-amber-300 font-bold">
                                                    {i + 1}
                                                </span>
                                                {tip}
                                            </li>
                                        ))}
                                    </ul>
                                </CardContent>
                            </Card>
                        )}

                        {/* API docs link */}
                        <Card className="border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                            <CardContent className="pt-5">
                                <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">
                                    You can also trigger imports directly via the REST API or Swagger UI.
                                </p>
                                <Button variant="outline" size="sm" className="w-full text-xs" asChild>
                                    <a
                                        href="http://localhost:8000/api/v1/docs#/datasets"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        <ExternalLink className="h-3.5 w-3.5 mr-1.5" />
                                        Open Swagger UI → /datasets
                                    </a>
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </main>

            {/* Import modal */}
            <ImportModal
                dataset={selectedDataset}
                onClose={() => setSelectedDataset(null)}
                onConfirm={handleImport}
            />
        </div>
    );
}
