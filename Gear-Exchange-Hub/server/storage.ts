import { db } from "./db";
import {
  items, trades, messages, users,
  type Item, type InsertItem, type UpdateItemRequest,
  type Trade, type InsertTrade,
  type Message, type InsertMessage,
  type User, type InsertUser
} from "@shared/schema";
import { eq, and, or, desc, sql } from "drizzle-orm";

export interface IStorage {
  getItems(filters?: { location?: string; category?: string; search?: string }): Promise<Item[]>;
  getItem(id: number): Promise<Item | undefined>;
  createItem(item: InsertItem): Promise<Item>;
  updateItem(id: number, updates: UpdateItemRequest): Promise<Item>;
  deleteItem(id: number): Promise<void>;
  getTrades(userId: number): Promise<Trade[]>;
  getTrade(id: number): Promise<(Trade & { item: Item; messages: Message[] }) | undefined>;
  createTrade(trade: InsertTrade): Promise<Trade>;
  updateTradeStatus(id: number, status: string): Promise<Trade>;
  getMessages(tradeId: number): Promise<Message[]>;
  createMessage(message: InsertMessage): Promise<Message>;
  getUser(id: number): Promise<User | undefined>;
  getUserByReplitId(replitId: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: number, updates: Partial<InsertUser>): Promise<User>;
}

export class DatabaseStorage implements IStorage {
  async getUserByReplitId(replitId: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.googleId, replitId));
    return user;
  }

  async getItems(filters?: { lat?: number; lng?: number; radius?: number; category?: string; search?: string }): Promise<Item[]> {
    let conditions = [eq(items.status, "available")];

    if (filters?.category) {
      conditions.push(eq(items.category, filters.category));
    }

    if (filters?.search) {
      conditions.push(or(
        sql`lower(${items.title}) LIKE ${`%${filters.search.toLowerCase()}%`}`,
        sql`lower(${items.description}) LIKE ${`%${filters.search.toLowerCase()}%`}`
      ) as any);
    }

    if (filters?.lat && filters?.lng && filters?.radius) {
      const radiusInMiles = filters.radius;
      // Haversine formula in SQL
      const distanceSql = sql`(3958.8 * acos(cos(radians(${filters.lat})) * cos(radians(${items.latitude})) * cos(radians(${items.longitude}) - radians(${filters.lng})) + sin(radians(${filters.lat})) * sin(radians(${items.latitude}))))`;
      conditions.push(sql`${distanceSql} <= ${radiusInMiles}`);
    }

    return await db.select().from(items).where(and(...conditions));
  }

  async getItem(id: number): Promise<Item | undefined> {
    const [item] = await db.select().from(items).where(eq(items.id, id));
    return item;
  }

  async createItem(item: InsertItem): Promise<Item> {
    const [newItem] = await db.insert(items).values(item).returning();
    return newItem;
  }

  async updateItem(id: number, updates: UpdateItemRequest): Promise<Item> {
    const [updatedItem] = await db.update(items).set(updates).where(eq(items.id, id)).returning();
    return updatedItem;
  }

  async deleteItem(id: number): Promise<void> {
    await db.delete(items).where(eq(items.id, id));
  }

  async getTrades(userId: number): Promise<Trade[]> {
    return await db.select().from(trades)
      .where(or(eq(trades.requesterId, userId), eq(trades.ownerId, userId)))
      .orderBy(desc(trades.createdAt));
  }

  async getTrade(id: number): Promise<(Trade & { item: Item; messages: Message[] }) | undefined> {
    const [trade] = await db.select().from(trades).where(eq(trades.id, id));
    if (!trade) return undefined;
    const [item] = await db.select().from(items).where(eq(items.id, trade.itemId));
    const tradeMessages = await db.select().from(messages).where(eq(messages.tradeId, id)).orderBy(messages.createdAt);
    return { ...trade, item, messages: tradeMessages };
  }

  async createTrade(trade: InsertTrade): Promise<Trade> {
    const [newTrade] = await db.insert(trades).values(trade).returning();
    return newTrade;
  }

  async updateTradeStatus(id: number, status: string): Promise<Trade> {
    const [updatedTrade] = await db.update(trades).set({ status, updatedAt: new Date() }).where(eq(trades.id, id)).returning();
    return updatedTrade;
  }

  async getMessages(tradeId: number): Promise<Message[]> {
    return await db.select().from(messages).where(eq(messages.tradeId, tradeId)).orderBy(messages.createdAt);
  }

  async createMessage(message: InsertMessage): Promise<Message> {
    const [newMessage] = await db.insert(messages).values(message).returning();
    return newMessage;
  }

  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async createUser(user: InsertUser): Promise<User> {
    const [newUser] = await db.insert(users).values(user).returning();
    return newUser;
  }

  async updateUser(id: number, updates: Partial<InsertUser>): Promise<User> {
    const [updatedUser] = await db.update(users).set(updates).where(eq(users.id, id)).returning();
    return updatedUser;
  }
}

export const storage = new DatabaseStorage();
