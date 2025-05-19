import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  AppBar,
  Toolbar,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import { Send as SendIcon, Logout as LogoutIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef(null);
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchMessages = async () => {
    try {
      const response = await axios.get('http://localhost:8000/messages/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      await axios.post(
        'http://localhost:8000/messages/',
        {
          content: newMessage,
          sender: user.username,
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setNewMessage('');
      fetchMessages();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Enterprise Chat
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
        <Paper
          elevation={3}
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
            {messages.map((message, index) => (
              <React.Fragment key={index}>
                <ListItem
                  alignItems="flex-start"
                  sx={{
                    flexDirection: message.sender === user.username ? 'row-reverse' : 'row',
                  }}
                >
                  <ListItemText
                    primary={
                      <Typography
                        component="span"
                        variant="body1"
                        sx={{
                          display: 'inline',
                          backgroundColor: message.sender === user.username ? '#e3f2fd' : '#f5f5f5',
                          padding: '8px 12px',
                          borderRadius: '12px',
                          maxWidth: '70%',
                        }}
                      >
                        {message.content}
                      </Typography>
                    }
                    secondary={
                      <Typography
                        component="span"
                        variant="caption"
                        sx={{ display: 'block', mt: 0.5 }}
                      >
                        {message.sender} • {format(new Date(message.timestamp), 'MMM d, h:mm a')}
                      </Typography>
                    }
                  />
                </ListItem>
                {index < messages.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            ))}
            <div ref={messagesEndRef} />
          </List>

          <Box
            component="form"
            onSubmit={handleSend}
            sx={{
              p: 2,
              backgroundColor: 'background.paper',
              borderTop: 1,
              borderColor: 'divider',
            }}
          >
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type a message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                size="small"
              />
              <Button
                type="submit"
                variant="contained"
                endIcon={<SendIcon />}
                disabled={!newMessage.trim()}
              >
                Send
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default Chat; 