import React, { useState, useEffect } from 'react';

const themes = {
  light: {
    bg: "#F3F1EA",
    text: "#14201A",
    muted: "#5B6B62",
    card: "#FFFFFF",
    accent: "#2F6F4E",
    accentText: "#FFFFFF",
    border: "rgba(20,32,26,0.10)",
    bubbleAi: "#EEF2ED",
    navBg: "rgba(243,241,234,0.82)",
  },
  dark: {
    bg: "#101713",
    text: "#F2F0E8",
    muted: "#93A39A",
    card: "#182019",
    accent: "#7FD9A4",
    accentText: "#0E1512",
    border: "rgba(242,240,232,0.10)",
    bubbleAi: "#1E2A22",
    navBg: "rgba(16,23,19,0.82)",
  },
};
