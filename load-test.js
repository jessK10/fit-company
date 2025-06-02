import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50, // Virtual users
  duration: '30s', // Total test duration
};

const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsIm5hbWUiOiJBZG1pbiIsInJvbGUiOiJhZG1pbiIsImlzcyI6ImZpdC1hcGkiLCJpYXQiOjE3NDg4NzIzODIsImV4cCI6MTc0ODg3NDE4Mn0.bWMLAXlXlrKVJkWYgEi_8y7Of2423yaZJH7cmQeMdyQ'; 
const url = 'http://localhost:5000/fitness/wod';

export default function () {
  const res = http.get(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
