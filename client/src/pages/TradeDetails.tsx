import { useRoute } from "wouter";
import { useTrade, useUpdateTradeStatus } from "@/hooks/use-trades";
import { useMessages, useSendMessage } from "@/hooks/use-messages";
import { useUser } from "@/hooks/use-user";
import { Navigation } from "@/components/Navigation";
import { Loader2, Send, CheckCircle, XCircle } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { format } from "date-fns";

export default function TradeDetails() {
  const [, params] = useRoute("/trades/:id");
  const tradeId = parseInt(params?.id || "0");
  
  const { data: user } = useUser();
  const { data: trade, isLoading: tradeLoading } = useTrade(tradeId);
  const { data: messages, isLoading: msgsLoading } = useMessages(tradeId);
  const { mutate: sendMessage, isPending: sendingMsg } = useSendMessage();
  const { mutate: updateStatus, isPending: updatingStatus } = useUpdateTradeStatus();

  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (tradeLoading || msgsLoading) return <div className="h-screen flex items-center justify-center"><Loader2 className="animate-spin text-primary" /></div>;
  if (!trade || !user) return <div className="p-8 text-center">Trade not found or unauthorized</div>;

  const isOwner = user.id === trade.ownerId;
  const isRequester = user.id === trade.requesterId;
  const isParticipant = isOwner || isRequester;

  if (!isParticipant) return <div className="p-8 text-center text-destructive">Unauthorized access</div>;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    sendMessage({ tradeId, content: input });
    setInput("");
  };

  const handleStatus = (status: "accepted" | "rejected" | "completed") => {
    updateStatus({ id: tradeId, status });
  };

  return (
    <div className="flex flex-col h-screen bg-background pb-safe">
      {/* Header */}
      <div className="px-6 py-4 border-b border-border bg-white/80 backdrop-blur shadow-sm z-10 flex justify-between items-center">
        <div>
          <h1 className="font-display font-bold text-lg">Trade #{trade.id}</h1>
          <p className="text-xs text-muted-foreground">{trade.item.title}</p>
        </div>
        <div className="px-2.5 py-1 bg-muted rounded-full text-xs font-bold uppercase tracking-wider">
          {trade.status}
        </div>
      </div>

      {/* Action Bar (Only for Owner and Pending state) */}
      {isOwner && trade.status === "requested" && (
        <div className="p-4 bg-orange-50 border-b border-orange-100 flex gap-3">
          <button 
            onClick={() => handleStatus("accepted")}
            disabled={updatingStatus}
            className="flex-1 py-2.5 bg-green-600 text-white rounded-xl font-bold text-sm shadow-sm hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
          >
            <CheckCircle className="w-4 h-4" /> Accept
          </button>
          <button 
            onClick={() => handleStatus("rejected")}
            disabled={updatingStatus}
            className="flex-1 py-2.5 bg-white border border-red-200 text-red-600 rounded-xl font-bold text-sm shadow-sm hover:bg-red-50 transition-colors flex items-center justify-center gap-2"
          >
            <XCircle className="w-4 h-4" /> Reject
          </button>
        </div>
      )}

      {/* Complete Button (If accepted) */}
      {trade.status === "accepted" && (
        <div className="p-4 bg-blue-50 border-b border-blue-100 text-center">
          <p className="text-sm text-blue-800 mb-3">Meet up to exchange items!</p>
          <button 
            onClick={() => handleStatus("completed")}
            disabled={updatingStatus}
            className="w-full py-2 bg-blue-600 text-white rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors"
          >
            Mark as Completed
          </button>
        </div>
      )}

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/10" ref={scrollRef}>
        {messages?.map((msg) => {
          const isMe = msg.senderId === user.id;
          return (
            <div key={msg.id} className={`flex ${isMe ? "justify-end" : "justify-start"}`}>
              <div 
                className={`
                  max-w-[80%] rounded-2xl px-4 py-2.5 text-sm shadow-sm
                  ${isMe 
                    ? "bg-primary text-primary-foreground rounded-br-none" 
                    : "bg-white text-foreground border border-border rounded-bl-none"
                  }
                `}
              >
                {msg.content}
                <div className={`text-[10px] mt-1 opacity-70 ${isMe ? "text-right" : "text-left"}`}>
                  {msg.createdAt && format(new Date(msg.createdAt), "h:mm a")}
                </div>
              </div>
            </div>
          );
        })}
        {messages?.length === 0 && (
          <div className="text-center text-muted-foreground text-sm py-8">
            No messages yet. Start the conversation!
          </div>
        )}
      </div>

      {/* Input Area (Only if accepted/requested) */}
      {(trade.status === "requested" || trade.status === "accepted") && (
        <form onSubmit={handleSend} className="p-4 bg-white border-t border-border flex gap-3 mb-16">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-4 py-3 bg-muted rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
            disabled={sendingMsg}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || sendingMsg}
            className="p-3 bg-foreground text-background rounded-xl hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {sendingMsg ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
      )}

      <Navigation />
    </div>
  );
}
