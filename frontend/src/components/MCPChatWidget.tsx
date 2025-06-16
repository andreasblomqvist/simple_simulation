import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Typography, Spin, Avatar, Badge, FloatButton } from 'antd';
import { MessageOutlined, SendOutlined, RobotOutlined, UserOutlined, CloseOutlined } from '@ant-design/icons';
import { useTheme } from './ThemeContext';

const { Text, Paragraph } = Typography;
const { TextArea } = Input;

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MCPChatWidgetProps {
  simulationData?: any; // Pass current simulation context
}

export const MCPChatWidget: React.FC<MCPChatWidgetProps> = ({ simulationData }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { darkMode } = useTheme();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      setHasUnread(false);
    }
  }, [isOpen]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // TODO: Replace with actual MCP server call
      const response = await fetch('/api/mcp/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          context: simulationData ? {
            hasSimulationData: true,
            totalOffices: Object.keys(simulationData.offices || {}).length,
            periods: simulationData.periods?.length || 0
          } : null
        }),
      });

      const data = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response || 'I apologize, but I encountered an issue processing your request.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (!isOpen) {
        setHasUnread(true);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'I apologize, but I\'m currently unable to process your request. Please try again later.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const chatWidget = (
    <Card
      size="small"
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        width: 380,
        height: 500,
        zIndex: 1000,
        boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
        borderRadius: 16,
        overflow: 'hidden',
        display: isOpen ? 'block' : 'none'
      }}
      bodyStyle={{ padding: 0, height: '100%' }}
      headStyle={{ 
        backgroundColor: darkMode ? '#1f1f1f' : '#fafafa',
        borderBottom: `1px solid ${darkMode ? '#303030' : '#f0f0f0'}`,
        borderRadius: '16px 16px 0 0'
      }}
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <RobotOutlined style={{ color: '#1890ff' }} />
            <Text strong>SimpleSim Assistant</Text>
          </div>
          <Button 
            type="text" 
            size="small" 
            icon={<CloseOutlined />}
            onClick={() => setIsOpen(false)}
          />
        </div>
      }
    >
      <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Messages Area */}
        <div 
                     style={{ 
             flex: 1, 
             padding: '16px', 
             overflowY: 'auto',
             backgroundColor: darkMode ? '#141414' : '#ffffff'
           }}
        >
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', padding: '32px 16px', color: '#8c8c8c' }}>
              <RobotOutlined style={{ fontSize: 32, marginBottom: 16 }} />
              <Paragraph type="secondary">
                Hi! I'm your SimpleSim assistant. Ask me about your simulation results, KPIs, or anything else!
              </Paragraph>
              {simulationData && (
                <Text type="secondary" style={{ fontSize: 12 }}>
                  💡 I can see your current simulation data and help analyze it.
                </Text>
              )}
            </div>
          )}
          
          <List
            dataSource={messages}
            renderItem={(message) => (
              <List.Item style={{ border: 'none', padding: '8px 0' }}>
                <div style={{ 
                  display: 'flex', 
                  gap: 8,
                  width: '100%',
                  flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
                }}>
                  <Avatar 
                    size="small"
                    icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ 
                      backgroundColor: message.type === 'user' ? '#1890ff' : '#52c41a',
                      flexShrink: 0
                    }}
                  />
                  <div style={{ 
                    maxWidth: '80%',
                    textAlign: message.type === 'user' ? 'right' : 'left'
                  }}>
                    <div style={{
                      padding: '8px 12px',
                      borderRadius: 12,
                                             backgroundColor: message.type === 'user' 
                         ? '#1890ff' 
                         : darkMode ? '#262626' : '#f5f5f5',
                      color: message.type === 'user' ? '#fff' : 'inherit',
                      display: 'inline-block'
                    }}>
                      <Text style={{ 
                        color: message.type === 'user' ? '#fff' : 'inherit',
                        fontSize: 14
                      }}>
                        {message.content}
                      </Text>
                    </div>
                    <div style={{ 
                      marginTop: 4, 
                      fontSize: 11, 
                      color: '#8c8c8c' 
                    }}>
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </div>
                </div>
              </List.Item>
            )}
          />
          
          {isLoading && (
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <Spin size="small" />
              <Text type="secondary" style={{ marginLeft: 8 }}>
                Thinking...
              </Text>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ 
          padding: '16px', 
          borderTop: `1px solid ${darkMode ? '#303030' : '#f0f0f0'}`,
          backgroundColor: darkMode ? '#1f1f1f' : '#fafafa'
        }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your simulation results..."
              autoSize={{ minRows: 1, maxRows: 3 }}
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              style={{ alignSelf: 'flex-end' }}
            />
          </div>
        </div>
      </div>
    </Card>
  );

  return (
    <>
      {chatWidget}
      <Badge dot={hasUnread} offset={[-5, 5]}>
        <FloatButton
          icon={<MessageOutlined />}
          onClick={() => setIsOpen(!isOpen)}
          style={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            width: 56,
            height: 56
          }}
          badge={{ dot: hasUnread }}
        />
      </Badge>
    </>
  );
};

export default MCPChatWidget; 