import { z } from 'zod';
import { insertItemSchema, Item, Trade, Message, User, CreateItemRequest, UpdateItemRequest, CreateTradeRequest, UpdateTradeStatusRequest, CreateMessageRequest } from './schema';

export type { CreateItemRequest, UpdateItemRequest, CreateTradeRequest, UpdateTradeStatusRequest, CreateMessageRequest };

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  items: {
    list: {
      method: 'GET' as const,
      path: '/api/items',
      input: z.object({
        location: z.string().optional(),
        category: z.string().optional(),
        search: z.string().optional(),
        lat: z.string().optional(),
        lng: z.string().optional(),
        radius: z.string().optional(),
      }).optional(),
      responses: {
        200: z.array(z.custom<Item>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/items/:id',
      responses: {
        200: z.custom<Item>(),
        404: errorSchemas.notFound,
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/items',
      input: insertItemSchema,
      responses: {
        201: z.custom<Item>(),
        400: errorSchemas.validation,
        401: errorSchemas.internal,
      },
    },
    update: {
      method: 'PATCH' as const,
      path: '/api/items/:id',
      console: 'input',
      input: insertItemSchema.partial(),
      responses: {
        200: z.custom<Item>(),
        404: errorSchemas.notFound,
        403: errorSchemas.internal,
      },
    },
    delete: {
      method: 'DELETE' as const,
      path: '/api/items/:id',
      responses: {
        204: z.void(),
        403: errorSchemas.internal,
        404: errorSchemas.notFound,
      },
    },
  },
  trades: {
    list: {
      method: 'GET' as const,
      path: '/api/trades',
      responses: {
        200: z.array(z.custom<Trade>()),
      },
    },
    get: {
      method: 'GET' as const,
      path: '/api/trades/:id',
      responses: {
        200: z.custom<Trade & { item: Item, messages: Message[] }>(),
        404: errorSchemas.notFound,
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/trades',
      input: z.object({ itemId: z.string() }),
      responses: {
        201: z.custom<Trade>(),
        400: errorSchemas.validation,
      },
    },
    updateStatus: {
      method: 'PATCH' as const,
      path: '/api/trades/:id/status',
      input: z.object({ status: z.enum(["accepted", "rejected", "completed"]) }),
      responses: {
        200: z.custom<Trade>(),
        403: errorSchemas.internal,
        404: errorSchemas.notFound,
      },
    },
  },
  messages: {
    list: {
      method: 'GET' as const,
      path: '/api/trades/:tradeId/messages',
      responses: {
        200: z.array(z.custom<Message>()),
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/trades/:tradeId/messages',
      input: z.object({ content: z.string() }),
      responses: {
        201: z.custom<Message>(),
        403: errorSchemas.internal,
      },
    },
  },
  users: {
    me: {
      method: 'GET' as const,
      path: '/api/user',
      responses: {
        200: z.custom<User>(),
        401: errorSchemas.internal,
      },
    },
    update: {
      method: 'PATCH' as const,
      path: '/api/user',
      input: z.object({
        bio: z.string().optional(),
        location: z.string().optional(),
        firstName: z.string().optional(),
        lastName: z.string().optional(),
        profileImageUrl: z.string().optional(),
        latitude: z.number().optional(),
        longitude: z.number().optional(),
      }),
      responses: {
        200: z.custom<User>(),
        401: errorSchemas.internal,
      },
    },
  },
};

export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (url.includes(`:${key}`)) {
        url = url.replace(`:${key}`, String(value));
      }
    });
  }
  return url;
}
