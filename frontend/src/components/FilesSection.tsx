// frontend/src/components/FilesSection.tsx
import React, { useState, useEffect } from "react";
import FilesManager from "./FilesManager";
import { NewsItem, InterpretResp } from "../types";

interface FileInfo {
  filename: string;
  time_range: string;
  article_count: number;
  file_size: string;
  created: number;
}

const FilesSection: React.FC = () => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<NewsItem[]>([]);
  const [selectedArticles, setSelectedArticles] = useState<NewsItem[]>([]);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [report, setReport] = useState<InterpretResp | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch("/data/info/files");
      if (!response.ok) {
        throw new Error(`Failed to fetch files: ${response.status}`);
      }
      const data = await response.json();
      setFiles(data);

      // Auto-select the first file if available
      if (data.length > 0) {
        setSelectedFile(data[0].filename);
        await fetchFileContent(data[0].filename);
      }
    } catch (err) {
      console.error("Error fetching files:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch files");
    } finally {
      setLoading(false);
    }
  };

  const fetchFileContent = async (filename: string) => {
    try {
      const response = await fetch(
        `/data/info/files/${encodeURIComponent(filename)}`
      );
      if (!response.ok) {
        throw new Error(`Failed to fetch file content: ${response.status}`);
      }
      const data = await response.json();

      // Convert to NewsItem objects if they aren't already
      const articles = data.map((item: any) => ({
        id: item.id,
        url: item.url,
        title: item.title,
        author: item.author,
        summary: item.summary,
        content: item.content,
        publish_timestamp: item.publish_timestamp,
        gmt8time: item.gmt8time,
        source: item.source,
      }));

      setFileContent(articles);
      setSelectedArticles([]); // Clear previous selections
    } catch (err) {
      console.error("Error fetching file content:", err);
      setError(
        err instanceof Error ? err.message : "Failed to fetch file content"
      );
    }
  };

  const handleFileSelect = async (filename: string) => {
    setSelectedFile(filename);
    await fetchFileContent(filename);
    setReport(null); // Clear previous report when changing files
  };

  const handleSelectArticle = (article: NewsItem) => {
    setSelectedArticles((prev) => {
      // Check if article is already selected
      const isSelected = prev.some((a) => a.id === article.id);
      if (isSelected) {
        // Remove from selection
        return prev.filter((a) => a.id !== article.id);
      } else {
        // Add to selection
        return [...prev, article];
      }
    });
  };

  const handleSelectAll = () => {
    if (selectedArticles.length === fileContent.length) {
      // If all are selected, deselect all
      setSelectedArticles([]);
    } else {
      // Otherwise, select all
      setSelectedArticles([...fileContent]);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    if (selectedArticles.length === 0) {
      setError("Please select at least one article to include in the report");
      return;
    }

    setGeneratingReport(true);
    setError(null);

    try {
      const response = await fetch("/data/info/report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          filename: selectedFile,
          item_ids: selectedArticles.map((article) => article.id),
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Failed to generate report: ${response.status} - ${errorText}`
        );
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      console.error("Error generating report:", err);
      setError(
        err instanceof Error ? err.message : "Failed to generate report"
      );
    } finally {
      setGeneratingReport(false);
    }
  };

  // Format date from timestamp
  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="py-6">
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-ios-gray-800 mb-2">
          File Management
        </h2>
        <p className="text-ios-gray-600">
          Access and download your saved article collections
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {/* Files list */}
          <div className="bg-white rounded-ios shadow-ios p-5">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-semibold text-ios-gray-800">
                Saved Files
              </h3>
              <button
                onClick={fetchFiles}
                className="text-xs text-uoft-blue hover:text-uoft-blue-600 transition-colors"
              >
                Refresh
              </button>
            </div>

            {loading ? (
              <div className="flex justify-center py-8">
                <div className="w-8 h-8 border-2 border-uoft-blue border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : files.length === 0 ? (
              <div className="text-center py-8 text-ios-gray-500">
                No files found. Try scraping some articles first.
              </div>
            ) : (
              <div className="space-y-3">
                {files.map((file) => (
                  <div
                    key={file.filename}
                    onClick={() => handleFileSelect(file.filename)}
                    className={`border rounded-ios p-3 cursor-pointer transition-colors ${
                      selectedFile === file.filename
                        ? "border-uoft-blue bg-uoft-blue/5"
                        : "border-ios-gray-200 hover:bg-ios-gray-50"
                    }`}
                  >
                    <div className="flex justify-between">
                      <div>
                        <div className="text-sm font-medium text-ios-gray-800 mb-1">
                          {file.time_range}
                        </div>
                        <div className="flex text-xs text-ios-gray-500 space-x-2">
                          <span>{file.article_count} articles</span>
                          <span>•</span>
                          <span>{file.file_size}</span>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <a
                          href={`/data/info/files/${encodeURIComponent(
                            file.filename
                          )}`}
                          download
                          onClick={(e) => e.stopPropagation()}
                          className="text-xs bg-ios-gray-100 text-ios-gray-700 px-2 py-1 rounded hover:bg-ios-gray-200 transition-colors"
                        >
                          Download
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Article selection */}
          {selectedFile && fileContent.length > 0 && (
            <div className="bg-white rounded-ios shadow-ios p-5 mt-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-ios-gray-800">
                  Articles in {selectedFile}
                </h3>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-ios-gray-600">
                    {selectedArticles.length} of {fileContent.length} selected
                  </span>
                  <button
                    onClick={handleSelectAll}
                    className="text-xs text-uoft-blue hover:text-uoft-blue-600 transition-colors"
                  >
                    {selectedArticles.length === fileContent.length
                      ? "Deselect All"
                      : "Select All"}
                  </button>
                </div>
              </div>

              <div className="max-h-96 overflow-y-auto pr-1 space-y-2">
                {fileContent.map((article) => (
                  <div
                    key={article.id}
                    onClick={() => handleSelectArticle(article)}
                    className={`flex items-start p-3 border rounded-ios cursor-pointer transition-colors ${
                      selectedArticles.some((a) => a.id === article.id)
                        ? "border-uoft-blue bg-uoft-blue/5"
                        : "border-ios-gray-200 hover:bg-ios-gray-50"
                    }`}
                  >
                    <div className="flex-shrink-0 mr-3">
                      <div
                        className={`w-5 h-5 rounded border flex items-center justify-center ${
                          selectedArticles.some((a) => a.id === article.id)
                            ? "bg-uoft-blue border-uoft-blue"
                            : "border-ios-gray-300"
                        }`}
                      >
                        {selectedArticles.some((a) => a.id === article.id) && (
                          <svg
                            className="w-3 h-3 text-white"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-ios-gray-900 truncate">
                        {article.title}
                      </p>
                      <div className="flex mt-1 items-center text-xs">
                        <span
                          className={`px-1.5 py-0.5 rounded-full text-xs ${
                            article.source === "techcrunch"
                              ? "bg-green-100 text-green-800"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {article.source}
                        </span>
                        <span className="mx-1.5 text-ios-gray-500">•</span>
                        <span className="text-ios-gray-500">
                          {formatDate(article.publish_timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Report display */}
          {report && (
            <div className="bg-white rounded-ios shadow-ios p-5 mt-5">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-ios-gray-800">
                  Generated Report
                </h3>
                <a
                  href={`/data/info/files/${encodeURIComponent(
                    report.report_file
                  )}`}
                  download
                  className="text-xs bg-uoft-blue text-white px-3 py-1.5 rounded hover:bg-uoft-blue-600 transition-colors"
                >
                  Download Report
                </a>
              </div>

              <div className="mb-4">
                <h4 className="text-md font-medium text-ios-gray-900 mb-2">
                  {report.title}
                </h4>
                <p className="text-sm text-ios-gray-700 whitespace-pre-line">
                  {report.summary}
                </p>
              </div>

              {report.key_points.length > 0 && (
                <div className="border-t border-ios-gray-200 pt-4 mt-4">
                  <h4 className="text-sm font-medium text-ios-gray-800 mb-2">
                    Key Points
                  </h4>
                  <ul className="text-sm text-ios-gray-700 space-y-1">
                    {report.key_points.map((point, index) => (
                      <li key={index} className="flex">
                        <span className="mr-2">{index + 1}.</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="border-t border-ios-gray-200 pt-4 mt-4">
                <h4 className="text-sm font-medium text-ios-gray-800 mb-2">
                  Full Report
                </h4>
                <div className="bg-ios-gray-50 p-4 rounded-ios max-h-96 overflow-y-auto">
                  <pre className="text-sm font-sans whitespace-pre-wrap text-ios-gray-800">
                    {report.full_report}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-ios shadow-ios p-5">
          <h3 className="text-sm font-semibold text-ios-gray-800 mb-4">
            Quick Actions
          </h3>

          <div className="space-y-3">
            <button
              onClick={fetchFiles}
              className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-white bg-uoft-blue hover:bg-opacity-90 text-sm transition duration-150"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Refresh Files
            </button>

            {selectedFile && (
              <a
                href={`/data/info/files/${encodeURIComponent(selectedFile)}`}
                download
                className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-ios-gray-800 bg-ios-gray-100 hover:bg-ios-gray-200 text-sm transition duration-150"
              >
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
                Download Selected File
              </a>
            )}

            <button
              onClick={handleGenerateReport}
              disabled={
                !selectedFile ||
                selectedArticles.length === 0 ||
                generatingReport
              }
              className={`w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-sm transition duration-150 ${
                !selectedFile ||
                selectedArticles.length === 0 ||
                generatingReport
                  ? "bg-ios-gray-100 text-ios-gray-400 cursor-not-allowed"
                  : "bg-ios-green text-white hover:bg-opacity-90"
              }`}
            >
              {generatingReport ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Generate Report ({selectedArticles.length})
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-3">
              <p className="text-xs text-red-700">{error}</p>
            </div>
          )}

          {selectedArticles.length > 0 && (
            <div className="mt-4 pt-4 border-t border-ios-gray-200">
              <h4 className="text-xs font-medium text-ios-gray-700 mb-2">
                Selected Articles
              </h4>
              <div className="max-h-56 overflow-y-auto">
                {selectedArticles.map((article) => (
                  <div
                    key={article.id}
                    className="flex justify-between items-center py-2 text-xs border-b border-ios-gray-100 last:border-b-0"
                  >
                    <span className="truncate max-w-[180px] text-ios-gray-800">
                      {article.title}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSelectArticle(article);
                      }}
                      className="ml-2 text-ios-gray-400 hover:text-red-500"
                    >
                      <svg
                        className="w-3.5 h-3.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilesSection;
