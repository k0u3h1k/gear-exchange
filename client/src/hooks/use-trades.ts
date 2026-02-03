import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type CreateTradeRequest, type UpdateTradeStatusRequest } from "@shared/routes";

export function useTrades() {
  return useQuery({
    queryKey: [api.trades.list.path],
    queryFn: async () => {
      const res = await fetch(api.trades.list.path, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch trades");
      return api.trades.list.responses[200].parse(await res.json());
    },
  });
}

export function useTrade(id: number) {
  return useQuery({
    queryKey: [api.trades.get.path, id],
    queryFn: async () => {
      const url = buildUrl(api.trades.get.path, { id });
      const res = await fetch(url, { credentials: "include" });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error("Failed to fetch trade details");
      return api.trades.get.responses[200].parse(await res.json());
    },
  });
}

export function useCreateTrade() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateTradeRequest) => {
      const res = await fetch(api.trades.create.path, {
        method: api.trades.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to create trade request");
      return api.trades.create.responses[201].parse(await res.json());
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.trades.list.path] });
    },
  });
}

export function useUpdateTradeStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status }: { id: number } & UpdateTradeStatusRequest) => {
      const url = buildUrl(api.trades.updateStatus.path, { id });
      const res = await fetch(url, {
        method: api.trades.updateStatus.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to update trade status");
      return api.trades.updateStatus.responses[200].parse(await res.json());
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [api.trades.list.path] });
      queryClient.invalidateQueries({ queryKey: [api.trades.get.path, data.id] });
    },
  });
}
