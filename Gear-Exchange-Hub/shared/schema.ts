import { pgTable, text, serial, integer, boolean, timestamp, doublePrecision, varchar, jsonb, index } from "drizzle-orm/pg-core";
import { relations, sql } from "drizzle-orm";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === AUTH TABLES (Mandatory for Replit Auth) ===

export const sessions = pgTable(
  "sessions",
  {
    sid: varchar("sid").primaryKey(),
    sess: jsonb("sess").notNull(),
    expire: timestamp("expire").notNull(),
  },
  (table) => [index("IDX_session_expire").on(table.expire)]
);

// === APP TABLES ===

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  googleId: text("google_id").unique(), // Keep existing naming if possible for compatibility
  username: text("username").notNull().unique(),
  email: text("email"),
  bio: text("bio"),
  location: text("location"), 
  latitude: doublePrecision("latitude"),
  longitude: doublePrecision("longitude"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const items = pgTable("items", {
  id: serial("id").primaryKey(),
  ownerId: integer("owner_id").notNull().references(() => users.id),
  title: text("title").notNull(),
  description: text("description").notNull(),
  category: text("category").notNull(),
  images: text("images").array().notNull().default([]),
  status: text("status").notNull().default("available"),
  location: text("location"), 
  latitude: doublePrecision("latitude"),
  longitude: doublePrecision("longitude"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const trades = pgTable("trades", {
  id: serial("id").primaryKey(),
  itemId: integer("item_id").notNull().references(() => items.id),
  requesterId: integer("requester_id").notNull().references(() => users.id),
  ownerId: integer("owner_id").notNull().references(() => users.id),
  status: text("status").notNull().default("requested"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  tradeId: integer("trade_id").notNull().references(() => trades.id),
  senderId: integer("sender_id").notNull().references(() => users.id),
  content: text("content").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// === RELATIONS ===

export const usersRelations = relations(users, ({ many }) => ({
  items: many(items),
  requestsSent: many(trades, { relationName: "requester" }),
  requestsReceived: many(trades, { relationName: "owner" }),
}));

export const itemsRelations = relations(items, ({ one, many }) => ({
  owner: one(users, {
    fields: [items.ownerId],
    references: [users.id],
  }),
  trades: many(trades),
}));

export const tradesRelations = relations(trades, ({ one, many }) => ({
  item: one(items, {
    fields: [trades.itemId],
    references: [items.id],
  }),
  requester: one(users, {
    fields: [trades.requesterId],
    references: [users.id],
    relationName: "requester",
  }),
  owner: one(users, {
    fields: [trades.ownerId],
    references: [users.id],
    relationName: "owner",
  }),
  messages: many(messages),
}));

export const messagesRelations = relations(messages, ({ one }) => ({
  trade: one(trades, {
    fields: [messages.tradeId],
    references: [trades.id],
  }),
  sender: one(users, {
    fields: [messages.senderId],
    references: [users.id],
  }),
}));

// === SCHEMAS ===

export const insertUserSchema = createInsertSchema(users).omit({ id: true, createdAt: true });
export const insertItemSchema = createInsertSchema(items).omit({ id: true, createdAt: true, ownerId: true });
export const insertTradeSchema = createInsertSchema(trades).omit({ id: true, createdAt: true, updatedAt: true, ownerId: true, status: true });
export const insertMessageSchema = createInsertSchema(messages).omit({ id: true, createdAt: true });

// === EXPLICIT TYPES ===

export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Item = typeof items.$inferSelect;
export type Trade = typeof trades.$inferSelect;
export type Message = typeof messages.$inferSelect;

export type CreateItemRequest = InsertItem;
export type UpdateItemRequest = Partial<InsertItem>;
export type CreateTradeRequest = { itemId: number };
export type UpdateTradeStatusRequest = { status: "accepted" | "rejected" | "completed" };
export type CreateMessageRequest = { content: string };
