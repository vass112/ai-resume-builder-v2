const fs = require('fs');
const env = {
  GEMINI_API_KEY: process.env.GEMINI_API_KEY || "",
  RAZORPAY_KEY: process.env.RAZORPAY_KEY || "",
  FIREBASE_CONFIG: {
    apiKey: process.env.FIREBASE_API_KEY || "",
    authDomain: process.env.FIREBASE_AUTH_DOMAIN || "",
    projectId: process.env.FIREBASE_PROJECT_ID || "",
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET || "",
    messagingSenderId: process.env.FIREBASE_SENDER_ID || "",
    appId: process.env.FIREBASE_APP_ID || ""
  }
};
fs.writeFileSync('env.js', `window._env = ${JSON.stringify(env, null, 2)};`);
