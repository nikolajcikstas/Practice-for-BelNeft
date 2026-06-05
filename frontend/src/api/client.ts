import axios from "axios";

const client = axios.create({
  baseURL: "/api",
  headers: {
    "X-User-Id": "1",
  },
});

export default client;
