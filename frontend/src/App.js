import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Avatar,
  AppBar,
  Toolbar
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const VIVITA_LOGO = 'https://vivita.vn/wp-content/uploads/2021/07/logo-vivita.png';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8001/ask', {
        question: userMessage
      });
      const botResponse = response.data.answer;
      setMessages(prev => [...prev, { role: 'assistant', content: botResponse }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ bgcolor: '#f2f6fc', minHeight: '100vh', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static" color="inherit" elevation={2} sx={{ mb: 0 }}>
        <Toolbar>
          <Avatar src={VIVITA_LOGO} alt="Vivita" sx={{ mr: 2, width: 48, height: 48 }} />
          <Typography variant="h5" color="primary" fontWeight={700}>
            Vivita Assistant
          </Typography>
        </Toolbar>
      </AppBar>
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 'calc(100vh - 64px)', p: 0, m: 0 }}>
        <Paper
          elevation={4}
          sx={{
            borderRadius: 4,
            p: 0,
            width: '100%',
            height: '100%',
            maxWidth: '100vw',
            maxHeight: '100%',
            display: 'flex',
            flexDirection: 'column',
            bgcolor: 'white',
            boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
            flex: 1,
          }}
        >
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: { xs: 1, sm: 3 },
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              bgcolor: '#f8fafc',
              borderTopLeftRadius: 24,
              borderTopRightRadius: 24,
              minHeight: 0,
            }}
          >
            {messages.map((message, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  alignItems: 'flex-end',
                  gap: 1,
                  mb: 0.5
                }}
              >
                <Avatar
                  sx={{ bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main', width: 36, height: 36, alignSelf: 'flex-end' }}
                  src={message.role === 'assistant' ? VIVITA_LOGO : undefined}
                >
                  {message.role === 'user' ? 'U' : 'V'}
                </Avatar>
                <Paper
                  elevation={2}
                  sx={{
                    px: 2,
                    py: 0.5,
                    borderRadius: 3,
                    bgcolor: message.role === 'user' ? 'primary.main' : 'white',
                    color: message.role === 'user' ? 'white' : 'text.primary',
                    maxWidth: { xs: '80vw', sm: 600 },
                    minWidth: 32,
                    width: 'fit-content',
                    minHeight: 'unset',
                    height: 'unset',
                    wordBreak: 'break-word',
                    fontSize: 16,
                    display: 'inline-block',
                    alignSelf: 'flex-end',
                  }}
                >
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </Paper>
              </Box>
            ))}
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <CircularProgress size={28} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
              p: { xs: 1, sm: 2 },
              bgcolor: '#f2f6fc',
              borderBottomLeftRadius: 24,
              borderBottomRightRadius: 24,
              borderTop: '1px solid #e3e8ee',
              display: 'flex',
              gap: 1,
              width: '100%',
            }}
          >
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Nhập câu hỏi của bạn..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              sx={{ bgcolor: 'white', borderRadius: 2 }}
              autoFocus
            />
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !input.trim()}
              sx={{ minWidth: 56, minHeight: 56, borderRadius: 2, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
            >
              <SendIcon fontSize="large" />
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
}

export default App; 