import { useEffect, useState } from "react";
import { useUpdateUser } from "@/hooks/use-user";
import { MapPin, AlertCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface GeoTrackerProps {
  onLocationFound?: (lat: number, lng: number) => void;
  autoUpdateProfile?: boolean;
}

export function GeoTracker({ onLocationFound, autoUpdateProfile = false }: GeoTrackerProps) {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const { mutate: updateUser } = useUpdateUser();

  const getLocation = () => {
    if (!navigator.geolocation) {
      setStatus("error");
      return;
    }

    setStatus("loading");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setStatus("success");
        if (onLocationFound) onLocationFound(latitude, longitude);
        if (autoUpdateProfile) {
          updateUser({ latitude, longitude });
        }
      },
      () => {
        setStatus("error");
      }
    );
  };

  useEffect(() => {
    // Auto-start if requested
    if (autoUpdateProfile) getLocation();
  }, []);

  if (status === "idle" || status === "success") {
    return (
      <button 
        onClick={getLocation}
        className={cn(
          "flex items-center text-sm font-medium transition-colors",
          status === "success" ? "text-primary" : "text-muted-foreground hover:text-foreground"
        )}
      >
        <MapPin className="w-4 h-4 mr-1.5" />
        {status === "success" ? "Location Updated" : "Update Location"}
      </button>
    );
  }

  if (status === "loading") {
    return (
      <div className="flex items-center text-sm text-muted-foreground">
        <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
        Locating...
      </div>
    );
  }

  return (
    <div className="flex items-center text-sm text-destructive">
      <AlertCircle className="w-4 h-4 mr-1.5" />
      Location Disabled
    </div>
  );
}
