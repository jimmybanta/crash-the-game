
// the base url we should use for all requests
// changes based on the environment

const ENV = 'DEV';


let BASE_URL = '';

if (ENV === 'DEV') {
    BASE_URL = 'http://127.0.0.1:8000/';
}
else if (ENV === 'STAG') {
    BASE_URL = 'https://api-stag.crashthegame.com/';
}
else if (ENV === 'PROD') {
    BASE_URL = 'https://api.crashthegame.com/';
}


export { BASE_URL };