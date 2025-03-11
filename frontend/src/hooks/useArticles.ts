// frontend/src/hooks/useArticles.ts
import { useState } from "react";
import { ScrapeReq, ScrapeResp } from "../types";

export const useArticles = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [articles, setArticles] = useState<ScrapeResp | null>(null);

  const fetchArticles = async (params: ScrapeReq) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/data/info/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data: ScrapeResp = await response.json();
      setArticles(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  return { articles, loading, error, fetchArticles };
};
