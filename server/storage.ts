
import {
  User, Item, Trade, Message,
  InsertUser, InsertItem, InsertTrade, InsertMessage,
  UpdateItemRequest
} from "@shared/schema";
import mongoose, { Schema, Document } from "mongoose";

// --- Mongoose Schemas ---

const UserSchema = new Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String }, // Optional for Google auth users
  email: { type: String },
  googleId: { type: String, unique: true, sparse: true },
  bio: { type: String },
  firstName: { type: String },
  lastName: { type: String },
  profileImageUrl: { type: String },
  location: { type: String },
  latitude: { type: Number },
  longitude: { type: Number },
  createdAt: { type: Date, default: Date.now }
});

const ItemSchema = new Schema({
  ownerId: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true },
  category: { type: String, required: true },
  images: { type: [String], default: [] },
  status: { type: String, enum: ["available", "sold"], default: "available" },
  location: { type: String },
  latitude: { type: Number },
  longitude: { type: Number },
  createdAt: { type: Date, default: Date.now }
});

const TradeSchema = new Schema({
  itemId: { type: String, required: true },
  requesterId: { type: String, required: true },
  ownerId: { type: String, required: true },
  status: { type: String, enum: ["requested", "accepted", "rejected", "completed"], default: "requested" },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

const MessageSchema = new Schema({
  tradeId: { type: String, required: true },
  senderId: { type: String, required: true },
  content: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

// --- Mongoose Models ---

const UserModel = mongoose.model<User & Document>("User", UserSchema);
const ItemModel = mongoose.model<Item & Document>("Item", ItemSchema);
const TradeModel = mongoose.model<Trade & Document>("Trade", TradeSchema);
const MessageModel = mongoose.model<Message & Document>("Message", MessageSchema);

// --- Storage Implementation ---

export interface IStorage {
  getItems(filters?: { lat?: number; lng?: number; radius?: number; category?: string; search?: string }): Promise<Item[]>;
  getItem(id: string): Promise<Item | undefined>;
  createItem(item: InsertItem & { ownerId: string }): Promise<Item>;
  updateItem(id: string, updates: UpdateItemRequest): Promise<Item>;
  deleteItem(id: string): Promise<void>;
  getTrades(userId: string): Promise<Trade[]>;
  getTrade(id: string): Promise<(Trade & { item: Item; messages: Message[] }) | undefined>;
  createTrade(trade: InsertTrade): Promise<Trade>;
  updateTradeStatus(id: string, status: string): Promise<Trade>;
  getMessages(tradeId: string): Promise<Message[]>;
  createMessage(message: InsertMessage & { senderId: string }): Promise<Message>;
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: string, updates: Partial<InsertUser>): Promise<User>;
}

export class MongoStorage implements IStorage {

  async getItems(filters?: { lat?: number; lng?: number; radius?: number; category?: string; search?: string }): Promise<Item[]> {
    const query: any = { status: "available" };

    if (filters?.category) {
      query.category = filters.category;
    }

    if (filters?.search) {
      const regex = new RegExp(filters.search, 'i');
      query.$or = [
        { title: regex },
        { description: regex }
      ];
    }

    if (filters?.lat && filters?.lng && filters?.radius) {
      // Basic implementation using bounding box or simple filtering could be done if $near is not set up on index.
      // But for accuracy with radius in miles, we'd typically use $geoNear (requires index) or manual filtration.
      // For simplicity without setting up 2dsphere indexes explicitly in this migration step (which might fail validation),
      // we can do manual Haversine filtering in Javascript if dataset is small, or use basic math query.

      // Let's rely on manual filtering after fetch for safety and simplicity in this specific context where index setup might be tricky.
      // However, we can try to filter vaguely by lat/lng ranges first.

      // 1 degree latitude ~ 69 miles
      // 1 degree longitude ~ 69 miles * cos(lat)
      const r = filters.radius / 69;
      query.latitude = { $gte: filters.lat - r, $lte: filters.lat + r };
      // longitude logic is more complex due to poles/dateline, skipping pre-filter for longitude to avoid bugs, verifying in code.
    }

    let items = await ItemModel.find(query);

    if (filters?.lat && filters?.lng && filters?.radius) {
      items = items.filter(item => {
        if (!item.latitude || !item.longitude) return false;
        const dist = this.getDistanceFromLatLonInMiles(filters.lat!, filters.lng!, item.latitude, item.longitude);
        return dist <= filters.radius!;
      });
    }

    return items.map(this.mapDoc);
  }

  // Helper for distance
  private getDistanceFromLatLonInMiles(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 3958.8; // Radius of the earth in miles
    const dLat = this.deg2rad(lat2 - lat1);
    const dLon = this.deg2rad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  private deg2rad(deg: number) {
    return deg * (Math.PI / 180);
  }

  async getItem(id: string): Promise<Item | undefined> {
    const item = await ItemModel.findById(id);
    return item ? this.mapDoc(item) : undefined;
  }

  async createItem(item: InsertItem & { ownerId: string }): Promise<Item> {
    const newItem = await ItemModel.create(item);
    return this.mapDoc(newItem);
  }

  async updateItem(id: string, updates: UpdateItemRequest): Promise<Item> {
    const updatedItem = await ItemModel.findByIdAndUpdate(id, updates, { new: true });
    if (!updatedItem) throw new Error("Item not found");
    return this.mapDoc(updatedItem);
  }

  async deleteItem(id: string): Promise<void> {
    await ItemModel.findByIdAndDelete(id);
  }

  async getTrades(userId: string): Promise<Trade[]> {
    const trades = await TradeModel.find({
      $or: [{ requesterId: userId }, { ownerId: userId }]
    }).sort({ createdAt: -1 });
    return trades.map(this.mapDoc);
  }

  async getTrade(id: string): Promise<(Trade & { item: Item; messages: Message[] }) | undefined> {
    const trade = await TradeModel.findById(id);
    if (!trade) return undefined;

    const item = await ItemModel.findById(trade.itemId);
    if (!item) return undefined; // Should theoretically not happen if ref integrity maintained

    const messages = await MessageModel.find({ tradeId: id }).sort({ createdAt: 1 });

    return {
      ...this.mapDoc(trade),
      item: this.mapDoc(item),
      messages: messages.map(this.mapDoc)
    };
  }

  async createTrade(trade: InsertTrade): Promise<Trade> {
    const newTrade = await TradeModel.create(trade);
    return this.mapDoc(newTrade);
  }

  async updateTradeStatus(id: string, status: string): Promise<Trade> {
    const updatedTrade = await TradeModel.findByIdAndUpdate(id, { status, updatedAt: new Date() }, { new: true });
    if (!updatedTrade) throw new Error("Trade not found");
    return this.mapDoc(updatedTrade);
  }

  async getMessages(tradeId: string): Promise<Message[]> {
    const messages = await MessageModel.find({ tradeId }).sort({ createdAt: 1 });
    return messages.map(this.mapDoc);
  }

  async createMessage(message: InsertMessage & { senderId: string }): Promise<Message> {
    const newMessage = await MessageModel.create(message);
    return this.mapDoc(newMessage);
  }

  async getUser(id: string): Promise<User | undefined> {
    if (!mongoose.Types.ObjectId.isValid(id)) return undefined;
    const user = await UserModel.findById(id);
    return user ? this.mapDoc(user) : undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const user = await UserModel.findOne({ username });
    return user ? this.mapDoc(user) : undefined;
  }

  async createUser(user: InsertUser): Promise<User> {
    const newUser = await UserModel.create(user);
    return this.mapDoc(newUser);
  }

  async updateUser(id: string, updates: Partial<InsertUser>): Promise<User> {
    const updatedUser = await UserModel.findByIdAndUpdate(id, updates, { new: true });
    if (!updatedUser) throw new Error("User not found");
    return this.mapDoc(updatedUser);
  }

  // Helper to map Mongoose document to plain object with string ID
  private mapDoc<T extends Document>(doc: T): any {
    const obj = doc.toObject();
    obj.id = obj._id.toString();
    obj._id = obj._id.toString();
    return obj;
  }
}

export const storage = new MongoStorage();
