
import axios from 'axios';

import { BASE_URL } from './BaseURL';

axios.defaults.baseURL = BASE_URL;

//// functions for making calls to the backend

// function for making an API call - that isn't streaming
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

//// functions for streaming data from the server
//// for use when the server returns a StreamingHttpResponse

// Utility function to format URL correctly
const formatUrl = (baseUrl, endpoint) => {
  if (!baseUrl.endsWith('/')) {
      baseUrl += '/';
  }
  if (endpoint.startsWith('/')) {
      endpoint = endpoint.substring(1);
  }
  return baseUrl + endpoint;
};

// generateStream takes a method, url and data and returns an async generator
export const apiStream = async ({method, url, 
                                  data = null}) => {

    const response = await fetch(
        formatUrl(BASE_URL, url),
        {
            method: method,
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        }
      
    )
    if (response.status !== 200) {
      console.log(response);
      console.log('error');
    } 
    //throw new Error(response.status.toString())

    if (!response.body) {
      console.log('no body')
    }
    //throw new Error('Response body does not exist')
    
    return getIterableStream(response)
};
  

// getIterableStream takes a response and returns an async generator
export async function* getIterableStream(response) {

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
  
    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        break
      }
      const decodedChunk = decoder.decode(value, { stream: true })

      yield decodedChunk
    }
  }
  