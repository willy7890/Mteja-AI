import { useEffect, useState } from 'react';

// Custom Hook kwa ajili ya kupokea jumbe za Telegram
export const useTelegramMessages = (webSocketUrl) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Kuanzisha muunganisho wa WebSocket
    const socket = new WebSocket(webSocketUrl);

    socket.onopen = () => {
      console.log('⚡ Muunganisho wa Telegram WebSocket umefanikiwa!');
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      // Kuongeza ujumbe mpya kwenye orodha ya jumbe
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    };

    socket.onclose = () => {
      console.log('🔌 Muunganisho wa WebSocket umefungwa.');
      setIsConnected(false);
    };

    // Kusafisha muunganisho pale component inapofungwa
    return () => {
      socket.close();
    };
  }, [webSocketUrl]);

  return { messages, isConnected };
};