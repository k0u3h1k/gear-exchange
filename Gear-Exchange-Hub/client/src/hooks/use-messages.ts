import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, type CreateMessageRequest } from "@shared/routes";

export function useMessages(tradeId: number) {
  return useQuery({
    queryKey: [api.messages.list.path, tradeId],
    queryFn: async () => {
      const url = buildUrl(api.messages.list.path, { tradeId });
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch messages");
      return api.messages.list.responses[200].parse(await res.json());
    },
    refetchInterval: 3000, // Poll every 3s for new messages
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ tradeId, content }: { tradeId: number } & CreateMessageRequest) => {
      const url = buildUrl(api.messages.create.path, { tradeId });
      const res = await fetch(url, {
        method: api.messages.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to send message");
      return api.messages.create.responses[201].parse(await res.json());
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: [api.messages.list.path, variables.tradeId] });
    },
  });
}
