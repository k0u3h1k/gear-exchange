import { useUser } from "@/hooks/use-user";
import { Redirect } from "wouter";
import { ArrowRight, Guitar, Camera, Gamepad2 } from "lucide-react";
import { motion } from "framer-motion";

export default function Landing() {
  const { data: user, isLoading } = useUser();

  if (isLoading) return null;
  if (user) return <Redirect to="/dashboard" />;

  const handleLogin = () => {
    window.location.href = "/api/login";
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Abstract Background Shapes */}
      <div className="absolute -top-20 -right-20 w-96 h-96 bg-secondary/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute top-1/2 -left-20 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-12 flex flex-col items-center justify-center min-h-screen text-center">
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 mb-6 px-4 py-1.5 rounded-full bg-white shadow-sm border border-border">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-semibold text-muted-foreground tracking-wide uppercase">Local Hobby Trading</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-display font-extrabold tracking-tight mb-6 text-foreground leading-[1.1]">
            Turn your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary/60">Dust</span> into <span className="text-transparent bg-clip-text bg-gradient-to-r from-secondary to-orange-400">Trust</span>
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            Hobby-Hopper connects you with local enthusiasts to trade the gear you don't use for the gear you've always wanted. No shipping, no fees, just hobbies.
          </p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 w-full justify-center"
        >
          <button 
            onClick={handleLogin}
            className="group px-8 py-4 rounded-xl bg-foreground text-background font-bold text-lg shadow-xl shadow-black/10 hover:scale-105 active:scale-95 transition-all duration-300 flex items-center justify-center gap-2"
          >
            Start Trading
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

        {/* Feature Icons */}
        <div className="mt-20 grid grid-cols-3 gap-8 md:gap-16 w-full max-w-lg">
          {[
            { Icon: Guitar, label: "Music" },
            { Icon: Camera, label: "Tech" },
            { Icon: Gamepad2, label: "Games" },
          ].map(({ Icon, label }, i) => (
            <motion.div 
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + (i * 0.1) }}
              className="flex flex-col items-center gap-3"
            >
              <div className="w-16 h-16 rounded-2xl bg-white shadow-lg shadow-primary/5 flex items-center justify-center border border-border/50">
                <Icon className="w-8 h-8 text-primary" strokeWidth={1.5} />
              </div>
              <span className="font-medium text-muted-foreground">{label}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
