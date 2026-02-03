import { useTrades } from "@/hooks/use-trades";
import { useUser } from "@/hooks/use-user";
import { Navigation } from "@/components/Navigation";
import { Link } from "wouter";
import { Repeat, ArrowRight, Clock, CheckCircle, XCircle } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

export default function TradesList() {
  const { data: trades, isLoading } = useTrades();
  const { data: user } = useUser();

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'accepted': return "text-green-600 bg-green-100";
      case 'rejected': return "text-red-600 bg-red-100";
      case 'completed': return "text-blue-600 bg-blue-100";
      default: return "text-yellow-600 bg-yellow-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'accepted': return CheckCircle;
      case 'rejected': return XCircle;
      case 'completed': return CheckCircle;
      default: return Clock;
    }
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-display font-bold text-foreground mb-6">Your Trades</h1>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
          </div>
        ) : trades && trades.length > 0 ? (
          <div className="space-y-4">
            {trades.map((trade) => {
              const isRequester = trade.requesterId === user?.id;
              const StatusIcon = getStatusIcon(trade.status);
              
              return (
                <Link key={trade.id} href={`/trades/${trade.id}`}>
                  <div className="bg-card rounded-2xl p-4 border border-border/50 shadow-sm hover:shadow-md transition-all cursor-pointer group">
                    <div className="flex justify-between items-start mb-3">
                      <div className={cn("px-2.5 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 uppercase tracking-wide", getStatusColor(trade.status))}>
                        <StatusIcon className="w-3.5 h-3.5" />
                        {trade.status}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {trade.createdAt && format(new Date(trade.createdAt), "MMM d, yyyy")}
                      </span>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                        <Repeat className="w-5 h-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-foreground truncate">
                          {isRequester ? "You requested an item" : "Someone requested your item"}
                        </p>
                        <p className="text-sm text-muted-foreground flex items-center gap-1 group-hover:text-primary transition-colors">
                          View Details <ArrowRight className="w-3 h-3" />
                        </p>
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-20 bg-muted/30 rounded-3xl border border-dashed border-border">
            <Repeat className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
            <h3 className="font-bold text-lg">No active trades</h3>
            <p className="text-muted-foreground mb-6">Start exploring items to trade!</p>
            <Link href="/dashboard" className="px-6 py-2.5 bg-primary text-primary-foreground rounded-lg font-medium text-sm hover:bg-primary/90 transition-colors">
              Explore Gear
            </Link>
          </div>
        )}
      </div>
      <Navigation />
    </div>
  );
}
