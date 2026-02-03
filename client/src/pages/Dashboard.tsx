import { useState } from "react";
import { useItems } from "@/hooks/use-items";
import { ItemCard } from "@/components/ItemCard";
import { GeoTracker } from "@/components/GeoTracker";
import { Navigation } from "@/components/Navigation";
import { Search, SlidersHorizontal, MapPin } from "lucide-react";
import { motion } from "framer-motion";

export default function Dashboard() {
  const [coords, setCoords] = useState<{ lat?: number; lng?: number }>({});
  const [radius, setRadius] = useState(5);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string | undefined>(undefined);
  
  const { data: items, isLoading } = useItems({
    ...coords,
    radius,
    search: search || undefined,
    category
  });

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-border shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-display font-bold text-foreground">Discover Gear</h1>
              <div className="flex items-center gap-2 mt-1">
                <MapPin className="w-3.5 h-3.5 text-primary" />
                <span className="text-xs text-muted-foreground">
                  Within {radius} miles • 
                  <GeoTracker onLocationFound={(lat, lng) => setCoords({ lat, lng })} autoUpdateProfile />
                </span>
              </div>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary overflow-hidden p-[2px]">
              <div className="w-full h-full bg-white rounded-full flex items-center justify-center">
                <span className="font-bold text-foreground text-xs">HH</span>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search guitars, cameras..."
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-muted/50 border-none text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary/20 focus:bg-white transition-all"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Search className="absolute left-3 top-3.5 w-5 h-5 text-muted-foreground" />
            <button className="absolute right-3 top-3 p-1 rounded-lg hover:bg-muted text-muted-foreground transition-colors">
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>

          {/* Categories */}
          <div className="flex gap-2 mt-4 overflow-x-auto pb-2 scrollbar-hide">
            {["All", "Music", "Tech", "Sports", "Art", "Other"].map((cat) => (
              <button
                key={cat}
                onClick={() => setCategory(cat === "All" ? undefined : cat)}
                className={`
                  px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all duration-200
                  ${(category === cat || (cat === "All" && !category))
                    ? "bg-foreground text-background shadow-md" 
                    : "bg-white border border-border text-muted-foreground hover:border-foreground/20"
                  }
                `}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Grid */}
      <main className="max-w-5xl mx-auto px-4 py-6">
        {isLoading ? (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        ) : items && items.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                {/* Calculate distance roughly if coords are known (this is usually done by backend) */}
                <ItemCard item={item} distance={item.latitude && coords.lat ? calculateDistance(coords.lat, coords.lng!, item.latitude, item.longitude!) : undefined} />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 px-6">
            <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-bold text-foreground">No items found nearby</h3>
            <p className="text-muted-foreground mt-2 max-w-xs mx-auto">Try increasing your search radius or changing the category.</p>
            <input 
              type="range" 
              min="1" 
              max="50" 
              value={radius} 
              onChange={(e) => setRadius(parseInt(e.target.value))}
              className="mt-6 w-full max-w-xs accent-primary"
            />
            <p className="text-xs text-muted-foreground mt-2">{radius} miles</p>
          </div>
        )}
      </main>

      <Navigation />
    </div>
  );
}

// Simple Haversine fallback for frontend distance estimation
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number) {
  const R = 3958.8; // Radius of Earth in miles
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}
