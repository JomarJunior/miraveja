import memberFetchSchema from "./schemas/miraveja.member.fetch.v1.json";

export const EventRegistry = {
    "miraveja.member.fetch.v1": memberFetchSchema
};

export type EventTopic = keyof typeof EventRegistry;