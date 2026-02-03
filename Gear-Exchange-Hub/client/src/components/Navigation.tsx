import { useLocation, Link } from "wouter";
import { Home, PlusCircle, Repeat, User } from "lucide-react";
import { cn } from "@/lib/utils";

export function Navigation() {
  const [location] = useLocation();

  const navItems = [
    { href: "/dashboard", icon: Home, label: "Explore" },
    { href: "/trades", icon: Repeat, label: "Trades" },
    { href: "/post", icon: PlusCircle, label: "Post" },
    { href: "/profile", icon: User, label: "Profile" },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-t border-border shadow-lg pb-safe">
      <div className="flex justify-around items-center h-16 max-w-md mx-auto">
        {navItems.map((item) => {
          const isActive = location === item.href;
          return (
            <Link key={item.href} href={item.href} className="w-full h-full flex flex-col items-center justify-center gap-1 group">
              <div 
                className={cn(
                  "p-1.5 rounded-xl transition-all duration-300",
                  isActive 
                    ? "bg-primary/10 text-primary translate-y-[-4px]" 
                    : "text-muted-foreground group-hover:text-foreground"
                )}
              >
                <item.icon className={cn("w-6 h-6", isActive && "fill-current")} strokeWidth={isActive ? 2.5 : 2} />
              </div>
              <span 
                className={cn(
                  "text-[10px] font-medium transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground"
                )}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
