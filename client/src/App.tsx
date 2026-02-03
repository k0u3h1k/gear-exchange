import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";

import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import ItemDetails from "@/pages/ItemDetails";
import PostItem from "@/pages/PostItem";
import TradesList from "@/pages/TradesList";
import TradeDetails from "@/pages/TradeDetails";
import UserProfile from "@/pages/UserProfile";
import { useUser } from "@/hooks/use-user";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Landing} />
      <ProtectedRoute path="/dashboard" component={Dashboard} />
      <ProtectedRoute path="/items/:id" component={ItemDetails} />
      <ProtectedRoute path="/post" component={PostItem} />
      <ProtectedRoute path="/trades" component={TradesList} />
      <ProtectedRoute path="/trades/:id" component={TradeDetails} />
      <ProtectedRoute path="/profile" component={UserProfile} />
      <Route component={NotFound} />
    </Switch>
  );
}

// Simple wrapper to handle auth protection
function ProtectedRoute({ component: Component, ...rest }: any) {
  const { data: user, isLoading } = useUser();

  return (
    <Route
      {...rest}
      component={() => {
        if (isLoading) return <div className="h-screen w-full flex items-center justify-center bg-background"><div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" /></div>;
        
        if (!user) {
          window.location.href = "/";
          return null;
        }
        return <Component />;
      }}
    />
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
