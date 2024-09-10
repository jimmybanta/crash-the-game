import axios from 'axios';

import { BASE_URL } from './BaseUrl';
  
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
