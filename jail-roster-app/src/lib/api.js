// src/lib/api.js
import axios from "axios";

// Fetch helper for JSON GET/POST
export async function apiFetchJson(url, options = {}) {
  const res = await fetch(url, {
    credentials: "include", // send cookies (session)
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const message = data?.error || data?.message || res.statusText;
    throw new Error(message);
  }

  return data;
}

// Axios instance for file uploads, etc.
export const apiAxios = axios.create({
  baseURL: "/api",
  withCredentials: true, // send cookies
});
