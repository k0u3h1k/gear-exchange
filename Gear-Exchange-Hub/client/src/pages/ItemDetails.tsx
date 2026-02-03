import { useRoute } from "wouter";
import { useItem } from "@/hooks/use-items";
import { useCreateTrade } from "@/hooks/use-trades";
import { useUser } from "@/hooks/use-user";
import { Navigation } from "@/components/Navigation";
import { ArrowLeft, MapPin, Share2, Check, Loader2 } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

export default function ItemDetails() {
  const [, params] = useRoute("/items/:id");
  const id = parseInt(params?.id || "0");
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  
  const { data: item, isLoading } = useItem(id);
  const { data: user } = useUser();
  const { mutate: createTrade, isPending: isCreatingTrade } = useCreateTrade();
  
  const [requestSent, setRequestSent] = useState(false);

  if (isLoading) return <div className="h-screen flex items-center justify-center"><Loader2 className="animate-spin text-primary" /></div>;
  if (!item) return <div className="h-screen flex items-center justify-center">Item not found</div>;

  const handleTradeRequest = () => {
    if (!user) {
      window.location.href = "/api/login";
      return;
    }
    
    createTrade({ itemId: item.id }, {
      onSuccess: () => {
        setRequestSent(true);
        toast({
          title: "Request Sent!",
          description: "The owner has been notified.",
        });
        setTimeout(() => setLocation("/trades"), 1500);
      },
      onError: () => {
        toast({
          title: "Error",
          description: "Failed to send request. You might already have a pending trade.",
          variant: "destructive",
        });
      }
    });
  };

  const isOwner = user?.id === item.ownerId;
  const displayImage = item.images && item.images.length > 0 
    ? item.images[0] 
    : "https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=800&h=600&fit=crop";

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Hero Image */}
      <div className="relative h-96 w-full">
        <img 
          src={displayImage} 
          alt={item.title} 
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent opacity-80" />
        
        <Link href="/dashboard" className="absolute top-4 left-4 p-2 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-white/30 transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <button className="absolute top-4 right-4 p-2 bg-white/20 backdrop-blur-md rounded-full text-white hover:bg-white/30 transition-colors">
          <Share2 className="w-6 h-6" />
        </button>
      </div>

      <div className="max-w-3xl mx-auto px-6 -mt-10 relative">
        <div className="glass-panel rounded-3xl p-6 md:p-8">
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className="inline-block px-3 py-1 bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider rounded-full mb-2">
                {item.category}
              </span>
              <h1 className="text-3xl font-display font-bold text-foreground mb-1">{item.title}</h1>
              <div className="flex items-center text-muted-foreground text-sm">
                <MapPin className="w-4 h-4 mr-1 text-secondary" />
                <span>Local Pickup</span>
              </div>
            </div>
          </div>

          <p className="text-muted-foreground leading-relaxed text-lg mb-8">
            {item.description}
          </p>

          {!isOwner && (
            <div className="border-t border-border pt-6">
              <button
                onClick={handleTradeRequest}
                disabled={isCreatingTrade || requestSent}
                className={`
                  w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all duration-300 flex items-center justify-center gap-2
                  ${requestSent 
                    ? "bg-green-500 text-white shadow-green-500/25 cursor-default" 
                    : "bg-gradient-to-r from-primary to-primary/90 text-primary-foreground shadow-primary/25 hover:shadow-xl hover:-translate-y-0.5"
                  }
                  disabled:opacity-70 disabled:transform-none
                `}
              >
                {isCreatingTrade ? (
                  <Loader2 className="animate-spin w-6 h-6" />
                ) : requestSent ? (
                  <>
                    <Check className="w-6 h-6" />
                    Request Sent
                  </>
                ) : (
                  "Request Trade"
                )}
              </button>
              <p className="text-center text-xs text-muted-foreground mt-3">
                No money involved. Just pure trading.
              </p>
            </div>
          )}
        </div>
      </div>
      
      <Navigation />
    </div>
  );
}
