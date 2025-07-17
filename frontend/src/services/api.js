import axios from "axios";

const api = axios.create({
  baseURL: "https://bfmadfdf0l.execute-api.us-east-1.amazonaws.com/Prod/",
});

export default api;
