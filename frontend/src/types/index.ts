export type NewsSource = "techcrunch" | "36kr";

export interface NewsItem {
  id: string;
  url: string;
  title: string;
  author: string | null;
  summary: string | null;
  content: string | null;
  publish_timestamp: number;
  gmt8time: string;
  source: NewsSource;
}

export interface InfoCollectReq {
  days_back: number;
  category: string;
  source: NewsSource[];
  limit: number;
}

export interface InfoCollectResp {
  timestamp: string;
  total_count: number;
  items: NewsItem[];
}
