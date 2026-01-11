'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Search, Loader2, FileText, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { api, SearchResult } from '@/lib/api-client';



export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!query.trim()) return;

    setSearching(true);
    setError(null);

    try {
      const data = await api.search.semantic({
        query_text: query,
        tenant_id: 1, // TODO: Get from auth context
        top_k: 10,
      });

      setResults(data.results || []);
      setSearchTime(data.search_duration_ms || 0);
      setSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed. Please try again.');
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="border-b bg-white dark:bg-slate-900 sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Home
                </Link>
              </Button>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Sparkles className="h-6 w-6 text-purple-600" />
                Search Documents
              </h1>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" asChild>
                <Link href="/documents">My Documents</Link>
              </Button>
              <Button size="sm" asChild>
                <Link href="/upload">Upload New</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Search Box */}
          <Card className="mb-8 border-2 shadow-lg">
            <CardContent className="p-6">
              <form onSubmit={handleSearch}>
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
                    <Input
                      type="text"
                      placeholder="Ask a question or search for content... (e.g., 'How to deploy Docker?')"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      className="pl-10 h-12 text-lg"
                      disabled={searching}
                    />
                  </div>
                  <Button
                    type="submit"
                    size="lg"
                    disabled={searching || !query.trim()}
                    className="px-8"
                  >
                    {searching ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="mr-2 h-5 w-5" />
                        Search
                      </>
                    )}
                  </Button>
                </div>
              </form>

              {/* Search Info */}
              <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600 dark:text-slate-400">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Semantic search enabled
                </div>
                <div>
                  Languages: English, Chinese (中文)
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Error Message */}
          {error && (
            <Card className="mb-8 border-red-200 bg-red-50 dark:bg-red-900/10">
              <CardContent className="p-4 text-red-600 dark:text-red-400">
                {error}
              </CardContent>
            </Card>
          )}

          {/* Results */}
          {results.length > 0 && (
            <>
              <div className="mb-4 text-sm text-slate-600 dark:text-slate-400">
                Found {results.length} results
                {searchTime && ` in ${searchTime}ms`}
              </div>

              <div className="space-y-4">
                {results.map((result) => (
                  <Card
                    key={result.chunk_id}
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        {/* Rank Badge */}
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center font-semibold text-blue-600 dark:text-blue-300">
                          {result.rank_position}
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          {/* Document Title */}
                          <div className="flex items-center gap-2 mb-2">
                            <FileText className="h-4 w-4 text-slate-400" />
                            <span className="font-semibold text-sm text-slate-700 dark:text-slate-300">
                              {result.document_title || `Document ${result.document_id}`}
                            </span>
                            {result.page_number && (
                              <span className="text-xs text-slate-500">
                                Page {result.page_number}
                              </span>
                            )}
                          </div>

                          {/* Text Snippet */}
                          <p className="text-slate-700 dark:text-slate-300 mb-3 line-clamp-3">
                            {result.text_snippet}
                          </p>

                          {/* Footer */}
                          <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-4 text-slate-500">
                              <span>Chunk ID: {result.chunk_id}</span>
                              <span>Doc ID: {result.document_id}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-slate-500">Relevance:</span>
                              <span className="font-semibold text-green-600 dark:text-green-400">
                                {formatScore(result.similarity_score)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}

          {/* No Results State */}
          {!searching && searched && results.length === 0 && !error && (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="h-16 w-16 mx-auto mb-4 text-slate-300" />
                <h3 className="text-xl font-semibold mb-2">No results found</h3>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                  We couldn't find any documents matching "{query}". Try different keywords or upload more documents.
                </p>
                <Button asChild variant="outline">
                  <Link href="/upload">Upload Documents</Link>
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Initial State */}
          {!searching && !searched && results.length === 0 && !error && (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="h-16 w-16 mx-auto mb-4 text-slate-300" />
                <h3 className="text-xl font-semibold mb-2">Start Your Search</h3>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                  Enter a question or keywords to search through your documents
                </p>

                {/* Example Queries */}
                <div className="max-w-md mx-auto">
                  <p className="text-sm font-semibold mb-3 text-slate-700 dark:text-slate-300">
                    Example queries:
                  </p>
                  <div className="space-y-2 text-sm text-left">
                    <button
                      onClick={() => setQuery('How to deploy with Docker?')}
                      className="w-full p-3 rounded-lg border hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
                    >
                      "How to deploy with Docker?"
                    </button>
                    <button
                      onClick={() => setQuery('What is the API authentication process?')}
                      className="w-full p-3 rounded-lg border hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
                    >
                      "What is the API authentication process?"
                    </button>
                    <button
                      onClick={() => setQuery('Database migration steps')}
                      className="w-full p-3 rounded-lg border hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-left"
                    >
                      "Database migration steps"
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tips Card */}
          <Card className="mt-8">
            <CardContent className="p-6">
              <h3 className="font-semibold mb-3">Search Tips</h3>
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li>• Use natural language questions for best results</li>
                <li>• Search works in both English and Chinese (中文)</li>
                <li>• Results are ranked by semantic relevance, not exact keyword matches</li>
                <li>• Upload more documents to improve search coverage</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
