import { useUser, useUpdateUser, useLogout } from "@/hooks/use-user";
import { useItems } from "@/hooks/use-items"; // Ideally filter by ownerId, assuming API supports it or we filter client-side for MVP
import { Navigation } from "@/components/Navigation";
import { User, Settings, LogOut } from "lucide-react";
import { ItemCard } from "@/components/ItemCard";

export default function UserProfile() {
  const { data: user, isLoading: userLoading } = useUser();
  const { mutate: logout } = useLogout();
  const { mutate: updateProfile } = useUpdateUser();
  // In a real app, we'd have a specific endpoint for user's items
  // For this MVP, let's just assume this endpoint works
  const { data: items } = useItems();

  if (userLoading || !user) return null;

  // Filter client side for MVP since API doesn't have explicit my-items endpoint yet
  const myItems = items?.filter(item => item.ownerId === user.id) || [];

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="bg-foreground text-background pb-20 pt-12 px-6 rounded-b-[2.5rem] shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

        <div className="relative z-10 flex justify-between items-start mb-8">
          <h1 className="text-3xl font-display font-bold">Gear Locker</h1>
          <button onClick={() => logout()} className="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors">
            <LogOut className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center gap-5 relative z-10">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary p-[3px]">
            <div className="w-full h-full rounded-full bg-foreground flex items-center justify-center border-4 border-foreground">
              <span className="text-2xl font-bold text-white">{user.username?.substring(0, 2).toUpperCase()}</span>
            </div>
          </div>
          <div>
            <h2 className="text-xl font-bold">{user.username}</h2>
            <p className="text-white/60 text-sm mt-1">{user.bio || "No bio yet"}</p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 -mt-10">
        <div className="bg-card rounded-2xl p-6 shadow-lg border border-border/50 mb-8 flex justify-between items-center">
          <div>
            <span className="block text-2xl font-bold text-foreground">{myItems.length}</span>
            <span className="text-sm text-muted-foreground">Items Listed</span>
          </div>
          <div className="h-8 w-px bg-border" />
          <div>
            <span className="block text-2xl font-bold text-foreground">0</span>
            <span className="text-sm text-muted-foreground">Trades Done</span>
          </div>
          <div className="h-8 w-px bg-border" />
          <div>
            <span className="block text-2xl font-bold text-foreground">5.0</span>
            <span className="text-sm text-muted-foreground">Rating</span>
          </div>
        </div>

        <h3 className="font-display font-bold text-lg mb-4">My Listings</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {myItems.map(item => (
            <ItemCard key={item.id} item={item} />
          ))}
          {myItems.length === 0 && (
            <div className="col-span-full py-10 text-center text-muted-foreground bg-muted/30 rounded-2xl border border-dashed border-border">
              No items listed yet.
            </div>
          )}
        </div>
      </div>

      <Navigation />
    </div>
  );
}
