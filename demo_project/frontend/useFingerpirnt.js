import { useEffect, useState } from 'react';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

const useFingerprint = () => {
  const [fingerprint, setFingerprint] = useState(null);

  useEffect(() => {
    const generateFingerprint = async () => {
      const fp = await FingerprintJS.load();
      const result = await fp.get();
      setFingerprint(result.visitorId); 
    };

    generateFingerprint();
  }, []);

  return fingerprint;
};

const fetchIP = async () => {
  const response = await fetch('https://api.ipify.org?format=json');
  const data = await response.json();
  return data.ip;
};

export { useFingerprint, fetchIP };
