// frontend/src/components/FilesManager.tsx
import React, { useState, useEffect } from "react";

interface FileInfo {
  filename: string;
  time_range: string;
  article_count: number;
  file_size: string;
  created: number;
}

interface FilesManagerProps {
  className?: string;
}

const FilesManager: React.FC<FilesManagerProps> = ({ className = "" }) => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Format timestamp string from YYYYMMDDHHmmSS to readable date
  const formatTimestamp = (timestamp: string) => {
    if (timestamp.length !== 14) return timestamp;

    const year = timestamp.substring(0, 4);
    const month = timestamp.substring(4, 6);
    const day = timestamp.substring(6, 8);
    const hour = timestamp.substring(8, 10);
    const minute = timestamp.substring(10, 12);

    const date = new Date(
      parseInt(year),
      parseInt(month) - 1, // months are 0-indexed in JS
      parseInt(day),
      parseInt(hour),
      parseInt(minute)
    );

    return new Intl.DateTimeFormat("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  // Format time range from "YYYYMMDDHHMMSS to YYYYMMDDHHMMSS"
  const formatTimeRange = (timeRange: string) => {
    const parts = timeRange.split(" to ");
    if (parts.length !== 2) return timeRange;

    return `${formatTimestamp(parts[0])} to ${formatTimestamp(parts[1])}`;
  };

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/data/info/files");

      if (!response.ok) {
        throw new Error(`Error fetching files: ${response.status}`);
      }

      const data = await response.json();
      setFiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch files");
    } finally {
      setLoading(false);
    }
  };

  // Fetch files when component mounts
  useEffect(() => {
    fetchFiles();
  }, []);

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
    <div className={`bg-white rounded-ios p-5 shadow-ios ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold text-ios-gray-800">Saved Files</h2>
        <button
          onClick={fetchFiles}
          disabled={loading}
          className="text-xs text-uoft-blue hover:text-uoft-blue/80 transition-colors"
        >
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="bg-ios-red/10 text-ios-red text-xs p-3 rounded-ios mb-3">
          {error}
        </div>
      )}

      {loading && files.length === 0 ? (
        <div className="flex justify-center items-center py-10">
          <div className="w-6 h-6 border-2 border-uoft-blue border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-8 text-ios-gray-500 text-sm">
          No saved files found.
        </div>
      ) : (
        <div className="max-h-80 overflow-y-auto pr-1 space-y-3">
          {files.map((file) => (
            <div
              key={file.filename}
              className="border border-ios-gray-100 rounded-ios p-3 hover:bg-ios-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div>
                    <div className="text-sm font-medium text-ios-gray-800 mb-1 line-clamp-1">
                      {formatTimeRange(file.time_range)}
                    </div>
                  </div>
                  <div className="flex items-center text-xs text-ios-gray-500 space-x-2">
                    <span>{file.article_count} articles</span>
                    <span>•</span>
                    <span>{file.file_size}</span>
                  </div>
                </div>
                <a
                  href={`/data/info/files/${encodeURIComponent(file.filename)}`}
                  download
                  className="flex-shrink-0 text-xs bg-uoft-blue/10 text-uoft-blue px-3 py-1.5 rounded-full hover:bg-uoft-blue/20 transition-colors"
                >
                  Download
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FilesManager;