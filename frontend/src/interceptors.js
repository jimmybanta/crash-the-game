import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000/';

axios.defaults.baseURL = BASE_URL;

axios.interceptors.request.use(request => {
    
    // set Content-Type to application/json
    request.headers['Content-Type'] = 'application/json';

    return request;
  },
  (error) => {
    return Promise.reject(error);
  }
);


export { BASE_URL };