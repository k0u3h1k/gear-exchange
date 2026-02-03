import { z } from "zod";

export const insertUserSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().optional(),
  email: z.string().email().optional(),
  googleId: z.string().optional(),
  bio: z.string().optional(),
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  profileImageUrl: z.string().optional(),
  location: z.string().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
});

export const insertItemSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  category: z.string().min(1, "Category is required"),
  images: z.array(z.string()).default([]),
  status: z.enum(["available", "sold"]).default("available"),
  location: z.string().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
});

export const insertTradeSchema = z.object({
  itemId: z.string(), // MongoDB IDs are strings
  requesterId: z.string(),
  ownerId: z.string(), // Added ownerId for trade creation validation if needed, though usually derived
  status: z.enum(["requested", "accepted", "rejected", "completed"]).default("requested"),
}).omit({ status: true }); // Status is server-managed initially

export const insertMessageSchema = z.object({
  tradeId: z.string(),
  content: z.string().min(1, "Content cannot be empty"),
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type InsertItem = z.infer<typeof insertItemSchema>;
// Trade input from API usually only contains itemId. 
// We'll define specific API schemas below.
export type InsertTrade = z.infer<typeof insertTradeSchema>;
export type InsertMessage = z.infer<typeof insertMessageSchema>;

export interface User extends InsertUser {
  id: string; // Mongoose _id mapped to id
  _id: string;
}

export interface Item extends InsertItem {
  id: string;
  _id: string;
  ownerId: string;
  createdAt: Date;
}

export interface Trade {
  id: string;
  _id: string;
  itemId: string;
  requesterId: string;
  ownerId: string;
  status: string;
  createdAt: Date;
  updatedAt?: Date;
}

export interface Message {
  id: string;
  _id: string;
  tradeId: string;
  senderId: string;
  content: string;
  createdAt: Date;
}

// API Schemas matched to what routes expect
export const api = {
  items: {
    list: {
      path: "/api/items",
      input: z.object({
        category: z.string().optional(),
        search: z.string().optional(),
        lat: z.string().optional(),
        lng: z.string().optional(),
        radius: z.string().optional()
      })
    },
    get: { path: "/api/items/:id" },
    create: {
      path: "/api/items",
      input: insertItemSchema
    },
    update: {
      path: "/api/items/:id",
      input: insertItemSchema.partial()
    },
    delete: { path: "/api/items/:id" }
  },
  trades: {
    list: { path: "/api/trades" },
    get: { path: "/api/trades/:id" },
    create: {
      path: "/api/trades",
      input: z.object({ itemId: z.string() })
    },
    updateStatus: {
      path: "/api/trades/:id/status",
      input: z.object({ status: z.enum(["accepted", "rejected", "completed"]) })
    }
  },
  messages: {
    list: { path: "/api/trades/:tradeId/messages" },
    create: {
      path: "/api/trades/:tradeId/messages",
      input: z.object({ content: z.string() })
    }
  },
  users: {
    me: { path: "/api/user" },
    update: {
      path: "/api/user",
      input: insertUserSchema.partial()
    }
  }
};

export type CreateTradeRequest = { itemId: string };
export type CreateItemRequest = InsertItem;
export type UpdateItemRequest = Partial<InsertItem>;
export type UpdateTradeStatusRequest = { status: "accepted" | "rejected" | "completed" };
export type CreateMessageRequest = { content: string };
