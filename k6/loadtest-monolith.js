import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50, // Number of concurrent users (virtual users)
  duration: '30s', // How long to run the test
};

export default function () {
  const url = 'http://localhost:8001/wod';

  const payload = JSON.stringify({
    email: 'testuser@example.com',
    exclude_ids: [1, 2, 3, 4, 5] // Adjust as needed
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(url, payload, params);

  check(res, {
    'status was 200': (r) => r.status === 200,
  });

  sleep(1); // Simulate user wait time
}
