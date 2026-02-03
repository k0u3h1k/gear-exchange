import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { insertItemSchema } from "@shared/schema";
import { useCreateItem } from "@/hooks/use-items";
import { useUser } from "@/hooks/use-user";
import { Navigation } from "@/components/Navigation";
import { Loader2, UploadCloud, MapPin, Camera } from "lucide-react";
import { useLocation } from "wouter";
import { z } from "zod";
import { GeoTracker } from "@/components/GeoTracker";
import { useState } from "react";

// Form schema with some UI-specific refinements
const formSchema = insertItemSchema.extend({
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  imageUrl: z.string().url().optional().or(z.literal("")),
});

type FormData = z.infer<typeof formSchema>;

export default function PostItem() {
  const [, setLocation] = useLocation();
  const { data: user } = useUser();
  const { mutate: createItem, isPending } = useCreateItem();
  const [coords, setCoords] = useState<{ lat?: number; lng?: number }>({});

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      category: "Music",
      status: "available",
      images: [],
    }
  });

  const onSubmit = (data: FormData) => {
    const submissionData = {
      ...data,
      // Fallback to manual coords if present, otherwise user profile coords
      latitude: coords.lat || user?.latitude || undefined,
      longitude: coords.lng || user?.longitude || undefined,
      // Handle the single image input -> array conversion
      images: data.imageUrl ? [data.imageUrl] : [],
    };
    
    // Remove the temporary UI field before sending
    delete (submissionData as any).imageUrl;

    createItem(submissionData as any, {
      onSuccess: () => setLocation("/dashboard"),
    });
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="max-w-md mx-auto px-4 py-8">
        <h1 className="text-3xl font-display font-bold text-foreground mb-2">Post Gear</h1>
        <p className="text-muted-foreground mb-8">List your item for local trading.</p>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          
          {/* Image Upload Placeholder */}
          <div className="border-2 border-dashed border-border rounded-2xl p-8 flex flex-col items-center justify-center text-center bg-muted/30 hover:bg-muted/50 transition-colors cursor-pointer group">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Camera className="w-8 h-8 text-primary" />
            </div>
            <p className="font-medium text-foreground">Add Photos</p>
            <p className="text-xs text-muted-foreground mt-1">Tap to upload (Max 5)</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Title</label>
              <input
                {...form.register("title")}
                placeholder="e.g. Fender Stratocaster"
                className="w-full px-4 py-3 rounded-xl bg-white border border-border focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
              />
              {form.formState.errors.title && <p className="text-xs text-destructive mt-1">{form.formState.errors.title.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Category</label>
              <select
                {...form.register("category")}
                className="w-full px-4 py-3 rounded-xl bg-white border border-border focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all appearance-none"
              >
                <option value="Music">Music</option>
                <option value="Tech">Tech</option>
                <option value="Sports">Sports</option>
                <option value="Art">Art</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Description</label>
              <textarea
                {...form.register("description")}
                rows={4}
                placeholder="Condition, history, what you're looking for..."
                className="w-full px-4 py-3 rounded-xl bg-white border border-border focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all resize-none"
              />
              {form.formState.errors.description && <p className="text-xs text-destructive mt-1">{form.formState.errors.description.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Image URL (Optional)</label>
              <input
                {...form.register("imageUrl")}
                placeholder="https://..."
                className="w-full px-4 py-3 rounded-xl bg-white border border-border focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
              />
            </div>

            <div className="bg-muted/50 p-4 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="w-4 h-4" />
                <span>Location</span>
              </div>
              <GeoTracker 
                onLocationFound={(lat, lng) => setCoords({ lat, lng })}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isPending}
            className="w-full py-4 rounded-xl bg-foreground text-background font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 transition-all duration-200 flex items-center justify-center"
          >
            {isPending ? (
              <>
                <Loader2 className="animate-spin w-5 h-5 mr-2" />
                Posting...
              </>
            ) : (
              "Post Item"
            )}
          </button>
        </form>
      </div>
      <Navigation />
    </div>
  );
}
