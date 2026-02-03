import type { Express } from "express";
import type { Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";
import { setupAuth, isAuthenticated } from "./auth";

async function getInternalUser(req: any) {
  if (req.isAuthenticated()) {
    return req.user;
  }
  return null;
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  await setupAuth(app);

  app.get(api.items.list.path, async (req, res) => {
    try {
      // The shared route input schema now includes lat, lng, radius as optional strings or numbers depending on your shared/routes update.
      // We updated shared/routes.ts to have them as strings (query params are strings by default in express).
      const filters = api.items.list.input?.safeParse(req.query);

      if (!filters?.success) {
        return res.status(400).json({ message: "Invalid query parameters" });
      }

      const data = filters.data || {};
      const lat = data.lat ? parseFloat(data.lat) : undefined;
      const lng = data.lng ? parseFloat(data.lng) : undefined;
      const radius = data.radius ? parseFloat(data.radius) : undefined;

      const items = await storage.getItems({
        lat,
        lng,
        radius,
        category: data.category,
        search: data.search
      });
      res.json(items);
    } catch (err) {
      res.status(400).json({ message: "Invalid query parameters" });
    }
  });

  app.get(api.items.get.path, async (req, res) => {
    const item = await storage.getItem(String(req.params.id));
    if (!item) {
      return res.status(404).json({ message: "Item not found" });
    }
    res.json(item);
  });

  app.post(api.items.create.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    try {
      const input = api.items.create.input.parse(req.body);
      // Ensure lat/lng are strictly numbers if coming from JSON, although schema says optional number
      // If client sends strings, we might need coercion if schema wasn't updated to Preprocess. 
      // But shared/schema.ts says number. Client sends numbers.
      const item = await storage.createItem({ ...input, ownerId: user.id });
      res.status(201).json(item);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json({
          message: err.errors[0].message,
          field: err.errors[0].path.join('.'),
        });
      }
      res.status(500).json({ message: "Internal server error" });
    }
  });

  app.patch(api.items.update.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    const itemId = String(req.params.id);
    const existingItem = await storage.getItem(itemId);

    if (!existingItem) return res.status(404).json({ message: "Item not found" });
    if (existingItem.ownerId !== user.id) return res.status(403).json({ message: "Forbidden" });

    try {
      const input = api.items.update.input.parse(req.body);
      const updatedItem = await storage.updateItem(itemId, input);
      res.json(updatedItem);
    } catch (err) {
      res.status(400).json({ message: "Validation error" });
    }
  });

  app.delete(api.items.delete.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    const itemId = String(req.params.id);
    const existingItem = await storage.getItem(itemId);

    if (!existingItem) return res.status(404).json({ message: "Item not found" });
    if (existingItem.ownerId !== user.id) return res.status(403).json({ message: "Forbidden" });

    await storage.deleteItem(itemId);
    res.status(204).send();
  });

  app.get(api.trades.list.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    const trades = await storage.getTrades(user.id);
    res.json(trades);
  });

  app.get(api.trades.get.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    const tradeId = String(req.params.id);
    const trade = await storage.getTrade(tradeId);

    if (!trade) return res.status(404).json({ message: "Trade not found" });
    if (trade.requesterId !== user.id && trade.ownerId !== user.id) {
      return res.status(403).json({ message: "Forbidden" });
    }

    res.json(trade);
  });

  app.post(api.trades.create.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    try {
      const input = api.trades.create.input.parse(req.body);
      const item = await storage.getItem(input.itemId);

      if (!item) return res.status(404).json({ message: "Item not found" });
      if (item.ownerId === user.id) return res.status(400).json({ message: "Cannot trade with yourself" });

      const trade = await storage.createTrade({
        itemId: input.itemId,
        requesterId: user.id,
        ownerId: item.ownerId
      });
      res.status(201).json(trade);
    } catch (err) {
      res.status(400).json({ message: "Validation error" });
    }
  });

  app.patch(api.trades.updateStatus.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });

    const tradeId = String(req.params.id);
    const trade = await storage.getTrade(tradeId);

    if (!trade) return res.status(404).json({ message: "Trade not found" });

    if (trade.ownerId !== user.id && trade.requesterId !== user.id) return res.status(403).json({ message: "Forbidden" });

    try {
      const input = api.trades.updateStatus.input.parse(req.body);
      if (input.status === 'accepted' || input.status === 'rejected') {
        if (trade.ownerId !== user.id) return res.status(403).json({ message: "Only owner can accept/reject" });
      }
      const updatedTrade = await storage.updateTradeStatus(tradeId, input.status);
      res.json(updatedTrade);
    } catch (err) {
      res.status(400).json({ message: "Validation error" });
    }
  });

  app.get(api.messages.list.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });
    const tradeId = String(req.params.tradeId);
    const trade = await storage.getTrade(tradeId);
    if (!trade) return res.status(404).json({ message: "Trade not found" });
    if (trade.requesterId !== user.id && trade.ownerId !== user.id) return res.status(403).json({ message: "Forbidden" });
    const messages = await storage.getMessages(tradeId);
    res.json(messages);
  });

  app.post(api.messages.create.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });
    const tradeId = String(req.params.tradeId);
    const trade = await storage.getTrade(tradeId);
    if (!trade) return res.status(404).json({ message: "Trade not found" });
    if (trade.requesterId !== user.id && trade.ownerId !== user.id) return res.status(403).json({ message: "Forbidden" });
    try {
      const input = api.messages.create.input.parse(req.body);
      const message = await storage.createMessage({
        tradeId,
        senderId: user.id,
        content: input.content
      });
      res.status(201).json(message);
    } catch (err) {
      res.status(400).json({ message: "Validation error" });
    }
  });

  app.get(api.users.me.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });
    res.json(user);
  });

  app.patch(api.users.update.path, isAuthenticated, async (req, res) => {
    const user = await getInternalUser(req);
    if (!user) return res.status(401).json({ message: "Unauthorized" });
    try {
      const input = api.users.update.input.parse(req.body);
      const updatedUser = await storage.updateUser(user.id, input);
      res.json(updatedUser);
    } catch (err) {
      res.status(400).json({ message: "Validation error" });
    }
  });

  // API catch-all for 404s
  app.all("/api/:path(.*)", (req, res) => {
    res.status(404).json({ message: "API Endpoint Not Found" });
  });

  await seedDatabase();
  return httpServer;
}

async function seedDatabase() {
  // Check if any users exist
  const existingUser = await storage.getUserByUsername("guitar_hero");

  if (!existingUser) {
    const demoUser1 = await storage.createUser({
      username: "guitar_hero",
      email: "hero@example.com",
      bio: "Love vintage guitars",
      location: "New York, NY",
      googleId: "demo_1"
    });
    const demoUser2 = await storage.createUser({
      username: "camera_fan",
      email: "cam@example.com",
      bio: "Canon shooter",
      location: "Brooklyn, NY",
      googleId: "demo_2"
    });
    await storage.createItem({
      ownerId: demoUser1.id,
      title: "Fender Stratocaster 1998",
      description: "Classic sunburst, good condition.",
      category: "Music",
      images: ["https://images.unsplash.com/photo-1564186763535-ebb21ef5277f"],
      status: "available",
      location: "New York, NY",
      latitude: 40.7128,
      longitude: -74.0060
    });
    await storage.createItem({
      ownerId: demoUser2.id,
      title: "Canon AE-1 Program",
      description: "Vintage film camera.",
      category: "Tech",
      images: ["https://images.unsplash.com/photo-1516035069371-29a1b244cc32"],
      status: "available",
      location: "Brooklyn, NY",
      latitude: 40.6782,
      longitude: -73.9442
    });
  }
}
