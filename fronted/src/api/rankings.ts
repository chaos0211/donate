import service from "./http";

export async function fetchRankings(params: Record<string, any>) {
  const { data } = await service.get("/api/v1/rankings", { params });
  return data;
}