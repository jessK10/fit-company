import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 50,
  duration: '30s',
};

export default function () {
  const url = 'http://localhost:5000/fitness/wod';
  const params = {
    headers: {
      Authorization: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsIm5hbWUiOiJBZG1pbiIsInJvbGUiOiJhZG1pbiIsImlzcyI6ImZpdC1hcGkiLCJpYXQiOjE3NDg4ODUyNjQsImV4cCI6MTc0ODg4NzA2NH0.x-4QWOBZ2fiJgQWdXnF70YQg55X7vPdnDbVK1v4YU24',
    },
  };

  const res = http.get(url, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}
