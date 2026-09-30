import { useEffect, useState } from 'react';
import { apiGet } from '../api/Client';

export const useTelegramMessages = () => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadMessages = async () => {
      try {
        const data = await apiGet('/api/v1/conversations/conversations/?channel=telegram');
        if (!cancelled) {
          setMessages(Array.isArray(data) ? data : data?.items || []);
          setIsConnected(true);
        }
      } catch {
        if (!cancelled) setIsConnected(false);
      }
    };

    loadMessages();
    const interval = window.setInterval(loadMessages, 5000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  return { messages, isConnected };
};