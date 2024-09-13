
import axios from 'axios';

import { BASE_URL } from './BaseURL';

axios.defaults.baseURL = BASE_URL;

// function for making an API call
export const apiCall = async ({method, url, 
                                data = null, params = null}) => {
    try {

            let response; 
            if (method === 'get') {
                response = await axios ({
                                          method: method,
                                          url: url,
                                          params: params, 
                                        });
            }
            else if (method === 'post') {
                response = await axios ({
                                          method: method,
                                          url: url,
                                          data: data,
                                        });
            }
            else {
                response = await axios ({
                                          method: method,
                                          url: url,
                                          data: data,
                                        });
            }

            if (response.status === 200) {
                return [true, response.data];
            } 
            else {
                return [false, response.data];
            }
    } 
    catch (error) {
      return [false, 'There was a problem communicating with the server - please try again.'];
    }
};