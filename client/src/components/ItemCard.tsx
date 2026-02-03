import { Item } from "@shared/schema";
import { MapPin } from "lucide-react";
import { Link } from "wouter";

interface ItemCardProps {
  item: Item;
  distance?: number;
}

export function ItemCard({ item, distance }: ItemCardProps) {
  // Use first image or a placeholder based on category
  const displayImage = item.images && item.images.length > 0 
    ? item.images[0] 
    : "https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=500&h=500&fit=crop"; // generic hobby image

  return (
    <Link href={`/items/${item.id}`} className="block group">
      <div className="bg-card rounded-2xl overflow-hidden shadow-sm border border-border/50 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 group-hover:border-primary/20">
        <div className="relative aspect-square overflow-hidden bg-muted">
          {/* Category Badge */}
          <div className="absolute top-3 right-3 z-10 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-bold text-foreground shadow-sm">
            {item.category}
          </div>
          
          <img 
            src={displayImage} 
            alt={item.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>
        
        <div className="p-4">
          <div className="flex justify-between items-start gap-2">
            <h3 className="font-display font-bold text-lg leading-tight line-clamp-1">{item.title}</h3>
            {distance !== undefined && (
              <span className="flex items-center text-xs font-medium text-muted-foreground whitespace-nowrap bg-muted px-2 py-0.5 rounded-md">
                <MapPin className="w-3 h-3 mr-1 text-primary" />
                {distance.toFixed(1)} mi
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-muted-foreground line-clamp-2">{item.description}</p>
        </div>
      </div>
    </Link>
  );
}
